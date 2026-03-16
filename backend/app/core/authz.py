import json
import re
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, status

AUTHZ_MAP_PATH = Path(__file__).parent.parent / "authz.map.json"
PUBLIC_MAP_PATH = Path(__file__).parent.parent / "public.map.json"


class AuthorizationEngine:
    def __init__(self):
        self.authz_map = self._load_authz_map()
        self.public_endpoints = self._load_public_endpoints()

    def _load_authz_map(self) -> dict:
        with open(AUTHZ_MAP_PATH, "r") as f:
            return json.load(f)

    def _load_public_endpoints(self) -> list[str]:
        with open(PUBLIC_MAP_PATH, "r") as f:
            data = json.load(f)
            return data.get("endpoints", [])

    def is_public_endpoint(self, path: str) -> bool:
        """Check if an endpoint is public (no auth required)."""
        for pattern in self.public_endpoints:
            # Convert path parameters like {id} to regex patterns
            regex_pattern = re.escape(pattern).replace(r"\{[^}]+\}", "[^/]+")
            if re.match(f"^{regex_pattern}$", path):
                return True
        return False

    def get_allowed_roles(self, path: str, method: str) -> Optional[list[str]]:
        """Get list of roles allowed to access this endpoint."""
        # Check exact match first
        if path in self.authz_map:
            endpoint_rules = self.authz_map[path]
            if method in endpoint_rules:
                return endpoint_rules[method]
            if "ANY" in endpoint_rules:
                return endpoint_rules["ANY"]

        # Check pattern match (for paths with parameters like /api/users/{id})
        for pattern, rules in self.authz_map.items():
            # Convert {id} style params to regex
            regex_pattern = re.sub(r"\{[^}]+\}", r"[^/]+", pattern)
            if re.match(f"^{regex_pattern}$", path):
                if method in rules:
                    return rules[method]
                if "ANY" in rules:
                    return rules["ANY"]

        return None

    def check_permission(
        self, path: str, method: str, user_role: str
    ) -> bool:
        """Check if a user with given role can access the endpoint."""
        # Public endpoints are always accessible
        if self.is_public_endpoint(path):
            return True

        allowed_roles = self.get_allowed_roles(path, method)
        
        if allowed_roles is None:
            # No rule defined - default deny
            return False

        return user_role in allowed_roles

    def require_permission(
        self, path: str, method: str, user_role: str
    ) -> None:
        """Raise HTTPException if user doesn't have permission."""
        if not self.check_permission(path, method, user_role):
            allowed_roles = self.get_allowed_roles(path, method)
            if allowed_roles is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"No authorization rule defined for {method} {path}",
                )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}",
            )


authz_engine = AuthorizationEngine()
