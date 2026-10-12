from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy import ForeignKey, DateTime, String, Index
from typing import List

from datetime import datetime,UTC


class Model(DeclarativeBase):
    pass

class Users(Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key = True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    coins: Mapped[int] = mapped_column(default = 0)

    __table_args__ = (
        CheckConstraint("coins >= 0", name="check_user_coins_non_negative"),
    )

    purchases: Mapped[List["Inventory"]] = relationship(back_populates="user")
    
    sent_transactions: Mapped[List["Transactions"]] = relationship(
        foreign_keys="Transactions.from_user_id",
        back_populates="from_user"
    )
    received_transactions: Mapped[List["Transactions"]] = relationship(
        foreign_keys="Transactions.to_user_id",
        back_populates="to_user"
    )
    purchase_history: Mapped[List["PurchaseHistory"]] = relationship(
        back_populates="user"
    )


class Merch(Model):
    __tablename__ = "merch"

    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)

    __table_args__ = (
        CheckConstraint("price > 0", name="check_merch_price_positive"),
    )

    purchases: Mapped[List["Inventory"]] = relationship(back_populates="item")
    purchase_history: Mapped[List["PurchaseHistory"]] = relationship(
        back_populates="item"
    )

class Inventory(Model):
    __tablename__ = "purchases"

    id: Mapped[int]  = mapped_column(primary_key = True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    merch_id: Mapped[int] = mapped_column(ForeignKey("merch.id"))
    quantity: Mapped[int] = mapped_column(default = 1)

    __table_args__ = (
        UniqueConstraint("user_id", "merch_id", name="uq_user_merch_inventory"),
        CheckConstraint("quantity > 0", name="check_inventory_quantity_positive"),
        Index("idx_user_inventory", "user_id", "merch_id")
    )

    user: Mapped["Users"] = relationship(back_populates="purchases")
    item: Mapped["Merch"] = relationship(back_populates="purchases")

class Transactions(Model):
    __tablename__ = "transactions"
    
    id: Mapped[int] = mapped_column(primary_key = True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    amount: Mapped[int]

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_transaction_amount_positive"),
        CheckConstraint("from_user_id != to_user_id", name="check_no_self_transfer"),
    )

    from_user: Mapped["Users"] = relationship(
        foreign_keys=[from_user_id],
        back_populates="sent_transactions"
    )
    to_user: Mapped["Users"] = relationship(
        foreign_keys=[to_user_id],
        back_populates="received_transactions"
    )


class PurchaseHistory(Model):
    __tablename__ = "purchase_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    merch_id: Mapped[int] = mapped_column(ForeignKey("merch.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.now(UTC),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_history_quantity_positive"),
    )

    user: Mapped["Users"] = relationship(
        back_populates="purchase_history"
    )

    item: Mapped["Merch"] = relationship(
        back_populates="purchase_history"
    )



