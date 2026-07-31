from fastapi import FastAPI, Body
from storage import Session, CustomerDB, AccountDB, load_customers
import bcrypt

app = FastAPI(title = "BankSystem")

def account_to_dict(db_account):
    if db_account is None:
        return None
    return {
        "id": db_account.id,
        "account_number": db_account.account_number,
        "owner_id": db_account.owner_id,
        "balance": db_account.balance,
        "account_type": db_account.account_type,
        "interest_rate": db_account.interest_rate,
        "credit_limit": db_account.credit_limit
    }

def customer_to_dict(db_customer):
    if db_customer is None:
        return None
    return {
        "id": db_customer.id,
        "name": db_customer.name,
        "phone": db_customer.phone,
        
    }
    


@app.get("/")
def root():
    return {"message" : "Banksystem API is running"}

@app.post("/customers")
def create_customers(name: str = Body(...), phone:str = Body(...), password:str = Body(...)):
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    session = Session()
    db_customer = CustomerDB(name = name, phone = phone, password_hash = password_hash)
    session.add(db_customer)
    session.commit()
    result = customer_to_dict(db_customer)
    session.close()
    return result

@app.post("/login")
def login(phone: str = Body(...), password: str = Body(...)):
    session = Session()
    db_customer = session.query(CustomerDB).filter(CustomerDB.phone == phone).first()
    session.close()
    
    if db_customer is None:
        return {"error": "Неверный телефон или пароль"}
    if bcrypt.checkpw(password.encode("utf-8"), db_customer.password_hash.encode("utf-8")):
        return {"message": "Вход выполнен", "customer_id": db_customer.id}
    return {"error": "Неверный телефон или пароль"}

@app.get("/customers")
def get_customers():
    customers = load_customers()
    return [customer_to_dict(c) for c in customers]

@app.get("/customers/{id}")
def get_customer(id: int):
    session = Session()
    db_customer = session.query(CustomerDB).filter(CustomerDB.id == id).first()
    session.close()
    if db_customer:
        return customer_to_dict(db_customer)
    return {"Error" : "Customer not found"}

@app.get("/customers/{customer_id}/accounts")
def get_customer_accounts(customer_id: int):
    session = Session()
    db_customer = session.query(CustomerDB).filter(CustomerDB.id == customer_id).first()
    if db_customer is None:
        session.close()
        return {"error": "Customer not found"}
    accounts = session.query(AccountDB).filter(AccountDB.owner_id == customer_id).all()
    session.close()
   
    return [account_to_dict(acc) for acc in accounts]

@app.post("/customers/{customer_id}/accounts")
def create_account(customer_id: int, account_number: str= Body(...), account_type:str= Body(...), balance:float = Body(...),interest_rate:float = Body(...), credit_limit:float = Body(...)):
    session = Session()
    db_customer = session.query(CustomerDB).filter(CustomerDB.id == customer_id).first()
    
    if db_customer is None:
        session.close()
        return {"error": "Customer not found"}
    
    db_account = AccountDB(
        account_number=account_number,
        owner_id=customer_id,
        account_type=account_type,
        balance=balance,
        interest_rate=interest_rate,
        credit_limit=credit_limit
    )
    session.add(db_account)
    session.commit()
    result = account_to_dict(db_account)
    session.close()
    return result

@app.post("/accounts/{account_number}/deposit")
def deposit(account_number: str, amount: float = Body(...)):
    if amount <= 0:
        return {"error": "Сумма должна быть положительной"}
    session = Session()
    db_account = session.query(AccountDB).filter(AccountDB.account_number == account_number).first()
    if db_account is None:
        session.close()
        return {"error": "Account not found"}
    
    db_account.balance += amount
    session.commit()
    result = account_to_dict(db_account)
    session.close()
    return result

@app.post("/accounts/{account_number}/withdraw")
def withdraw(account_number: str, amount: float = Body(...)):
    if amount <= 0:
        return {"error": "Сумма снятия должна быть положительной"}
    session = Session()
    db_account = session.query(AccountDB).filter(AccountDB.account_number == account_number).first()
    if db_account is None:
        session.close()
        return {"error": "Account not found"}  
    available = db_account.balance
    if db_account.account_type == "credit":
        available += db_account.credit_limit
    
    if amount > available:
        session.close()
        return {"error": f"Недостаточно средств. Доступно: {available}"}
    db_account.balance -= amount
    session.commit()
    result = account_to_dict(db_account)
    session.close()
    return result    

@app.get("/customers/{customer_id}/total")  
def get_total_balance(customer_id: int):
    session = Session()
    account = session.query(AccountDB).filter(AccountDB.owner_id == customer_id).all()
    session.close()
    
    total = sum(acc.balance for acc in account)
    return{
        "customer_id": customer_id,
        "total_balance": total,
        "accounts_count": len(account)
    }
    