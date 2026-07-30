from fastapi import FastAPI
from storage import Session, CustomerDB, AccountDB, load_customers

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
def create_customers(name: str, phone:str):
    session = Session()
    db_customer = CustomerDB(name = name, phone = phone)
    session.add(db_customer)
    session.commit()
    result = customer_to_dict(db_customer)
    session.close()
    return result

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
def create_account(customer_id: int, account_number: str, account_type:str, balance:float = 0.0,interest_rate:float = 0.0, credit_limit:float = 0.0):
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
def deposit(account_number: str, amount: float):
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
def withdraw(account_number: str, amount: float):
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
    