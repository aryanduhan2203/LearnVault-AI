from fastapi import APIRouter, HTTPException

from app.schemas.auth_schema import RegisterRequest, LoginRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

auth_service = AuthService()


@router.post("/register")
def register(payload: RegisterRequest):
    try:
        result = auth_service.register(
            payload.email,
            payload.password
        )

        return {
            "message": result["message"],
            "user": {
                "id": result["user"].id,
                "email": result["user"].email
            } if result["user"] else None,
            "access_token": (
                result["session"].access_token
                if result["session"] else None
            ),
            "refresh_token": (
                result["session"].refresh_token
                if result["session"] else None
            )
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.post("/login")
def login(payload: LoginRequest):
    try:
        result = auth_service.login(
            payload.email,
            payload.password
        )

        return {
            "message": result["message"],
            "user": {
                "id": result["user"].id,
                "email": result["user"].email
            },
            "access_token": result["session"].access_token,
            "refresh_token": result["session"].refresh_token
        }

    except ValueError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error)
        )
