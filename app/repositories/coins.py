from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Purchases


class PurchasesRepository:
    def __ini__(self, db: AsyncSession):
        self.db = db
    

    def create_purchase():
        