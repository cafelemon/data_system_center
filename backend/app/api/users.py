from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload
from starlette import status

from app.api.deps import get_db, require_admin_user
from app.core.config import settings
from app.core.responses import ApiResponse, ok
from app.core.security import hash_password
from app.models import Department, OperationLog, Role, User
from app.schemas.user import (
    SelectOption,
    StatusOption,
    UserCreate,
    UserListResponse,
    UserOptionsResponse,
    UserRead,
    UserStatusUpdate,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["users"])


def user_query():
    return select(User).options(selectinload(User.role), selectinload(User.department))


def get_user_or_404(db: Session, user_id: int) -> User:
    user = db.scalar(user_query().where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return user


def ensure_unique_user(
    db: Session,
    *,
    username: str | None = None,
    email: str | None = None,
    exclude_user_id: int | None = None,
) -> None:
    conditions = []
    if username is not None:
        conditions.append(User.username == username)
    if email is not None:
        conditions.append(User.email == email)
    if not conditions:
        return

    query = select(User).where(or_(*conditions))
    if exclude_user_id is not None:
        query = query.where(User.id != exclude_user_id)

    duplicate = db.scalar(query)
    if duplicate is not None:
        field = "用户名" if duplicate.username == username else "邮箱"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{field}已存在",
        )


def get_enabled_role(db: Session, role_id: int) -> Role:
    role = db.get(Role, role_id)
    if role is None or not role.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="角色不存在或已停用",
        )
    return role


def get_enabled_department(db: Session, department_id: int) -> Department:
    department = db.get(Department, department_id)
    if department is None or not department.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="部门不存在或已停用",
        )
    return department


def write_user_log(
    db: Session,
    *,
    operator: User,
    operation_type: str,
    target_user: User,
    detail: str,
    request: Request,
) -> None:
    db.add(
        OperationLog(
            user_id=operator.id,
            module="用户管理",
            operation_type=operation_type,
            target_id=str(target_user.id),
            target_name=target_user.real_name,
            operation_detail=detail,
            ip_address=request.client.host if request.client else None,
        )
    )


@router.get("", response_model=ApiResponse[UserListResponse])
def list_users(
    keyword: str | None = Query(default=None, max_length=100),
    role_id: int | None = Query(default=None),
    status_value: str | None = Query(
        default=None,
        alias="status",
        pattern="^(enabled|disabled)$",
    ),
    department_id: int | None = Query(default=None),
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin_user),
) -> ApiResponse[UserListResponse]:
    conditions = []
    if keyword:
        keyword_like = f"%{keyword.strip()}%"
        conditions.append(
            or_(
                User.username.ilike(keyword_like),
                User.real_name.ilike(keyword_like),
                User.email.ilike(keyword_like),
                Department.name.ilike(keyword_like),
            )
        )
    if role_id is not None:
        conditions.append(User.role_id == role_id)
    if status_value:
        conditions.append(User.status == status_value)
    if department_id is not None:
        conditions.append(User.department_id == department_id)

    base_query = select(User).join(User.role).join(User.department).where(*conditions)
    total = db.scalar(
        select(func.count())
        .select_from(User)
        .join(User.role)
        .join(User.department)
        .where(*conditions)
    )
    users = db.scalars(
        base_query.options(selectinload(User.role), selectinload(User.department))
        .order_by(User.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return ok(
        UserListResponse(
            items=[UserRead.model_validate(user) for user in users],
            total=total or 0,
            page=page,
            page_size=page_size,
        )
    )


@router.get("/options", response_model=ApiResponse[UserOptionsResponse])
def get_user_options(
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_admin_user),
) -> ApiResponse[UserOptionsResponse]:
    roles = db.scalars(
        select(Role)
        .where(Role.enabled.is_(True))
        .order_by(Role.sort_order.asc(), Role.id.asc())
    ).all()
    departments = db.scalars(
        select(Department)
        .where(Department.enabled.is_(True))
        .order_by(Department.sort_order.asc(), Department.id.asc())
    ).all()

    return ok(
        UserOptionsResponse(
            roles=[
                SelectOption(id=role.id, name=role.name, code=role.code)
                for role in roles
            ],
            departments=[
                SelectOption(
                    id=department.id,
                    name=department.name,
                    code=department.code,
                )
                for department in departments
            ],
            statuses=[
                StatusOption(label="启用", value="enabled"),
                StatusOption(label="禁用", value="disabled"),
            ],
        )
    )


@router.post("", response_model=ApiResponse[UserRead])
def create_user(
    payload: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> ApiResponse[UserRead]:
    ensure_unique_user(db, username=payload.username, email=payload.email)
    get_enabled_role(db, payload.role_id)
    get_enabled_department(db, payload.department_id)

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password or settings.default_user_password),
        real_name=payload.real_name,
        email=payload.email,
        role_id=payload.role_id,
        department_id=payload.department_id,
        status=payload.status,
    )
    db.add(user)
    db.flush()
    write_user_log(
        db,
        operator=current_user,
        operation_type="新增用户",
        target_user=user,
        detail=f"新增用户 {user.username}",
        request=request,
    )
    db.commit()
    return ok(UserRead.model_validate(get_user_or_404(db, user.id)))


@router.put("/{user_id}", response_model=ApiResponse[UserRead])
def update_user(
    user_id: int,
    payload: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> ApiResponse[UserRead]:
    user = get_user_or_404(db, user_id)
    if user.id == current_user.id and payload.status == "disabled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能禁用当前登录账号",
        )

    ensure_unique_user(db, email=payload.email, exclude_user_id=user.id)
    get_enabled_role(db, payload.role_id)
    get_enabled_department(db, payload.department_id)

    user.real_name = payload.real_name
    user.email = payload.email
    user.role_id = payload.role_id
    user.department_id = payload.department_id
    user.status = payload.status
    if payload.password:
        user.password_hash = hash_password(payload.password)

    write_user_log(
        db,
        operator=current_user,
        operation_type="编辑用户",
        target_user=user,
        detail=f"编辑用户 {user.username}",
        request=request,
    )
    db.commit()
    return ok(UserRead.model_validate(get_user_or_404(db, user.id)))


@router.patch("/{user_id}/status", response_model=ApiResponse[UserRead])
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_user),
) -> ApiResponse[UserRead]:
    user = get_user_or_404(db, user_id)
    if user.id == current_user.id and payload.status == "disabled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能禁用当前登录账号",
        )

    user.status = payload.status
    write_user_log(
        db,
        operator=current_user,
        operation_type="调整用户状态",
        target_user=user,
        detail=f"将用户 {user.username} 状态调整为 {payload.status}",
        request=request,
    )
    db.commit()
    return ok(UserRead.model_validate(get_user_or_404(db, user.id)))
