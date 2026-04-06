from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy import ForeignKey
from typing import List

# настроить realtionship
class Model(DeclarativeBase):
    pass


class Users(Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key = True)
    username: Mapped[str]
    password_hash: Mapped[str]
    coins: Mapped[int] = mapped_column(default = 0)

    purchases: Mapped[List["Purchases"]] = relationship(back_populates="user")
    
    sent_transactions: Mapped[List["Transactions"]] = relationship(
        foreign_keys="Transactions.from_user_id",
        back_populates="from_user"
    )
    received_transactions: Mapped[List["Transactions"]] = relationship(
        foreign_keys="Transactions.to_user_id",
        back_populates="to_user"
    )



class Merch(Model):
    __tablename__ = "merch"
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str]
    price: Mapped[int]

    purchases: Mapped[List["Purchases"]] = relationship(back_populates="item")

class Purchases(Model):
    __tablename__ = "purchases"
    id: Mapped[int]  = mapped_column(primary_key = True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    merch_id: Mapped[int] = mapped_column(ForeignKey("merch.id"))
    quantity: Mapped[int] = mapped_column(default = 1)

    user: Mapped["Users"] = relationship(back_populates="purchases")
    item: Mapped["Merch"] = relationship(back_populates="purchases")


class Transactions(Model):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key = True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[int]

    from_user: Mapped["Users"] = relationship(
        foreign_keys=[from_user_id],
        back_populates="sent_transactions"
    )
    to_user: Mapped["Users"] = relationship(
        foreign_keys=[to_user_id],
        back_populates="received_transactions"
    )






