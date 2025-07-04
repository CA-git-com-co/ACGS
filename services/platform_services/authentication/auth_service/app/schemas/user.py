from pydantic import BaseModel, EmailStr, Field, field_validator
import re

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Valid email address")
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(None, max_length=100, description="Full name")
    username: str = Field(..., min_length=3, max_length=50, description="Username")

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format and security."""
        if not v:
            raise ValueError("Username is required")

        # Check for valid characters (alphanumeric, underscore, hyphen)
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")

        # Prevent SQL injection patterns
        dangerous_patterns = ['--', ';', '/*', '*/', 'xp_', 'sp_', 'exec', 'execute']
        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError("Username contains invalid characters")

        return v.strip()

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str | None) -> str | None:
        """Validate full name if provided."""
        if v is None:
            return v

        # Remove extra whitespace
        v = v.strip()

        # Check for XSS patterns
        xss_patterns = ['<script', '</script', 'javascript:', 'onload=', 'onerror=']
        v_lower = v.lower()
        for pattern in xss_patterns:
            if pattern in v_lower:
                raise ValueError("Full name contains invalid characters")

        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128, description="Password")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength and security."""
        if not v:
            raise ValueError("Password is required")

        # Check minimum length
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")

        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")

        # Check for at least one digit
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one digit")

        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")

        # Check for common weak passwords
        weak_passwords = ['password', '12345678', 'qwerty', 'admin', 'letmein']
        if v.lower() in weak_passwords:
            raise ValueError("Password is too common")

        return v


class UserUpdate(UserBase):
    password: str | None = None


class UserInDBBase(UserBase):
    id: int
    hashed_password: str

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    pass
