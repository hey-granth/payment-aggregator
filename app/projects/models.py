from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy import String, Text, DateTime, UUID, ForeignKey, Boolean
from datetime import datetime
from app.core.database import Base
from uuid import uuid4


# used to define a project which can have multiple provider configurations
class Project(Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    provider_configs = relationship("ProviderConfig", back_populates="project")


# used to define multiple provider configurations for a single project
class ProviderConfig(Base):
    __tablename__ = "provider_configs"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    provider_name: Mapped[str] = mapped_column(String(255), nullable=False)
    credentials: Mapped[str] = mapped_column(Text, nullable=False)
    is_primary: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # indicates if this is the primary provider for the project. when the payment comes to the project, this will decide which provider to use first. other providers can be used as fallback options.

    # commented out the following fields coz doesn't seem needed for now
    # created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    # updated_at: Mapped[datetime] = mapped_column(
    #     DateTime, default=datetime.now, onupdate=datetime.now
    # )

    project = relationship("Project", back_populates="provider_configs")
