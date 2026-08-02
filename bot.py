import telebot
from storage import Session, CustomerDB, AccountDB
from datetime import date
import bcrypt

TOKEN = "8774852317:AAHEbRb3c3Z7oWd0_33Yv8EGvTC7HoiUxns"
bot = telebot.TeleBot(TOKEN)
sessions = {}

@bot.message_handler(commands = ["start"])
def start(message):
    bot.reply_to(message, "🏦 Привет! Я банковский бот.\n/register Имя Телефон Пароль\n/login Телефон Пароль\n/help")
    
@bot.message_handler(commands = ["help"])
def help (message):
    bot.reply_to(message, "/register Имя Телефон Пароль\n/login Телефон Пароль\n/balance\n/accounts\n/deposit НомерСчёта Сумма\n/withdraw НомерСчёта Сумма\n/create_account - создать аккаунт")
    
@bot.message_handler(commands = ["register"])
def register(message):
    args = message.text.split()
    if len(args) < 4:
        bot.message_handler(message, "Формат: /register Имя Телефон Пароль")
        return
    
    name = args[1]
    phone = args[2]
    password = args[3]
    password_hash = bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt()).decode("utf-8")    

    session = Session()
    existing = session.query(CustomerDB).filter(CustomerDB.phone == phone).first()
    if existing:
        bot.reply_to(message, "❌ Этот телефон уже зарегистрирован")
        return
    
    db_customer = CustomerDB(
        name = name,
        phone = phone,
        password_hash = password_hash
    )
    session.add(db_customer)
    session.commit()
    session.close()
    
    bot.reply_to(message, f"✅ {name}, вы зарегистрированы! Войдите: /login {phone} пароль")
    
@bot.message_handler(commands = ["login"])
def login(message):
    args = message.text.split()
    if len(args) < 3:
        bot.message_handler(message, "Формат: /login Телефон Пароль")
        return
    
    phone = args[1]
    password = args[2]
    
    session = Session()
    db_customers = session.query(CustomerDB).filter(CustomerDB.phone == phone).first()
    session.close()
    
    if db_customers and bcrypt.checkpw(password.encode(), db_customers.password_hash.encode()):
        sessions[message.chat.id] = db_customers.id
        bot.reply_to(message, f"✅ Вход выполнен, {db_customers.name}!")
    else:
        bot.reply_to(message, "❌ Неверный телефон или пароль")
        
@bot.message_handler(commands = ["balance"])
def balance(message):
    customer_id = sessions.get(message.chat.id) 
    if not customer_id:
        bot.reply_to(message, "❌ Сначала войдите: /login Телефон Пароль")
        return
    
    session = Session()
    accounts = session.query(AccountDB).filter(AccountDB.owner_id  == customer_id).all() 
    session.close()
    
    total = sum(acc.balance for acc in accounts)
    text = f"💰 Ваш общий баланс: {total:.2f} руб\n\nСчета:\n"
    for acc in accounts:
        text += f"• {acc.account_number}: {acc.balance:.2f} руб ({acc.account_type})\n"
    bot.reply_to(message, text)   
    
@bot.message_handler(commands = ["create_account"])  
def create_account(message):
    customer_id = sessions.get(message.chat.id)
    if not customer_id:
        bot.reply_to(message, "❌ Сначала войдите")
        return
    
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "Формат: /create_account НомерСчёта Тип(normal/savings/credit)")
        return
    
    acc_number = args[1]
    acc_type = args[2]
    
    session = Session()
    db_account = AccountDB(
        account_number = acc_number,
        owner_id = customer_id,
        account_type = acc_type,
        balance = 0.0        
    )
    session.add(db_account)
    session.commit()
    session.close()
    
    bot.reply_to(message, f"✅ Счёт {acc_number} создан")
    
    
@bot.message_handler(commands = ["deposit"])
def deposit(message):
    
    customer_id = sessions.get(message.chat.id)
    
    if not customer_id:
        bot.reply_to(message, "❌ Сначала войдите") 
        return
    
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "Формат: /deposit НомерСчёта Сумма") 
        return
    
    acc_number = args[1]
    amount = float(args[2])
    
    if amount < 0:
        bot.reply_to(message, "❌ Сумма должна быть положительной")
        return
    
    
    session = Session()
    account = session.query(AccountDB).filter(
        AccountDB.account_number == acc_number,
        AccountDB.owner_id == customer_id
    ).first()
    if not account:
        session.close()
        bot.reply_to(message, "❌ Счёт не найден или не ваш")
        return
    
    account.balance += amount
    new_balance = account.balance
    session.commit()
    session.close()
    bot.reply_to(message, f"✅ Пополнено {amount:.2f} руб. Баланс счёта: {new_balance:.2f} руб")
      
@bot.message_handler(commands = ["withdraw"])
def withdraw(message):
    customer_id = sessions.get(message.chat.id)
    if not customer_id:
        bot.reply_to(message, "❌ Сначала войдите")
        return
    
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "Формат: /withdraw НомерСчёта Сумма")
        return
    
    acc_number = args[1]
    amount = float(args[2])
    
    if amount <= 0:
        bot.reply_to(message, "❌ Сумма должна быть положительной")
        return
    
    session = Session()
    account = session.query(AccountDB).filter(
        AccountDB.account_number == acc_number,
        AccountDB.owner_id == customer_id
    ).first()
    if not account:
        bot.reply_to(message, "❌ Счёт не найден или не ваш")
        return
    
    aviable = account.balance
    if account.account_type == "credit":
        aviable += account.credit_limit
        
    if amount > aviable:
        bot.reply_to(message, f"❌ Недостаточно средств. Доступно: {aviable:.2f}")
        return
    
    account.balance -= amount
    new_balance = account.balance
    session.commit()
    session.close()
    bot.reply_to(message, f"✅ Со счета снято {amount:.2f} руб. Баланс счёта: {new_balance:.2f} руб")
    
    
bot.polling()