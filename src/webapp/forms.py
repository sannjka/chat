from typing import Self
from pydantic import BaseModel, EmailStr, Field, model_validator
from fastapi.exceptions import RequestValidationError


class UserData(BaseModel):
    username: EmailStr = Field(..., description='Электронная почта')
    password: str = Field(
        ..., min_length=5, max_length=50, description='Пароль',
    )

class UserRegister(UserData):
    password_check: str = Field(
        ..., min_length=5, max_length=50, description='Подтверждение пароля',
    )

    @model_validator(mode='after')
    def check_password_match(self) -> Self:
        pw1 = self.password
        pw2 = self.password_check
        if pw1 != pw2:
            raise RequestValidationError('password do not match')
        return self
