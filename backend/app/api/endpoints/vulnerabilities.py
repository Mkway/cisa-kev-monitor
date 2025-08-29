"""
취약점 관련 API 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.models.base import get_db
from app.models.vulnerability import (
    Vulnerability, Vendor, Product, VulnerabilityHistory, DataSyncStatus
)
from app.schemas.vulnerability import (
    VulnerabilityResponse, VulnerabilityListResponse, 
    VulnerabilitySearchRequest, VulnerabilityStats,
    VulnerabilityHistoryResponse, DataSyncStatusResponse
)

router = APIRouter()

@router.get("/", response_model=VulnerabilityListResponse)
async def get_vulnerabilities(
    page: int = Query(1, ge=1, description="페이지 번호"),
    per_page: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    vendor: Optional[str] = Query(None, description="벤더명 필터"),
    product: Optional[str] = Query(None, description="제품명 필터"),
    ransomware_only: bool = Query(False, description="랜섬웨어 관련만"),
    date_from: Optional[datetime] = Query(None, description="시작 날짜"),
    date_to: Optional[datetime] = Query(None, description="종료 날짜"),
    sort_by: str = Query("date_added", description="정렬 기준"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="정렬 순서"),
    db: Session = Depends(get_db)
):
    """취약점 목록 조회"""
    
    # 기본 쿼리 설정
    query = db.query(Vulnerability).options(
        joinedload(Vulnerability.vendor),
        joinedload(Vulnerability.product)
    )
    
    # 필터 적용
    if vendor:
        query = query.join(Vendor).filter(
            Vendor.name.ilike(f'%{vendor}%')
        )
    
    if product:
        query = query.join(Product).filter(
            Product.name.ilike(f'%{product}%')
        )
    
    if ransomware_only:
        query = query.filter(Vulnerability.known_ransomware_use == True)
    
    if date_from:
        query = query.filter(Vulnerability.date_added >= date_from)
    
    if date_to:
        query = query.filter(Vulnerability.date_added <= date_to)
    
    # 정렬 적용
    if sort_by == "date_added":
        sort_column = Vulnerability.date_added
    elif sort_by == "cve_id":
        sort_column = Vulnerability.cve_id
    elif sort_by == "vendor":
        query = query.join(Vendor)
        sort_column = Vendor.name
    else:
        sort_column = Vulnerability.date_added
    
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # 전체 개수 조회
    total = query.count()
    
    # 페이지네이션 적용
    offset = (page - 1) * per_page
    vulnerabilities = query.offset(offset).limit(per_page).all()
    
    # 전체 페이지 수 계산
    pages = (total + per_page - 1) // per_page
    
    return VulnerabilityListResponse(
        items=vulnerabilities,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )

@router.get("/{cve_id}", response_model=VulnerabilityResponse)
async def get_vulnerability_by_cve(
    cve_id: str = Path(..., description="CVE ID"),
    db: Session = Depends(get_db)
):
    """특정 CVE 상세 정보 조회"""
    
    vulnerability = db.query(Vulnerability).options(
        joinedload(Vulnerability.vendor),
        joinedload(Vulnerability.product)
    ).filter(
        Vulnerability.cve_id == cve_id.upper()
    ).first()
    
    if not vulnerability:
        raise HTTPException(
            status_code=404, 
            detail=f"CVE {cve_id} not found"
        )
    
    return vulnerability

@router.get("/{cve_id}/history", response_model=List[VulnerabilityHistoryResponse])
async def get_vulnerability_history(
    cve_id: str = Path(..., description="CVE ID"),
    db: Session = Depends(get_db)
):
    """취약점 변경 이력 조회"""
    
    # 취약점 존재 확인
    vulnerability = db.query(Vulnerability).filter(
        Vulnerability.cve_id == cve_id.upper()
    ).first()
    
    if not vulnerability:
        raise HTTPException(
            status_code=404, 
            detail=f"CVE {cve_id} not found"
        )
    
    # 히스토리 조회
    history = db.query(VulnerabilityHistory).filter(
        VulnerabilityHistory.vulnerability_id == vulnerability.id
    ).order_by(desc(VulnerabilityHistory.timestamp)).all()
    
    return history

@router.post("/search", response_model=VulnerabilityListResponse)
async def search_vulnerabilities(
    search_request: VulnerabilitySearchRequest,
    db: Session = Depends(get_db)
):
    """고급 취약점 검색"""
    
    query = db.query(Vulnerability).options(
        joinedload(Vulnerability.vendor),
        joinedload(Vulnerability.product)
    )
    
    # 텍스트 검색
    if search_request.query:
        search_term = f'%{search_request.query}%'
        query = query.filter(
            or_(
                Vulnerability.cve_id.ilike(search_term),
                Vulnerability.vulnerability_name.ilike(search_term),
                Vulnerability.short_description.ilike(search_term)
            )
        )
    
    # 벤더 필터
    if search_request.vendor:
        query = query.join(Vendor).filter(
            Vendor.name.ilike(f'%{search_request.vendor}%')
        )
    
    # 제품 필터
    if search_request.product:
        query = query.join(Product).filter(
            Product.name.ilike(f'%{search_request.product}%')
        )
    
    # CVE ID 필터
    if search_request.cve_id:
        query = query.filter(
            Vulnerability.cve_id.ilike(f'%{search_request.cve_id}%')
        )
    
    # 랜섬웨어 필터
    if search_request.ransomware_only:
        query = query.filter(Vulnerability.known_ransomware_use == True)
    
    # 날짜 범위 필터
    if search_request.date_from:
        query = query.filter(Vulnerability.date_added >= search_request.date_from)
    
    if search_request.date_to:
        query = query.filter(Vulnerability.date_added <= search_request.date_to)
    
    # 최신순 정렬
    query = query.order_by(desc(Vulnerability.date_added))
    
    # 전체 개수 조회
    total = query.count()
    
    # 페이지네이션 적용
    offset = (search_request.page - 1) * search_request.per_page
    vulnerabilities = query.offset(offset).limit(search_request.per_page).all()
    
    # 전체 페이지 수 계산
    pages = (total + search_request.per_page - 1) // search_request.per_page
    
    return VulnerabilityListResponse(
        items=vulnerabilities,
        total=total,
        page=search_request.page,
        per_page=search_request.per_page,
        pages=pages
    )

@router.get("/stats/overview", response_model=VulnerabilityStats)
async def get_vulnerability_stats(db: Session = Depends(get_db)):
    """취약점 통계 정보"""
    
    # 기본 통계
    total_vulnerabilities = db.query(Vulnerability).count()
    total_vendors = db.query(Vendor).count()
    total_products = db.query(Product).count()
    ransomware_vulnerabilities = db.query(Vulnerability).filter(
        Vulnerability.known_ransomware_use == True
    ).count()
    
    # 최근 30일 추가된 취약점
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_additions = db.query(Vulnerability).filter(
        Vulnerability.date_added >= thirty_days_ago
    ).count()
    
    # 벤더별 통계 (상위 10개)
    vendor_stats = db.query(
        Vendor.name,
        func.count(Vulnerability.id).label('count')
    ).join(Vulnerability).group_by(Vendor.name).order_by(
        desc(func.count(Vulnerability.id))
    ).limit(10).all()
    
    by_vendor = [
        {"name": stat.name, "count": stat.count} 
        for stat in vendor_stats
    ]
    
    # 월별 통계 (최근 12개월)
    twelve_months_ago = datetime.utcnow() - timedelta(days=365)
    monthly_stats = db.query(
        func.date_trunc('month', Vulnerability.date_added).label('month'),
        func.count(Vulnerability.id).label('count')
    ).filter(
        Vulnerability.date_added >= twelve_months_ago
    ).group_by(
        func.date_trunc('month', Vulnerability.date_added)
    ).order_by('month').all()
    
    by_month = [
        {
            "month": stat.month.strftime('%Y-%m') if stat.month else 'Unknown',
            "count": stat.count
        }
        for stat in monthly_stats
    ]
    
    return VulnerabilityStats(
        total_vulnerabilities=total_vulnerabilities,
        total_vendors=total_vendors,
        total_products=total_products,
        ransomware_vulnerabilities=ransomware_vulnerabilities,
        recent_additions=recent_additions,
        by_vendor=by_vendor,
        by_month=by_month
    )

@router.get("/vendors/", response_model=List[Dict[str, Any]])
async def get_vendors(
    search: Optional[str] = Query(None, description="벤더명 검색"),
    limit: int = Query(50, ge=1, le=200, description="결과 개수 제한"),
    db: Session = Depends(get_db)
):
    """벤더 목록 조회"""
    
    query = db.query(
        Vendor.name,
        func.count(Vulnerability.id).label('vulnerability_count')
    ).join(Vulnerability).group_by(Vendor.name)
    
    if search:
        query = query.filter(Vendor.name.ilike(f'%{search}%'))
    
    vendors = query.order_by(
        desc(func.count(Vulnerability.id))
    ).limit(limit).all()
    
    return [
        {
            "name": vendor.name,
            "vulnerability_count": vendor.vulnerability_count
        }
        for vendor in vendors
    ]

@router.get("/products/", response_model=List[Dict[str, Any]])
async def get_products(
    vendor: Optional[str] = Query(None, description="벤더명 필터"),
    search: Optional[str] = Query(None, description="제품명 검색"),
    limit: int = Query(50, ge=1, le=200, description="결과 개수 제한"),
    db: Session = Depends(get_db)
):
    """제품 목록 조회"""
    
    query = db.query(
        Product.name,
        Vendor.name.label('vendor_name'),
        func.count(Vulnerability.id).label('vulnerability_count')
    ).join(Vendor).join(Vulnerability).group_by(Product.name, Vendor.name)
    
    if vendor:
        query = query.filter(Vendor.name.ilike(f'%{vendor}%'))
    
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    
    products = query.order_by(
        desc(func.count(Vulnerability.id))
    ).limit(limit).all()
    
    return [
        {
            "name": product.name,
            "vendor_name": product.vendor_name,
            "vulnerability_count": product.vulnerability_count
        }
        for product in products
    ]