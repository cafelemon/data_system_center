from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from starlette import status

from app.api.deps import get_current_user, get_db
from app.core.responses import ApiResponse, ok
from app.core.security import create_access_token, verify_password
from app.models import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.operation_logs import write_operation_log

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=ApiResponse[TokenResponse])
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ApiResponse[TokenResponse]:
    user = db.scalar(
        select(User)
        .options(selectinload(User.role), selectinload(User.department))
        .where(User.username == payload.username)
    )
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    if user.status != "enabled":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已禁用",
        )
    if not user.role.enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号角色已停用",
        )

    access_token, expires_in = create_access_token(user.id)
    user_read = UserRead.model_validate(user)
    write_operation_log(
        db,
        module="登录认证",
        operation_type="登录系统",
        operator=user,
        target_id=str(user.id),
        target_name=user.real_name,
        detail=f"用户 {user.username} 登录系统",
        request=request,
    )
    db.commit()

    return ok(
        TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
            user=user_read,
        )
    )


@router.get("/me", response_model=ApiResponse[UserRead])
def read_current_user(
    current_user: User = Depends(get_current_user),
) -> ApiResponse[UserRead]:
    return ok(UserRead.model_validate(current_user))
