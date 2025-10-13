from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from app.core.database import AsyncSessionLocal
from app.core import security
from app.core.config import settings
from app.users import crud as user_crud, models as user_models, schema as user_schemas
from app.projects import crud as project_crud, models as project_models


reusable_oauth2 = security.OAuth2PasswordBearerWithCookie(
    tokenUrl=f"{settings.API_V1_STR}/users/login/token"
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session for a single request.
    """
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> user_models.User:
    """
    Dependency to get the current user from the authentication token.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = user_schemas.TokenData(**payload)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await user_crud.get_user_by_username(db, username=token_data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_active_user(
    current_user: user_models.User = Depends(get_current_user),
) -> user_models.User:
    """
    Dependency to get the current active user. Raises an error if the user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_project_from_api_key(
    api_key: str = Header(..., description="The API Key for your project"),
    db: AsyncSession = Depends(get_db),
) -> project_models.Project:
    """
    Dependency to authenticate a request using a project's API key.
    """
    project = await project_crud.get_project_by_api_key(db=db, api_key=api_key)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )
    return project
