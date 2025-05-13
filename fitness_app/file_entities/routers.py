from fastapi import APIRouter, Depends, UploadFile, status

from fitness_app.auth.dependencies import HasPermission
from fitness_app.auth.permissions import Authenticated
from fitness_app.core.dependencies import DbSession, FileEntityServiceDep
from fitness_app.file_entities.schemas import FileEntitySchema

file_entities_router = APIRouter(prefix="/files", tags=["Файлы"])


@file_entities_router.get(
    "/{filename:path}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Файла с указанным filename не найдено"
        }
    },
    response_model=str,
    summary="Получение ссылки на файл по filename",
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def get_by_filename(
    session: DbSession,
    service: FileEntityServiceDep,
    filename: str,
) -> str:
    return await service.get_by_filename(session, filename)


@file_entities_router.post(
    "/",
    response_model=FileEntitySchema,
    summary="Добавление файла",
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def create(
    session: DbSession,
    service: FileEntityServiceDep,
    file: UploadFile,
) -> FileEntitySchema:
    file_entity = await service.create(session, file)
    full_url = await service.get_by_filename(session, file_entity.filename)
    return FileEntitySchema(**file_entity.__dict__, full_url=full_url)
