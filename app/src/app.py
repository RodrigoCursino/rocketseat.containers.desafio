from fastapi  import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.routers import products, health

api = FastAPI(
    title="API Restaurante 🍔",
    description="API para gerenciamento de pedidos e clientes de um restaurante.",
    version="1.0.0",
    docs_url="/swagger",         # muda o caminho padrão /docs → /swagger
    redoc_url="/documentacao",   # muda /redoc → /documentacao
)


# Configuração do CORS

origins = [
    '*'
]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routes
api.include_router(products.router)
api.include_router(health.router)

@api.get("/")
async def root(request: Request):
    return {"message": "API is running"}

# docker compose down -v
# docker compose up -d --build