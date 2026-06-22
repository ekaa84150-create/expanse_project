from pydantic import BaseModel, Field

class UserCreateSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50, description="Username cannot be empty and must be between 3 and 50 characters")
    password: str = Field(min_length=6, description="Password must be at least 6 characters long")

class UserResponse(BaseModel):
    id: str
    username: str

    class Config:
        from_attributes = True
        
class TokenResponse(BaseModel):
    access_token: str
    token_type: str