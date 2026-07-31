from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, DeclarativeBase, relationship

DATABASE_URL = "postgresql://postgres:postgres123@db:5432/banksystem"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind = engine)

class Base(DeclarativeBase):
    pass

class CustomerDB(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key = True)
    password_hash = Column(String(100),nullable=False, default="")
    name = Column(String(100), nullable = False)
    phone = Column(String(20), nullable = False)
    
    accounts = relationship("AccountDB", back_populates="owner")
    
class AccountDB(Base):
    __tablename__ = "accounts"  
    
    id = Column(Integer, primary_key = True)
    account_number = Column(String(50), nullable = False, unique = True)
    owner_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    balance = Column(Float, default=0.0)
    account_type = Column(String(20), nullable = False)
    interest_rate = Column(Float, default=0.0)
    credit_limit = Column(Float, default=0.0)
    
    owner = relationship("CustomerDB", back_populates="accounts")

Base.metadata.create_all(engine)

def load_customers():
    session = Session()
    customers = session.query(CustomerDB).all()
    session.close()
    return customers

