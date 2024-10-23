from pydantic import BaseModel, EmailStr


class BaseUser(BaseModel):
    email: EmailStr

    model_config = {
        "json_schema_extra": {
            "example": {
               "email": "fiona@mail.com",
            },
        }
    }

class User(BaseUser):
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
               "email": "fiona@mail.com",
               "password": "green!",
            },
        }
    }

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
