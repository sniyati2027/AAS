import httpx
from typing import Optional, Dict, Any
from app.core.config import settings


class KeycloakAdmin:
    """Client for Keycloak Admin API."""

    def __init__(self):
        self.server_url = settings.keycloak_server_url
        self.realm = settings.keycloak_realm
        self.client_id = settings.keycloak_client_id
        self.client_secret = settings.keycloak_client_secret
        self._access_token: Optional[str] = None

    async def get_admin_token(self) -> str:
        """Get admin access token from Keycloak."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.server_url}/realms/{self.realm}/protocol/openid-connect/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["access_token"]

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user from Keycloak by email."""
        token = await self.get_admin_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.server_url}/admin/realms/{self.realm}/users",
                params={"email": email},
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            users = response.json()
            return users[0] if users else None

    async def create_user(
        self,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        enabled: bool = True,
    ) -> Dict[str, Any]:
        """Create a new user in Keycloak."""
        token = await self.get_admin_token()
        
        user_data = {
            "email": email,
            "username": email,
            "firstName": first_name,
            "lastName": last_name,
            "enabled": enabled,
            "emailVerified": True,
            "credentials": [
                {
                    "type": "password",
                    "value": password,
                    "temporary": False,
                }
            ],
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.server_url}/admin/realms/{self.realm}/users",
                json=user_data,
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            
            # Get the created user
            user = await self.get_user_by_email(email)
            return user

    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> None:
        """Update user in Keycloak."""
        token = await self.get_admin_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.server_url}/admin/realms/{self.realm}/users/{user_id}",
                json=updates,
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()

    async def delete_user(self, user_id: str) -> None:
        """Delete user from Keycloak."""
        token = await self.get_admin_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.server_url}/admin/realms/{self.realm}/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()


keycloak_admin = KeycloakAdmin()
