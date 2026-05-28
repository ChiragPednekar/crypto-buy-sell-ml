from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    
    # Real Exchange Encrypted Keys (Phase 1 Layer)
    exchange_name = Column(String, default="binance")
    api_key_encrypted = Column(String, nullable=True)
    api_secret_encrypted = Column(String, nullable=True)

    portfolio = relationship("Portfolio", back_populates="user", uselist=False)
    trades = relationship("Trade", back_populates="user")

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    balance = Column(Float, default=10000.0) # start with $10k paper trading
    btc_amount = Column(Float, default=0.0)

    user = relationship("User", back_populates="portfolio")

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String) # "BUY" or "SELL"
    price = Column(Float)
    quantity = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_live = Column(Integer, default=0) # 0 for Paper, 1 for Exchange Live

    user = relationship("User", back_populates="trades")
