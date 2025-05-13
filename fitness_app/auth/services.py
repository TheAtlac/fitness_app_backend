from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.auth.schemas import (
    AuthTokenPayload,
    AuthTokenSchema,
    LoginCredentials,
)
from fitness_app.core.exceptions import UnauthorizedException
from fitness_app.users.repositories import UserRepository


class PasswordService:
    def __init__(self):
        self._crypto_context = CryptContext(schemes=["bcrypt"])

    def get_password_hash(self, raw_password: str):
        return self._crypto_context.hash(raw_password)

    def compare_passwords(self, raw_password: str, hashed_password: str):
        return self._crypto_context.verify(raw_password, hashed_password)


class TokenService:
    def __init__(self, secret_key: str, token_lifetime: int):
        self._secret_key = secret_key
        self._token_lifetime = token_lifetime

    def create_auth_token(self, payload: AuthTokenPayload):
        claims = {"exp": datetime.now(UTC) + timedelta(seconds=self._token_lifetime)}
        claims.update(payload.model_dump(mode="json"))

        return jwt.encode(claims, self._secret_key, algorithm="HS256")

    def verify_auth_token(self, token: str):
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=["HS256"],
                options={"required": ["exp"], "verify_exp": True},
                leeway=0.0,
            )
            return AuthTokenPayload.model_validate(payload)
        except jwt.InvalidTokenError:
            return None


class AuthService:
    def __init__(
        self,
        password_service: PasswordService,
        token_service: TokenService,
        user_repository: UserRepository,
    ):
        self._password_service = password_service
        self._token_service = token_service
        self._user_repository = user_repository

    async def login_user(self, session: AsyncSession, credentials: LoginCredentials):
        user = await self._user_repository.get_by_email(session, credentials.email)
        if user is None:
            raise UnauthorizedException()

        if not self._password_service.compare_passwords(
            credentials.password, user.password_hash
        ):
            raise UnauthorizedException()

        payload = AuthTokenPayload(user_id=user.id)
        token = self._token_service.create_auth_token(payload)

        return AuthTokenSchema(token=token)

    async def authenticate_user(self, session: AsyncSession, token: str):
        payload = self._token_service.verify_auth_token(token)
        if payload is None:
            raise UnauthorizedException()

        user = await self._user_repository.get_by_id(session, payload.user_id)
        if user is None:
            raise UnauthorizedException()

        return user
