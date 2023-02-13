from fastapi import FastAPI
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Dict

app = FastAPI()


# Data models for user and token
class User(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone_number: str
    is_email_verified: bool = False
    is_phone_verified: bool = False


class Token(BaseModel):
    access_token: str
    token_type: str


# User Registration
class UserRegistration(BaseModel):
    username: str
    password: str


# User Login
class UserLogin(BaseModel):
    username: str
    password: str


# Customer Class
class Customer(BaseModel):
    name: str
    email: str


# Account class
class Account(BaseModel):
    account_id: int
    customer_id: int
    balance: float


class QRCode(BaseModel):
    code: str


# Customer account, user, QRCODES DATABASES
customers_db = {}
accounts_db = {}
users_db = {}
qr_codes_db = {}
tokens_db = {}

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# User registration API endpoint
@app.post("/register")
def register(user: UserRegistration):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exist")
    users_db[user.username] = user.password
    return {"message": "User registered successfully"}


# Token Generation API endpoint
@app.post("/token", response_model=Token)
def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or user.password != form_data.password:
        raise HTTPException(status_code=400, detail="Invalid user or password")
    access_token = "random_access_token"
    tokens_db[access_token] = user.username
    return {"access_token": access_token, "token_type": "bearer"}


# User login API endpoint
@app.post("/login")
def login(user: UserLogin):
    if user.username not in users_db or users_db[user.username] != user.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Login Successful"}


# Create Customer function
def create_customer(customer: Customer):
    customer_id = len(customers_db) + 1
    customers_db[customer_id] = customer
    return {"customer_id": customer_id}


# Create a new account API endpoint
@app.post("/accounts")
def create_account(account: Account):
    if account.customer_id not in customers_db:
        raise HTTPException(status_code=400, detail="Customer does not exist")
    return {"message": "Account created successfully"}


# Transfer funds between accounts API Endpoint
@app.post("/accounts/transfer")
def transfer_funds(data: Dict):
    from_account_id = data["from_account_id"]
    to_account_id = data["to_account_id"]
    amount = data["amount"]

    if from_account_id not in accounts_db or to_account_id not in accounts_db:
        raise HTTPException(status_code=400, detail="Account does not exist")
    if accounts_db[from_account_id].balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    accounts_db[from_account_id].balance -= amount
    accounts_db[to_account_id].balance += amount
    return {"message": "Funds transferred successfully"}


# Get Balance Api endpoint
@app.get("/accounts/{account_id}/balance")
def get_account_balance(account_id: int):
    if account_id not in accounts_db:
        raise HTTPException(status_code=400, detail="Account does not exists")
    return {"balance": accounts_db[account_id].balance}


# Generate QR code API endpoint
@app.post("/qrcode")
def generate_qr_code(user: UserLogin):
    if user.username not in users_db or users_db[user.username] != user.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    qr_code = f"{user.username}:{user.password}"
    qr_codes_db[qr_code] = user.username
    return {"qr_code": qr_code}


# Login with QR code API endpoint
@app.post("/login/qrcode")
def login_with_qr_code(qr_code: QRCode):
    if qr_code.code not in qr_codes_db:
        raise HTTPException(status_code=400, detail="Invalid QR code")
    username = qr_codes_db[qr_code.code]
    return {"message": f"Login successful for {username}"}
