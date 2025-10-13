from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from . import crud, schema  # NOQA
from app.core import security
from app.core.dependencies import get_db
from ..core.config import settings  # NOQA


router = APIRouter()


@router.post("/users/", response_model=schema.User, status_code=status.HTTP_201_CREATED)
async def create_user(user: schema.UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new user asynchronously.
    """
    db_user = await crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    return await crud.create_user(db=db, user=user)


# @router.post("/token", response_model=schema.Token)
# async def login_for_access_token(
#     db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
# ):
#     """
#     Authenticate user and return an access token asynchronously.
#     """
#     user = await security.authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#
#     access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = security.create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=schema.User)
async def read_users_me(
    current_user: schema.User = Depends(security.get_current_active_user),
) -> schema.User:
    """
    Fetch the current logged in user asynchronously.
    """
    return current_user


router = APIRouter()


@router.post("/login/token")
async def login_for_access_token(
    response: Response,  # 1. Inject the Response object
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    # ... (user authentication logic remains the same)
    user = await security.authenticate_user(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # 2. Set the cookie on the response object
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Prevents JavaScript from reading the cookie
        samesite="lax",  # The core CSRF protection
        secure=True,  # Only send cookie over HTTPS in production
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {"detail": "Login successful"}


@router.post("/token/refresh")
async def refresh_token(
    response: Response,
    refresh_token: str = Cookie(None),  # Extract refresh_token from cookies
    db: AsyncSession = Depends(get_db),
):
    """
    Use the refresh token to get a new access token.
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found"
        )

    user = await security.get_user_from_token(
        db=db, token=refresh_token, token_type="refresh"
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Issue a new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = security.create_access_token(
        data={"sub": user.username, "type": "access"},
        expires_delta=access_token_expires,
    )

    # Set the new access token in a cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        samesite="lax",
        max_age=int(access_token_expires.total_seconds()),
        secure=settings.SECURE_COOKIES,
    )
    return {"detail": "Access token refreshed"}
