from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fitness_app.file_entities.models import FileEntity


class FileEntityRepository:
    async def save(self, session: AsyncSession, file_entity: FileEntity):
        session.add(file_entity)
        await session.flush()
        await session.commit()
        return file_entity

    async def get_by_id(self, session: AsyncSession, id: int):
        statement = select(FileEntity).where(FileEntity.id == id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_filename(self, session: AsyncSession, filename: str):
        statement = (
            select(FileEntity)
            .where(FileEntity.filename == filename)
            .options(joinedload(FileEntity.exercise))
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def delete(self, session: AsyncSession, file_entity: FileEntity):
        await session.delete(file_entity)
        await session.commit()
        return file_entity
