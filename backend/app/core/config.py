from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "Atlas AI Command Center"
    app_env: str = "development"
    log_level: str = "INFO"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://atlas:atlas_secret@localhost:5432/atlas_db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    storage_backend: str = "local"
    gcs_bucket_name: str = ""
    
    gemini_api_key: str = ""
    ai_model: str = "gemini-2.0-flash-exp"
    
    approved_email_domains: str = "atlasuniversity.edu.in"
    
    keycloak_server_url: str = ""
    keycloak_realm: str = "atlas"
    keycloak_client_id: str = "atlas-backend"
    keycloak_client_secret: str = ""

    # Comma-separated origins for CORS (e.g. http://localhost:3000,https://app.example.com)
    cors_origins: str = "http://localhost:3000,http://localhost:3000,http://127.0.0.1:3000,http://127.0.0.1:3000"


settings = Settings()
