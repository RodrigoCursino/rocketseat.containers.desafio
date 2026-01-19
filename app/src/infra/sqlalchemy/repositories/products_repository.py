from src.infra.sqlalchemy.models.products import Products
from sqlalchemy.orm import Session
from src.schemas.product_schema import ProductSchema

class ProductsRepository:

    def __init__(self, db: Session):
        self.db = db

    def store(self, product: ProductSchema):

        """ Store a new product in the database """

        model = Products(
            name=product.name,
            price=product.price
        )
        
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return model

    def list(self):
        
        """ List all products from the database """
        return self.db.query(Products).all()
    
    def get_by_id(self, product_id: int):
        
        """ Get a product by its ID """
        return self.db.query(Products).filter(Products.id == product_id).first()
    
    def delete(self, product_id: int):
        
        """ Delete a product by its ID """
        product = self.get_by_id(product_id)
        if product:
            self.db.delete(product)
            self.db.commit()
            return True
        return False
    
    def update(self, product_id: int, product_data: ProductSchema):
        
        """ Update a product by its ID """
        product = self.get_by_id(product_id)
        if product:
            product.name = product_data.name
            product.price = product_data.price
            self.db.commit()
            self.db.refresh(product)
            return product
        return None