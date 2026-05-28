from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    has_api_keys: bool = False

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TradeBase(BaseModel):
    type: str # BUY/SELL
    price: float
    quantity: float

class TradeCreate(TradeBase):
    pass

class TradeResponse(TradeBase):
    id: int
    timestamp: datetime
    is_live: int

    class Config:
        from_attributes = True

class PortfolioResponse(BaseModel):
    balance: float
    btc_amount: float
    trades: List[TradeResponse] = []

    class Config:
        from_attributes = True

class ModelPrediction(BaseModel):
    signal: str
    confidence: float
    current_price: float
    regime: int
    predicted_future_price: Optional[float] = None
    volatility: Optional[float] = None
    error: Optional[str] = None
    
class APIKeySetup(BaseModel):
    exchange_name: str
    api_key: str
    api_secret: str
