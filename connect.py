import MetaTrader5 as mt5

result = mt5.initialize()
print("MT5 Initialize:", result)


#GET ACCOUNT INFORMATION
account_info = mt5.account_info()
login = account_info.login
balance = account_info.balance
equity = account_info.equity

print("login:", login)  
print("balance:", balance)
print("equity:", equity)