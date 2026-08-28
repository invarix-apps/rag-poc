import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, UserPlan
from app.errors import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.lib.security import create_access_token, hash_password, verify_password


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.__session = session

    async def register(
        self,
        name: str,
        email: str,
        password: str,
        plan: UserPlan = UserPlan.NO_AI,
    ) -> User:
        if await self.__get_by_email(email) is not None:
            raise EmailAlreadyRegisteredError()

        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            plan=plan,
        )
        self.__session.add(user)
        await self.__session.commit()
        await self.__session.refresh(user)
        return user

    async def login(self, email: str, password: str) -> str:
        user = await self.__get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        return create_access_token(user.id)

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.__session.get(User, user_id)

    async def __get_by_email(self, email: str) -> User | None:
        result = await self.__session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
