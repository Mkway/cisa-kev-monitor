"""
CISA KEV 데이터 동기화 서비스
"""

import httpx
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from dateutil.parser import parse as parse_date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.models.base import SessionLocal
from app.models.vulnerability import (
    Vendor, Product, Vulnerability, 
    VulnerabilityHistory, DataSyncStatus
)
from app.schemas.vulnerability import CISAKEVResponse, CISAVulnerabilityRaw

logger = logging.getLogger(__name__)

class CISAKEVSyncService:
    """CISA KEV 데이터 동기화 서비스"""
    
    def __init__(self):
        self.client = httpx.Client(timeout=30.0)
        self.source = "cisa_kev"
        
    def __del__(self):
        """클라이언트 정리"""
        if hasattr(self, 'client'):
            self.client.close()

    async def fetch_kev_data(self) -> Optional[CISAKEVResponse]:
        """CISA KEV 데이터 fetch"""
        try:
            logger.info("CISA KEV 데이터 요청 중...")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(settings.CISA_KEV_URL)
                response.raise_for_status()
                
                logger.info(f"데이터 수신 완료: {len(response.content)} bytes")
                
                # JSON 파싱 및 검증
                json_data = response.json()
                kev_data = CISAKEVResponse(**json_data)
                
                logger.info(f"파싱 완료: {kev_data.count}개 취약점")
                return kev_data
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP 요청 실패: {e}")
            return None
        except Exception as e:
            logger.error(f"데이터 fetch 중 오류: {e}")
            return None

    def normalize_vendor_name(self, vendor_name: str) -> str:
        """벤더명 정규화"""
        if not vendor_name:
            return "Unknown"
            
        # 소문자 변환 및 공백 정리
        normalized = vendor_name.lower().strip()
        
        # 일반적인 정규화 패턴
        replacements = {
            " inc.": "",
            " inc": "",
            " corporation": "",
            " corp.": "",
            " corp": "",
            " ltd.": "",
            " ltd": "",
            " llc": "",
            " co.": "",
            " company": "",
            ".": "",
            ",": ""
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
            
        return normalized.strip()

    def normalize_product_name(self, product_name: str) -> str:
        """제품명 정규화"""
        if not product_name:
            return "Unknown"
            
        return product_name.lower().strip()

    def get_or_create_vendor(self, db: Session, vendor_name: str) -> Vendor:
        """벤더 조회 또는 생성"""
        normalized_name = self.normalize_vendor_name(vendor_name)
        
        # 기존 벤더 조회
        vendor = db.query(Vendor).filter(
            Vendor.normalized_name == normalized_name
        ).first()
        
        if not vendor:
            # 새 벤더 생성
            vendor = Vendor(
                name=vendor_name.strip(),
                normalized_name=normalized_name
            )
            db.add(vendor)
            db.flush()  # ID 생성을 위해 flush
            logger.debug(f"새 벤더 생성: {vendor.name}")
            
        return vendor

    def get_or_create_product(self, db: Session, vendor: Vendor, product_name: str) -> Product:
        """제품 조회 또는 생성"""
        normalized_name = self.normalize_product_name(product_name)
        
        # 기존 제품 조회
        product = db.query(Product).filter(
            Product.vendor_id == vendor.id,
            Product.normalized_name == normalized_name
        ).first()
        
        if not product:
            # 새 제품 생성
            product = Product(
                name=product_name.strip(),
                normalized_name=normalized_name,
                vendor_id=vendor.id
            )
            db.add(product)
            db.flush()  # ID 생성을 위해 flush
            logger.debug(f"새 제품 생성: {vendor.name} - {product.name}")
            
        return product

    def parse_cisa_date(self, date_str: str) -> Optional[datetime]:
        """CISA 날짜 문자열 파싱"""
        if not date_str or date_str.lower() in ('', 'n/a', 'unknown'):
            return None
            
        try:
            # CISA는 YYYY-MM-DD 형식 사용
            return parse_date(date_str).replace(tzinfo=timezone.utc)
        except Exception as e:
            logger.warning(f"날짜 파싱 실패: {date_str} - {e}")
            return None

    def parse_boolean_field(self, value: str) -> bool:
        """CISA 불린 필드 파싱"""
        if not value:
            return False
        return value.lower() in ('yes', 'true', '1', 'known')

    def create_or_update_vulnerability(
        self, 
        db: Session, 
        vendor: Vendor, 
        product: Product, 
        vuln_data: CISAVulnerabilityRaw
    ) -> Tuple[Vulnerability, bool]:
        """취약점 생성 또는 업데이트"""
        
        # 기존 취약점 조회
        existing_vuln = db.query(Vulnerability).filter(
            Vulnerability.cve_id == vuln_data.cveID
        ).first()
        
        # 날짜 파싱
        date_added = self.parse_cisa_date(vuln_data.dateAdded)
        due_date = self.parse_cisa_date(vuln_data.dueDate)
        
        # 랜섬웨어 사용 여부
        ransomware_use = self.parse_boolean_field(vuln_data.knownRansomwareCampaignUse)
        
        if existing_vuln:
            # 기존 데이터와 비교하여 변경사항 확인
            changes = {}
            old_values = {}
            
            if existing_vuln.vulnerability_name != vuln_data.vulnerabilityName:
                old_values['vulnerability_name'] = existing_vuln.vulnerability_name
                existing_vuln.vulnerability_name = vuln_data.vulnerabilityName
                changes['vulnerability_name'] = vuln_data.vulnerabilityName
                
            if existing_vuln.short_description != vuln_data.shortDescription:
                old_values['short_description'] = existing_vuln.short_description
                existing_vuln.short_description = vuln_data.shortDescription
                changes['short_description'] = vuln_data.shortDescription
                
            if existing_vuln.required_action != vuln_data.requiredAction:
                old_values['required_action'] = existing_vuln.required_action
                existing_vuln.required_action = vuln_data.requiredAction
                changes['required_action'] = vuln_data.requiredAction
                
            if existing_vuln.known_ransomware_use != ransomware_use:
                old_values['known_ransomware_use'] = existing_vuln.known_ransomware_use
                existing_vuln.known_ransomware_use = ransomware_use
                changes['known_ransomware_use'] = ransomware_use
                
            if existing_vuln.due_date != due_date:
                old_values['due_date'] = existing_vuln.due_date.isoformat() if existing_vuln.due_date else None
                existing_vuln.due_date = due_date
                changes['due_date'] = due_date.isoformat() if due_date else None
                
            if existing_vuln.notes != vuln_data.notes:
                old_values['notes'] = existing_vuln.notes
                existing_vuln.notes = vuln_data.notes
                changes['notes'] = vuln_data.notes
            
            # 변경사항이 있으면 히스토리 기록
            if changes:
                existing_vuln.updated_at = datetime.utcnow()
                existing_vuln.last_checked_at = datetime.utcnow()
                
                # 히스토리 기록
                history = VulnerabilityHistory(
                    vulnerability_id=existing_vuln.id,
                    action='updated',
                    changed_fields=list(changes.keys()),
                    old_values=old_values,
                    new_values=changes,
                    source='cisa_sync',
                    notes=f"CISA KEV 동기화로 인한 업데이트"
                )
                db.add(history)
                
                logger.info(f"취약점 업데이트: {vuln_data.cveID} - {len(changes)}개 필드 변경")
                return existing_vuln, False
            else:
                # 변경사항 없음, 마지막 확인 시간만 업데이트
                existing_vuln.last_checked_at = datetime.utcnow()
                return existing_vuln, False
                
        else:
            # 새 취약점 생성
            new_vuln = Vulnerability(
                cve_id=vuln_data.cveID,
                vendor_id=vendor.id,
                product_id=product.id,
                vulnerability_name=vuln_data.vulnerabilityName,
                date_added=date_added or datetime.utcnow(),
                short_description=vuln_data.shortDescription,
                required_action=vuln_data.requiredAction,
                due_date=due_date,
                known_ransomware_use=ransomware_use,
                notes=vuln_data.notes,
                last_checked_at=datetime.utcnow()
            )
            
            db.add(new_vuln)
            db.flush()  # ID 생성
            
            # 히스토리 기록
            history = VulnerabilityHistory(
                vulnerability_id=new_vuln.id,
                action='created',
                source='cisa_sync',
                notes=f"CISA KEV에서 새로 추가된 취약점"
            )
            db.add(history)
            
            logger.info(f"새 취약점 생성: {vuln_data.cveID}")
            return new_vuln, True

    def update_sync_status(
        self, 
        db: Session, 
        status: str, 
        total_records: int = 0,
        processed_records: int = 0,
        error_message: str = None
    ):
        """동기화 상태 업데이트"""
        sync_status = db.query(DataSyncStatus).filter(
            DataSyncStatus.source == self.source
        ).first()
        
        if not sync_status:
            sync_status = DataSyncStatus(source=self.source)
            db.add(sync_status)
        
        now = datetime.utcnow()
        sync_status.status = status
        sync_status.total_records = total_records
        sync_status.processed_records = processed_records
        sync_status.error_message = error_message
        sync_status.last_sync_at = now
        sync_status.updated_at = now
        
        if status == 'success':
            sync_status.last_successful_sync_at = now
            
        db.commit()

    async def sync_vulnerabilities(self) -> Dict[str, any]:
        """전체 취약점 동기화 실행"""
        db = SessionLocal()
        
        try:
            logger.info("CISA KEV 동기화 시작")
            
            # 동기화 상태를 진행 중으로 변경
            self.update_sync_status(db, 'in_progress')
            
            # CISA 데이터 가져오기
            kev_data = await self.fetch_kev_data()
            if not kev_data:
                self.update_sync_status(
                    db, 'error', 
                    error_message="CISA KEV 데이터를 가져올 수 없습니다"
                )
                return {
                    'success': False,
                    'error': 'CISA KEV 데이터를 가져올 수 없습니다'
                }
            
            # 통계 초기화
            stats = {
                'total': len(kev_data.vulnerabilities),
                'created': 0,
                'updated': 0,
                'errors': 0,
                'vendors_created': 0,
                'products_created': 0
            }
            
            initial_vendor_count = db.query(Vendor).count()
            initial_product_count = db.query(Product).count()
            
            # 각 취약점 처리
            for i, vuln_data in enumerate(kev_data.vulnerabilities):
                try:
                    # 벤더 처리
                    vendor = self.get_or_create_vendor(db, vuln_data.vendorProject)
                    
                    # 제품 처리
                    product = self.get_or_create_product(db, vendor, vuln_data.product)
                    
                    # 취약점 처리
                    vulnerability, is_new = self.create_or_update_vulnerability(
                        db, vendor, product, vuln_data
                    )
                    
                    if is_new:
                        stats['created'] += 1
                    else:
                        stats['updated'] += 1
                    
                    # 진행 상황 업데이트 (100개마다)
                    if (i + 1) % 100 == 0:
                        self.update_sync_status(
                            db, 'in_progress', 
                            stats['total'], i + 1
                        )
                        db.commit()  # 중간 커밋
                        logger.info(f"진행 상황: {i + 1}/{stats['total']} 처리 완료")
                        
                except Exception as e:
                    logger.error(f"취약점 처리 중 오류 ({vuln_data.cveID}): {e}")
                    stats['errors'] += 1
                    
            # 최종 통계 계산
            final_vendor_count = db.query(Vendor).count()
            final_product_count = db.query(Product).count()
            stats['vendors_created'] = final_vendor_count - initial_vendor_count
            stats['products_created'] = final_product_count - initial_product_count
            
            # 최종 커밋
            db.commit()
            
            # 성공 상태로 업데이트
            self.update_sync_status(
                db, 'success', 
                stats['total'], stats['total'] - stats['errors']
            )
            
            logger.info(f"CISA KEV 동기화 완료: {stats}")
            
            return {
                'success': True,
                'stats': stats,
                'catalog_version': kev_data.catalogVersion,
                'date_released': kev_data.dateReleased
            }
            
        except Exception as e:
            logger.error(f"동기화 중 치명적 오류: {e}")
            db.rollback()
            self.update_sync_status(
                db, 'error',
                error_message=str(e)
            )
            
            return {
                'success': False,
                'error': str(e)
            }
            
        finally:
            db.close()

# 전역 서비스 인스턴스
cisa_sync_service = CISAKEVSyncService()