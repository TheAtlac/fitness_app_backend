from abc import ABC, abstractmethod

from fitness_app.users.models import User


class BasePermission(ABC):
    @abstractmethod
    def has_permission(self, user: User | None) -> bool: ...


class Anonymous(BasePermission):
    def has_permission(self, user: User | None) -> bool:
        return user is None


class Authenticated(BasePermission):
    def has_permission(self, user: User | None) -> bool:
        return user is not None


class IsCustomer(BasePermission):
    def has_permission(self, user: User | None) -> bool:
        return user is not None and user.role == "CUSTOMER"


class IsCoach(BasePermission):
    def has_permission(self, user: User | None) -> bool:
        return user is not None and user.role == "COACH"
