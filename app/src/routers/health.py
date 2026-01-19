from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm.session import Session
from src.infra.sqlalchemy.config.database import get_db
from sqlalchemy import text

router = APIRouter(
    prefix="/healthz",
    tags=["Health Check"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}

@router.get("/ready", status_code=status.HTTP_200_OK)
def readiness_check(db: Session = Depends(get_db)):
    try:
        # Tenta executar uma consulta leve (ex: SELECT 1) para verificar a conexão
        db.execute(text("SELECT 1")) 
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        # Se a conexão falhar, retorna status 503 Service Unavailable
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unready", "database": "disconnected", "error": str(e)}
        )
