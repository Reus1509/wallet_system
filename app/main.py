from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from app.models import Wallet, Base

load_dotenv()

DB_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = None
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        if hasattr(request.state, 'db'):
            request.state.db.close()
    return response


class OperationRequest(BaseModel):
    operation_type: str
    amount: float


class CreateWalletRequest(BaseModel):
    wallet_uuid: str
    initial_balance: float = 0.0


class BalanceResponse(BaseModel):
    balance: float


def get_wallet(db, wallet_uuid: str):
    return db.query(Wallet).filter(Wallet.uuid == wallet_uuid).first()


def update_balance(db, wallet_uuid: str, amount: float, operation_type: str):
    wallet = get_wallet(db, wallet_uuid)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    new_balance = float(wallet.balance) + amount if operation_type == 'DEPOSIT' else float(wallet.balance) - amount
    if new_balance < 0:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    wallet.balance = new_balance
    db.commit()
    return wallet


@app.post("/api/v1/wallets/{wallet_uuid}/operation")
async def perform_operation(wallet_uuid: str, operation_request: OperationRequest, request: Request):
    db = request.state.db
    try:
        update_balance(db, wallet_uuid, operation_request.amount, operation_request.operation_type)
        return {"message": f"{operation_request.operation_type} successful"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/v1/wallets/{wallet_uuid}")
async def get_balance(wallet_uuid: str, request: Request):
    db = request.state.db
    wallet = get_wallet(db, wallet_uuid)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return BalanceResponse(balance=float(wallet.balance))

@app.post("/api/v1/wallets/")
async def create_wallet(create_wallet_request: CreateWalletRequest, request: Request):
    db = request.state.db
    new_wallet = Wallet(uuid=create_wallet_request.wallet_uuid, balance=create_wallet_request.initial_balance)
    db.add(new_wallet)
    db.commit()
    return {"uuid": new_wallet.uuid, "initial_balance": new_wallet.balance}


@app.delete("/api/v1/wallets/{wallet_uuid}")
async def delete_wallet(wallet_uuid: str, request: Request):
    db = request.state.db
    wallet = get_wallet(db, wallet_uuid)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    db.delete(wallet)
    db.commit()
    return {"message": f"Wallet {wallet_uuid} deleted successfully"}


@app.get("/api/v1/wallets")
async def get_all_wallets(request: Request):
    db = request.state.db
    wallets = db.query(Wallet).all()
    results = [
        {
            "uuid": wallet.uuid,
            "balance": float(wallet.balance),
        } for wallet in wallets
    ]
    return results


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
