from typing import Optional, Dict, Any
import httpx
from jose import jwt, JWTError
from app.core.config import settings


class KeycloakService:
    """Service for validating Keycloak JWT tokens."""

    def __init__(self):
        self.server_url = settings.keycloak_server_url
        self.realm = settings.keycloak_realm
        self.client_id = settings.keycloak_client_id
        self._public_key: Optional[str] = None

    async def get_public_key(self) -> str:
        """Fetch the public key from Keycloak for token verification."""
        if self._public_key:
            return self._public_key

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.server_url}/realms/{self.realm}"
            )
            response.raise_for_status()
            data = response.json()
            self._public_key = (
                f"-----BEGIN PUBLIC KEY-----\n"
                f"{data['public_key']}\n"
                f"-----END PUBLIC KEY-----"
            )
            return self._public_key

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a Keycloak JWT token."""
        if not self.server_url:
            return None

        try:
            public_key = await self.get_public_key()
            
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=self.client_id,
                options={"verify_aud": True},
            )
            
            return payload
        except JWTError as e:
            print(f"Token verification failed: {e}")
            return None


keycloak_service = KeycloakService()
