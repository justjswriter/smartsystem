from datetime import datetime

from pydantic import BaseModel, Field


class PlantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    species: str | None = Field(default=None, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    description: str | None = None
    image_url: str | None = None


class PlantUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    species: str | None = Field(default=None, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    description: str | None = None
    image_url: str | None = None


class PlantResponse(BaseModel):
    id: int
    user_id: int
    name: str
    species: str | None
    location: str | None
    description: str | None
    image_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
