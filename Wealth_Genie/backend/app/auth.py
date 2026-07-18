import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from uuid import UUID
from typing import Dict, Any

# We use auto_error=False or standard HTTPBearer to handle auth
security = HTTPBearer()

# Construct JWKS URL from SUPABASE_URL
jwks_url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
jwks_client = jwt.PyJWKClient(jwks_url)

def verify_jwt(token: str) -> Dict[str, Any]:
    try:
        # 1. Retrieve the token header to check the algorithm
        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get("alg")

        if alg == "HS256":
            # Decode using symmetric secret
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated"
            )
        elif alg in ("RS256", "ES256"):
            # Decode using JWKS public keys
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256"],
                audience="authenticated"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Unsupported token algorithm: {alg}"
            )
        
        # Verify custom Supabase role claim
        if payload.get("role") != "authenticated":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: role is not authenticated"
            )
            
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: sub claim is missing"
            )
            
        try:
            UUID(user_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: sub claim is not a valid UUID"
            )
            
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidAudienceError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: audience does not match"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}"
        )

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UUID:
    payload = verify_jwt(credentials.credentials)
    return UUID(payload["sub"])
