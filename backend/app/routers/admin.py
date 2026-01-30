from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.db_models import SystemConfig as SystemConfigModel, UserRole
from app.models import SystemConfig, SystemConfigUpdate
from app.routers.users import get_current_user

router = APIRouter(
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)


# 관리자 권한 확인 의존성
def get_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user.role != UserRole.LIBRARIAN:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")
    return current_user


@router.get("/config", response_model=List[SystemConfig])
async def get_system_config(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    """시스템 설정 조회 (관리자 전용)"""
    configs = db.query(SystemConfigModel).all()
    return configs


@router.put("/config/{key}", response_model=SystemConfig)
async def update_system_config(
    key: str,
    config_update: SystemConfigUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_admin_user)
):
    """시스템 설정 수정 (관리자 전용)"""
    config = db.query(SystemConfigModel).filter(SystemConfigModel.key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="설정을 찾을 수 없습니다")
    
    config.value = config_update.value
    db.commit()
    db.refresh(config)
    
    return config
