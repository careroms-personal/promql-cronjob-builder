from pydantic import BaseModel
from typing import Optional, Literal

class AuthConfig(BaseModel):
  type: Literal["none", "bearer", "basic"] = "none"
  token: Optional[str] = None
  username: Optional[str] = None
  password: Optional[str] = None

class ServerConfig(BaseModel):
  id: str
  url: str
  api: str = "api/v1"
  timeout: int = 30
  auth: Optional[AuthConfig] = None
  headers: dict[str, str] = {}

class ServerConfigs(BaseModel):
  server_configs: list[ServerConfig]
