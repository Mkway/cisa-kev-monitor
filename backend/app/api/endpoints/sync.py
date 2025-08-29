"""
데이터 동기화 관리 API 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
import asyncio
import logging

from app.models.base import get_db
from app.models.vulnerability import DataSyncStatus
from app.schemas.vulnerability import DataSyncStatusResponse
from app.services.cisa_sync import cisa_sync_service

logger = logging.getLogger(__name__)

router = APIRouter()

# 동기화 진행 상태 추적
sync_in_progress = False

@router.get("/status", response_model=DataSyncStatusResponse)
async def get_sync_status(db: Session = Depends(get_db)):
    """동기화 상태 조회"""
    
    sync_status = db.query(DataSyncStatus).filter(
        DataSyncStatus.source == "cisa_kev"
    ).first()
    
    if not sync_status:
        raise HTTPException(
            status_code=404,
            detail="Sync status not found"
        )
    
    return sync_status

@router.post("/trigger")
async def trigger_sync(
    background_tasks: BackgroundTasks,
    force: bool = False,
    db: Session = Depends(get_db)
):
    """데이터 동기화 트리거"""
    global sync_in_progress
    
    # 진행 중인 동기화 확인
    if sync_in_progress and not force:
        raise HTTPException(
            status_code=409,
            detail="Sync already in progress"
        )
    
    # 동기화 상태 확인
    sync_status = db.query(DataSyncStatus).filter(
        DataSyncStatus.source == "cisa_kev"
    ).first()
    
    if sync_status and sync_status.status == "in_progress" and not force:
        raise HTTPException(
            status_code=409,
            detail="Sync already in progress in database"
        )
    
    # 백그라운드에서 동기화 실행
    background_tasks.add_task(run_sync_background)
    
    return {
        "message": "Sync triggered successfully",
        "status": "started"
    }

async def run_sync_background():
    """백그라운드 동기화 실행"""
    global sync_in_progress
    
    try:
        sync_in_progress = True
        logger.info("백그라운드 CISA KEV 동기화 시작")
        
        result = await cisa_sync_service.sync_vulnerabilities()
        
        if result['success']:
            logger.info(f"백그라운드 동기화 완료: {result.get('stats', {})}")
        else:
            logger.error(f"백그라운드 동기화 실패: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"백그라운드 동기화 중 예외: {e}")
    finally:
        sync_in_progress = False

@router.post("/sync-now")
async def sync_now(db: Session = Depends(get_db)):
    """즉시 동기화 실행 (동기식)"""
    global sync_in_progress
    
    if sync_in_progress:
        raise HTTPException(
            status_code=409,
            detail="Sync already in progress"
        )
    
    try:
        sync_in_progress = True
        logger.info("즉시 CISA KEV 동기화 시작")
        
        result = await cisa_sync_service.sync_vulnerabilities()
        
        if result['success']:
            return {
                "message": "Sync completed successfully",
                "stats": result.get('stats', {}),
                "catalog_version": result.get('catalog_version'),
                "date_released": result.get('date_released')
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Sync failed: {result.get('error', 'Unknown error')}"
            )
            
    except Exception as e:
        logger.error(f"동기화 중 예외: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Sync failed: {str(e)}"
        )
    finally:
        sync_in_progress = False

@router.get("/progress")
async def get_sync_progress(db: Session = Depends(get_db)):
    """동기화 진행 상황 조회"""
    
    sync_status = db.query(DataSyncStatus).filter(
        DataSyncStatus.source == "cisa_kev"
    ).first()
    
    if not sync_status:
        return {
            "status": "not_initialized",
            "progress": 0,
            "message": "Sync not initialized"
        }
    
    progress = 0
    if sync_status.total_records and sync_status.total_records > 0:
        progress = int(
            (sync_status.processed_records or 0) / sync_status.total_records * 100
        )
    
    return {
        "status": sync_status.status,
        "progress": progress,
        "total_records": sync_status.total_records,
        "processed_records": sync_status.processed_records,
        "last_sync_at": sync_status.last_sync_at,
        "error_message": sync_status.error_message,
        "in_progress_flag": sync_in_progress
    }