from sqlalchemy import Column, String, Numeric
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Wallet(Base):
    __tablename__ = 'wallets'

    uuid = Column(String, primary_key=True, nullable=False)
    balance = Column(Numeric(precision=10, scale=2), nullable=False, default=0)
