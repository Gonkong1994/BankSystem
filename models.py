class Accaunt:
    def __init__(self, account_number: str, owner: str, balance: float = 0.0):
        self.account_number = account_number
        self.owner = owner
        self._balance = balance
        
    def __str__(self) -> str:
        return f"Счет {self.account_number} | Владелец {self.owner} | Баланс {self._balance: .2f}"        
        
    @property
    def balance(self) -> float:
        return self._balance
    
    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self._balance += amount
        
    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
        if amount >= self._balance:
            raise ValueError("Недостаточно средств")
        self._balance -= amount
        
class SavingsAccount(Accaunt):
    def __init__(self, account_number: str, owner: str, balance: float = 0, interest_rate: float = 0.05):
        super().__init__(account_number, owner, balance)
        self.interest_rate = interest_rate
        
    def calculate_interest(self) -> float:
        return self._balance * self.interest_rate
    
    def add_interest(self) -> float:
        interest = self.calculate_interest()
        self._balance += interest
        
class CreditAccount(Accaunt):
    def __init__(self, account_number:str, owner:str, balance:float = 0, credit_limit: float = 10000.00):
        super().__init__(account_number, owner, balance)
        self.credit_limit = credit_limit
        
    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
        if amount >= self._balance + self.credit_limit:
            raise ValueError(f"Превышен кредитный лимит. Доступно: {self._balance + self.credit_limit}")
        self._balance -= amount
        
    def __str__(self):
        return f"Счёт {self.account_number} | Владелец: {self.owner} | Баланс: {self._balance:.2f} | Лимит: {self.credit_limit:.2f}"
    
class Customer:
    def __init__(self, name: str, phone: str):
        self.name = name
        self.phone = phone
        self.accounts: list[Accaunt] = []
        
    def add_account(self, accounts : Accaunt) -> None:
        self.accounts.append(accounts)
        
    def get_total_balance(self) -> float:
        return sum(acc.balance for acc in self.accounts)
    
    def __str__(self):
        return f"Клиент: {self.name} | Телефон: {self.phone} | Счетов: {len(self.accounts)}"
        
if __name__ == "__main__":
    ivan = Customer("Иван", "+375291234567")
    
    acc1 = Accaunt("111", ivan.name, 5000)
    saving = SavingsAccount("222", ivan.name, 2000, interest_rate=0.05)
    credit = CreditAccount("333", ivan.name, 3000, credit_limit=10000)
    
    ivan.add_account(acc1)
    ivan.add_account(saving)
    ivan.add_account(credit)
    
    print(ivan)
    print(f"Общий баланс: {ivan.get_total_balance()}")
    
    for acc in ivan.accounts:
        print(acc)
   