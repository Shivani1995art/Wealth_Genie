from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from supabase import create_client, Client
from uuid import UUID

from app.config import settings
from app.schemas import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserLoginRequest,
    UserLoginResponse,
    TokenVerificationResponse,
    ErrorResponse
)
from app.auth import get_current_user_id, verify_jwt

app = FastAPI(title="FinPilot AI - Wealth Genie API", version="1.0.0")

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
supabase_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

# Custom exception handlers to match the Standard Error Schema
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else "Error",
            "detail": str(exc.detail),
            "status_code": exc.status_code
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation Error",
            "detail": str(exc.errors()),
            "status_code": 400
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "status_code": 500
        }
    )

# ----------------- AUTH ROUTERS -----------------

@app.post(
    "/api/v1/auth/register",
    response_model=UserRegisterResponse,
    status_code=201,
    responses={400: {"model": ErrorResponse}}
)
def register_user(request: UserRegisterRequest):
    try:
        response = supabase_client.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User registration failed: empty user returned"
            )
            
        access_token = ""
        if response.session:
            access_token = response.session.access_token
            
        return UserRegisterResponse(
            user_id=UUID(response.user.id),
            email=response.user.email,
            access_token=access_token
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post(
    "/api/v1/auth/login",
    response_model=UserLoginResponse,
    responses={401: {"model": ErrorResponse}}
)
def login_user(request: UserLoginRequest):
    try:
        response = supabase_client.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if not response.session or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
        return UserLoginResponse(
            access_token=response.session.access_token,
            user_id=UUID(response.user.id)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@app.post(
    "/api/v1/auth/logout",
    status_code=204,
    responses={401: {"model": ErrorResponse}}
)
def logout_user(user_id: UUID = Depends(get_current_user_id)):
    # For MVP, FastAPI logout is a stateless no-op
    return

@app.get(
    "/api/v1/auth/verify-token",
    response_model=TokenVerificationResponse,
    responses={401: {"model": ErrorResponse}}
)
def verify_token(user_id: UUID = Depends(get_current_user_id), authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    payload = verify_jwt(token)
    return TokenVerificationResponse(
        user_id=user_id,
        email=payload.get("email", ""),
        aud=payload.get("aud", ""),
        role=payload.get("role", "")
    )
