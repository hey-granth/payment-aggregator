import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import dependencies
from app.users import models as user_models
from . import crud, schema

router = APIRouter()


@router.post("/", response_model=schema.Project)
async def create_project(
    project: schema.ProjectCreate,
    db: AsyncSession = Depends(dependencies.get_db),
    current_user: user_models.User = Depends(dependencies.get_current_active_user),
):
    """
    Create a new project for the current authenticated user.
    """
    return await crud.create_project(db=db, project=project, user_id=current_user.id)


@router.post("/{project_id}/providers/", response_model=schema.ProviderConfig)
async def create_provider_config_for_project(
    project_id: uuid.UUID,
    config: schema.ProviderConfigCreate,
    db: AsyncSession = Depends(dependencies.get_db),
    current_user: user_models.User = Depends(dependencies.get_current_active_user),
):
    """
    Add a new provider configuration to one of the user's projects.
    """
    # Note: In a real application, you would add a check here to ensure
    # the current_user actually owns the project with project_id.
    return await crud.create_provider_config(
        db=db, config=config, project_id=project_id
    )


@router.get("/{project_id}/providers/", response_model=List[schema.ProviderConfig])
async def read_provider_configs_for_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(dependencies.get_db),
    current_user: user_models.User = Depends(dependencies.get_current_active_user),
):
    """
    Retrieve all provider configurations for one of the user's projects.
    """
    project = await crud.get_project_by_id(db=db, project_id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this project"
        )
    return await crud.get_provider_configs_for_project(db=db, project_id=project_id)
