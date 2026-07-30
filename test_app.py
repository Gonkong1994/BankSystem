import os
os.environ["POSTGRES_HOST"] = "localhost"
from starlette.testclient import TestClient
from app import app
import random

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message" : "Banksystem API is running"}
    
def test_create_customer():
    response = client.post("/customers/", json={
        "name" : "Ivan",
        "phone": "+375291234567"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Ivan" 
    assert data["phone"] == "+375291234567"
    assert "id" in data
    
def test_get_customers():
    client.post("/customers/", json={
        "name" : "Ivan",
        "phone": "+375291234567"
    })
    response = client.get("/customers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data,list)
    assert len(data) >= 1
    
def test_create_account():
    response = client.post("/customers/", json={
            "name" : "Ivan",
            "phone": "+375291234567"
        })
    data = response.json()
    customer_id = data["id"]
    
    response = client.post(f"/customers/{customer_id}/accounts", json={
        "account_number": f"ACC-{random.randint(10000, 99999)}",
        "owner_id": customer_id,
        "account_type" : "Normal",
        "balance" : 1000.00,
        "interest_rate" : 0.10,
        "credit_limit" :10000
    })
    assert response.status_code ==200
    data = response.json()
    assert data["account_number"].startswith("ACC-")
    assert data["account_type"] == "Normal"
    assert data["balance"] == 1000.00
    assert data["interest_rate"] == 0.10
    assert data["credit_limit"] == 10000
    
def test_deposit():
    response = client.post("/customers/", json={
                "name" : "Ivan",
                "phone": "+375291234567"
            })
    data = response.json()
    customer_id = data["id"]
    
    acc_number = f"ACC-{random.randint(10000, 99999)}"
    response = client.post(f"/customers/{customer_id}/accounts", json={
            "account_number": acc_number,
            "owner_id": customer_id,
            "account_type" : "Normal",
            "balance" : 1000.00,
            "interest_rate" : 0.10,
            "credit_limit" :10000
        })
    
    
    data = response.json()
    account_number = data["account_number"]
    response = client.post(f"/accounts/{account_number}/deposit", json=500.00)  
        
    
    
    assert response.status_code ==200
    data = response.json()
    assert data["balance"] == 1500.00
   
def test_withdraw():
    response = client.post("/customers/", json={
                    "name" : "Ivan",
                    "phone": "+375291234567"
                })
    data = response.json()
    customer_id = data["id"]
        
    acc_number = f"ACC-{random.randint(10000, 99999)}"
    response = client.post(f"/customers/{customer_id}/accounts", json={
            "account_number": acc_number,
            "owner_id": customer_id,
            "account_type" : "Normal",
            "balance" : 1000.00,
            "interest_rate" : 0.10,
            "credit_limit" :10000
            })
        
        
    data = response.json()
    account_number = data["account_number"]
    response = client.post(f"/accounts/{account_number}/withdraw", json=500.00)
    assert response.status_code ==200
    data = response.json()
    assert data["balance"] == 500.00
    
def test_total_balance():
    response = client.post("/customers/", json={
                        "name" : "Ivan",
                        "phone": "+375291234567"
                    })
    data = response.json()
    customer_id = data["id"]
            
    acc_number_1 = f"ACC-{random.randint(10000, 99999)}"
    client.post(f"/customers/{customer_id}/accounts", json={
            "account_number": acc_number_1,
            "owner_id": customer_id,
            "account_type" : "Normal",
            "balance" : 1000.00,
            "interest_rate" : 0.10,
            "credit_limit" :10000
            })
    acc_number_2 = f"ACC-{random.randint(10000, 99999)}"
    client.post(f"/customers/{customer_id}/accounts", json={
            "account_number": acc_number_2,
            "owner_id": customer_id,
            "account_type" : "Save",
            "balance" : 2000.00,
            "interest_rate" : 0.10,
            "credit_limit" :10000
            })
    response = client.get(f"/customers/{customer_id}/total")
    assert response.status_code ==200
    data = response.json()
    assert data["total_balance"] == 3000.00
    