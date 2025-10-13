from sqlalchemy.ext.asyncio import AsyncSession
from . import schema, models  # NOQA
from secrets import token_urlsafe
from sqlalchemy.future import select
from uuid import UUID


async def create_project(
    db: AsyncSession, project_data: schema.ProjectCreate
) -> models.Project:
    """
    Creates a new project in the database and generate an API Key for it.
    """
    while True:
        api_key = token_urlsafe(
            32
        )  # generates a secure random URL-safe text string, in this case 32 bytes long.
        # checks if the generated API key already exists in the database. if it doesn't, we break the while loop. if it does, the loop runs again and produces a new key.
        existing_project = await get_project_by_api_key(db, api_key=api_key)
        if not existing_project:
            break
    new_project = schema.Project(
        project_name=project_data.project_name,
        api_key=api_key,
        project_id=project_data.project_id,
        created_at=project_data.created_at,
        updated_at=project_data.updated_at,
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return new_project


async def get_project_by_api_key(
    db: AsyncSession, api_key: str
) -> models.Project | None:
    """
    Retrieves a project from the database by its API Key.
    """
    result = await db.execute(select(models.Project).filter_by(api_key=api_key))
    return result.scalars().first()


async def create_provider_config(
    db: AsyncSession, project_id, provider_data: schema.ProviderConfigCreate
) -> models.ProviderConfig:
    """
    Creates a new provider configuration for a specific project.
    """
    new_provider = models.ProviderConfig(
        project_id=project_id,
        provider_name=provider_data.provider_name,
        credentials=provider_data.credentials,
        is_primary=provider_data.is_primary,
    )
    db.add(new_provider)
    await db.commit()
    await db.refresh(new_provider)
    return new_provider


async def get_provider_configs_for_project(
    db: AsyncSession, project_id: UUID
) -> list[models.ProviderConfig]:
    """
    Retrieves all provider configurations for a specific project.
    """
    result = await db.execute(
        select(models.ProviderConfig).filter_by(project_id=project_id)
    )
    return list(result.scalars().all())


async def get_project_by_id(
    db: AsyncSession, project_id: UUID
) -> models.Project | None:
    """
    Retrieves a project from the database by its ID.
    """
    result = await db.execute(select(models.Project).filter_by(project_id=project_id))
    return result.scalars().first()
