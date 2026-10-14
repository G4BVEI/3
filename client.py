from dataclasses import dataclass, replace
from datetime import date
from typing import Literal, Optional
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class Ok[T]:
    value: T


@dataclass(frozen=True, slots=True)
class Err[E]:
    error: E


type Result[T, E] = Ok[T] | Err[E]

type ClientError = Literal[
    "name_required",
    "name_too_long",
    "cpf_required",
    "email_required",
    "invalid_email",
    "invalid_birth_date",
]

MAX_NAME_LEN = 250


def is_valid_email(email: str) -> bool:
    if email.count("@") != 1:
        return False

    user, domain = email.split("@")

    if not user or not domain:
        return False

    if "." not in domain:
        return False

    parts = domain.split(".")
    if len(parts) < 2 or any(p == "" for p in parts):
        return False

    return True


class Client:
    def __init__(
        self,
        *,
        id: UUID,
        name: str,
        cpf: str,
        email: str,
        birth_date: date,
        phone: Optional[str] = None,
        is_active: bool = True,
    ) -> None:
        self.id = id
        self.name = name
        self.cpf = cpf
        self.email = email
        self.birth_date = birth_date
        self.phone = phone
        self.is_active = is_active

    @staticmethod
    def validate(
        name: str, cpf: str, email: str, birth_date: object
    ) -> Optional[ClientError]:
        if not name:
            return "name_required"
        if len(name) > MAX_NAME_LEN:
            return "name_too_long"
        if not cpf:
            return "cpf_required"
        if not email:
            return "email_required"
        if not is_valid_email(email):
            return "invalid_email"
        if not isinstance(birth_date, date):
            return "invalid_birth_date"
        return None

    @classmethod
    def create(
        cls,
        name: str,
        cpf: str,
        email: str,
        birth_date: date,
        phone: Optional[str] = None,
        id: Optional[UUID] = None,
        is_active: bool = True,
    ) -> Result["Client", ClientError]:

        if (err := cls.validate(name, cpf, email, birth_date)) is not None:
            return Err(err)

        return Ok(
            cls(
                id=id or uuid4(),
                name=name,
                cpf=cpf,
                email=email.lower(),
                birth_date=birth_date,
                phone=phone,
                is_active=is_active,
            )
        )

    def age(self) -> int:
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True

    def __str__(self) -> str:
        return f"{self.name} - {self.email} ({self.is_active})"

    def __repr__(self) -> str:
        return f"<Client {self.name} ({self.id})>"


@dataclass(frozen=True, slots=True)
class ClientDraft:
    name: str = "João"
    cpf: str = "123"
    email: str = "a@b.com"
    birth_date: date = date(1990, 1, 1)
    phone: Optional[str] = None
    id: Optional[UUID] = None
    is_active: bool = True

    def with_(self, **kw) -> "ClientDraft":
        return replace(self, **kw)

    def build(self) -> Result[Client, ClientError]:
        return Client.create(
            name=self.name,
            cpf=self.cpf,
            email=self.email,
            birth_date=self.birth_date,
            phone=self.phone,
            id=self.id,
            is_active=self.is_active,
        )
