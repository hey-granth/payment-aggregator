from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from . import crud, schema
from app.core import security
from app.core.database import get_db


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


@router.post("/token", response_model=schema.Token)
async def login_for_access_token(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Authenticate user and return an access token asynchronously.
    """
    user = await security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=schema.User)
async def read_users_me(
    current_user: schema.User = Depends(security.get_current_active_user),
) -> schema.User:
    """
    Fetch the current logged in user asynchronously.
    """
    return current_user
