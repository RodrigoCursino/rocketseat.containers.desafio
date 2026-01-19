from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm.session import Session
from fastapi import Depends

from src.infra.sqlalchemy.repositories.products_repository import ProductsRepository
from src.infra.sqlalchemy.config.database import get_db
from src.schemas.product_schema import ProductSchema

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductSchema)
def create_product(product: ProductSchema, db: Session = Depends(get_db)):
    repository = ProductsRepository(db)
    return repository.store(product)

@router.get("/", response_model=list[ProductSchema])
def list_product(db: Session = Depends(get_db)):
    repository = ProductsRepository(db)
    return repository.list()

@router.get("/{product_id}", response_model=ProductSchema)
def get_product(product_id: int, db: Session = Depends(get_db)):
    repository = ProductsRepository(db)
    product = repository.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    repository = ProductsRepository(db)
    success = repository.delete(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return

@router.put("/{product_id}", response_model=ProductSchema)
def update_product(product_id: int, product: ProductSchema, db: Session = Depends(get_db)):
    repository = ProductsRepository(db)
    updated_product = repository.update(product_id, product)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product
