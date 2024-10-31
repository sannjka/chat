from typing import Dict, Optional

from fastapi import Depends, HTTPException, status, Request
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param

from src.auth.jwt_handler import verify_access_token

class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("access_token")
        if not authorization:
            authorization: str = request.headers.get('Authorization')

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:  # pragma: no cover
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl='/api/v1/user/signin',
                                               auto_error=False)

async def authenticate(token: str = Depends(oauth2_scheme)) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Sign in for access'
        )

    decoded_token = verify_access_token(token)
    return decoded_token['sub']

async def get_user_from_cookie(token: str = Depends(oauth2_scheme)) -> str:
    try:
        user = await authenticate(token)
    except HTTPException:
        user = None
    return user
