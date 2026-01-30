from fastapi import APIRouter, HTTPException, Query, Depends, Header
from sqlalchemy.orm import Session
from typing import Optional
import hashlib

from app.models import User as UserSchema, UserCreate, UserUpdate, UserLogin
from app.db_models import User as UserModel
from app.database import get_db

router = APIRouter()


def hash_password(password: str) -> str:
    """간단한 비밀번호 해싱 (실제로는 bcrypt 사용 권장)"""
    return hashlib.sha256(password.encode()).hexdigest()


async def get_current_user(x_user_id: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """현재 로그인한 사용자 가져오기 (헤더 기반 임시 인증)"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다")
    
    user = db.query(UserModel).filter(UserModel.user_id == int(x_user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="유효하지 않은 사용자입니다")
    
    return user


@router.get("/", response_model=list[UserSchema])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """회원 목록 조회"""
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """특정 회원 조회"""
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다")
    return user


@router.post("/", response_model=UserSchema, status_code=201)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """회원 가입"""
    # 이메일 중복 체크
    existing = db.query(UserModel).filter(UserModel.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다")
    
    new_user = UserModel(
        email=user_data.email,
        password=hash_password(user_data.password),
        name=user_data.name,
        phone=user_data.phone,
        address=user_data.address,
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """로그인"""
    user = db.query(UserModel).filter(UserModel.email == login_data.email).first()
    if not user or user.password != hash_password(login_data.password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다")
    
    return {
        "success": True,
        "message": "로그인 성공",
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    }


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """회원 정보 수정"""
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다")
    
    update_data = user_data.model_dump(exclude_unset=True)
    
    # 비밀번호 변경 시 해싱 처리
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])
        
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """회원 삭제"""
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다")
    
    db.delete(user)
    db.commit()
