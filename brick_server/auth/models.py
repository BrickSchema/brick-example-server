from typing import List, Dict, Any
from pydantic import BaseModel, Field

class TokenResponse(BaseModel):
    token: str = Field(..., description='JWT token')
    name: str = Field(..., description='Associated name with the token')
    exp: int = Field(..., description='The token\'s expiration time in unix timestamp')


TokensResponse = List[TokenResponse]
