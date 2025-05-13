from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from fitness_app.auth.permissions import BasePermission
from fitness_app.core.dependencies import AuthServiceDep, DbSession
from fitness_app.core.exceptions import UnauthorizedException
from fitness_app.users.models import User

security_schema = HTTPBearer(
    description="Аутентификация при помощи JWT токена", auto_error=False
)


async def authenticate_user(
    session: DbSession,
    auth_service: AuthServiceDep,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(security_schema)
    ] = None,
):
    if credentials is None:
        return None
    return await auth_service.authenticate_user(session, credentials.credentials)


AuthenticateUser = Annotated[User | None, Depends(authenticate_user)]


class HasPermission:
    def __init__(self, permission: BasePermission):
        self._permission = permission

    def __call__(self, user: AuthenticateUser):
        if not self._permission.has_permission(user):
            raise UnauthorizedException()
