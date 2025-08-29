"""
CLI 명령어 도구
"""

import asyncio
import click
import logging
from datetime import datetime
from app.services.cisa_sync import cisa_sync_service
from app.core.database import init_database, reset_database
from app.models.base import SessionLocal
from app.models.vulnerability import Vulnerability, Vendor, Product, DataSyncStatus

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """CISA KEV 관리 CLI 도구"""
    pass

@cli.command()
def init_db():
    """데이터베이스 초기화"""
    click.echo("🔧 데이터베이스 초기화 중...")
    try:
        init_database()
        click.echo("✅ 데이터베이스 초기화 완료")
    except Exception as e:
        click.echo(f"❌ 초기화 실패: {e}")

@cli.command()
def reset_db():
    """데이터베이스 리셋"""
    if not click.confirm('모든 데이터가 삭제됩니다. 계속하시겠습니까?'):
        click.echo("❌ 취소되었습니다")
        return
        
    click.echo("🔄 데이터베이스 리셋 중...")
    try:
        reset_database()
        click.echo("✅ 데이터베이스 리셋 완료")
    except Exception as e:
        click.echo(f"❌ 리셋 실패: {e}")

@cli.command()
def sync():
    """CISA KEV 데이터 동기화"""
    click.echo("🔄 CISA KEV 데이터 동기화 시작...")
    
    async def run_sync():
        result = await cisa_sync_service.sync_vulnerabilities()
        return result
    
    try:
        result = asyncio.run(run_sync())
        
        if result['success']:
            stats = result['stats']
            click.echo("✅ 동기화 완료!")
            click.echo(f"📊 통계:")
            click.echo(f"  - 전체: {stats['total']}개")
            click.echo(f"  - 새로 추가: {stats['created']}개")
            click.echo(f"  - 업데이트: {stats['updated']}개")
            click.echo(f"  - 오류: {stats['errors']}개")
            click.echo(f"  - 새 벤더: {stats['vendors_created']}개")
            click.echo(f"  - 새 제품: {stats['products_created']}개")
            
            if 'catalog_version' in result:
                click.echo(f"📅 카탈로그 버전: {result['catalog_version']}")
        else:
            click.echo(f"❌ 동기화 실패: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        click.echo(f"❌ 동기화 중 오류: {e}")

@cli.command()
def status():
    """현재 상태 확인"""
    db = SessionLocal()
    try:
        # 기본 통계
        vuln_count = db.query(Vulnerability).count()
        vendor_count = db.query(Vendor).count()
        product_count = db.query(Product).count()
        
        click.echo("📊 현재 데이터베이스 상태:")
        click.echo(f"  - 취약점: {vuln_count:,}개")
        click.echo(f"  - 벤더: {vendor_count:,}개")
        click.echo(f"  - 제품: {product_count:,}개")
        
        # 랜섬웨어 관련 통계
        ransomware_count = db.query(Vulnerability).filter(
            Vulnerability.known_ransomware_use == True
        ).count()
        click.echo(f"  - 랜섬웨어 관련: {ransomware_count:,}개")
        
        # 동기화 상태
        sync_status = db.query(DataSyncStatus).filter(
            DataSyncStatus.source == "cisa_kev"
        ).first()
        
        if sync_status:
            click.echo(f"\n🔄 마지막 동기화:")
            click.echo(f"  - 상태: {sync_status.status}")
            if sync_status.last_sync_at:
                click.echo(f"  - 시간: {sync_status.last_sync_at}")
            if sync_status.last_successful_sync_at:
                click.echo(f"  - 마지막 성공: {sync_status.last_successful_sync_at}")
            if sync_status.error_message:
                click.echo(f"  - 오류: {sync_status.error_message}")
        
        # 최근 추가된 취약점 (상위 5개)
        recent_vulns = db.query(Vulnerability).order_by(
            Vulnerability.date_added.desc()
        ).limit(5).all()
        
        if recent_vulns:
            click.echo(f"\n📋 최근 취약점 (상위 5개):")
            for vuln in recent_vulns:
                click.echo(f"  - {vuln.cve_id}: {vuln.vulnerability_name[:50]}...")
                
    except Exception as e:
        click.echo(f"❌ 상태 확인 실패: {e}")
    finally:
        db.close()

@cli.command()
@click.argument('cve_id')
def detail(cve_id):
    """특정 CVE 상세 정보"""
    db = SessionLocal()
    try:
        vuln = db.query(Vulnerability).filter(
            Vulnerability.cve_id == cve_id.upper()
        ).first()
        
        if not vuln:
            click.echo(f"❌ {cve_id} 취약점을 찾을 수 없습니다")
            return
            
        click.echo(f"🔍 {vuln.cve_id} 상세 정보:")
        click.echo(f"  취약점명: {vuln.vulnerability_name}")
        click.echo(f"  벤더: {vuln.vendor.name}")
        click.echo(f"  제품: {vuln.product.name}")
        click.echo(f"  추가일: {vuln.date_added}")
        click.echo(f"  랜섬웨어: {'예' if vuln.known_ransomware_use else '아니오'}")
        if vuln.due_date:
            click.echo(f"  마감일: {vuln.due_date}")
        click.echo(f"  설명: {vuln.short_description}")
        click.echo(f"  조치: {vuln.required_action}")
        if vuln.notes:
            click.echo(f"  노트: {vuln.notes}")
            
    except Exception as e:
        click.echo(f"❌ 조회 실패: {e}")
    finally:
        db.close()

@cli.command()
@click.option('--vendor', help='벤더명으로 필터링')
@click.option('--product', help='제품명으로 필터링')
@click.option('--ransomware', is_flag=True, help='랜섬웨어 관련만')
@click.option('--limit', default=10, help='결과 개수 제한')
def search(vendor, product, ransomware, limit):
    """취약점 검색"""
    db = SessionLocal()
    try:
        query = db.query(Vulnerability)
        
        if vendor:
            query = query.join(Vendor).filter(
                Vendor.name.ilike(f'%{vendor}%')
            )
        
        if product:
            query = query.join(Product).filter(
                Product.name.ilike(f'%{product}%')
            )
            
        if ransomware:
            query = query.filter(Vulnerability.known_ransomware_use == True)
        
        vulnerabilities = query.order_by(
            Vulnerability.date_added.desc()
        ).limit(limit).all()
        
        if not vulnerabilities:
            click.echo("❌ 검색 결과가 없습니다")
            return
            
        click.echo(f"🔍 검색 결과 ({len(vulnerabilities)}개):")
        for vuln in vulnerabilities:
            ransomware_flag = " 🦠" if vuln.known_ransomware_use else ""
            click.echo(f"  {vuln.cve_id}: {vuln.vulnerability_name[:50]}...{ransomware_flag}")
            click.echo(f"    벤더/제품: {vuln.vendor.name} / {vuln.product.name}")
            
    except Exception as e:
        click.echo(f"❌ 검색 실패: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    cli()