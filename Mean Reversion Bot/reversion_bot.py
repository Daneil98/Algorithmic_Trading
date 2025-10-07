from config import path, login_number

import MetaTrader5 as mt5
import pandas as pd
from time import sleep
from datetime import datetime

def get_indicators():
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, period)
    #print('Rates:', rates)

    open_prices = []
    
    for rate in rates:
        open_price = rate[1]
        open_prices.append(open_price)
        
    #print("Open Prices:", open_prices)
    open_prices_series = pd.Series(open_prices)
    #print("Open Prices Series:", open_prices_series)
    
    sma = open_prices_series.mean()
    std = open_prices_series.std()
    
    return sma, std  

def get_exposure(symbol):
    positions = mt5.positions_get(symbol=symbol)
    
    exposure = 0
    for pos in positions:
        if pos.type == 0:  # Buy position
            exposure += pos.volume
        elif pos.type == 1:  # Sell position
            exposure -= pos.volume
            
    return exposure


def send_market_order(symbol, order_type, volume, sl=0.0, tp=0.0):

    action = mt5.TRADE_ACTION_DEAL    
    
    def get_market_price(symbol, order_type):
        symbol_info = mt5.symbol_info(symbol)      
        if symbol_info is None:
            raise ValueError(f"Failed to get tick for {symbol}: MT5 Error: {mt5.last_error()}")
        elif order_type == 0:
            return symbol_info.ask
        elif order_type == 1:
            return symbol_info.bid
        else:
            raise ValueError("order_type must be 0 (buy) or 1 (sell)")
 
    #Buy Order Request   
    request = {
        "action": action,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY,
        "price": get_market_price("BTCUSD", 0),         #0 is to BUY, 1 is to SELL
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 1,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    res = mt5.order_send(request)
    return res 

def close_position(symbol, where_type=None):
    positions = mt5.positions_get()
    print(f"Open Positions: {positions} \n")

    for pos in positions:
        if pos.type == where_type:
            pos_to_close = pos
            break

    def get_close_price(symbol, order_type):
        symbol_info = mt5.symbol_info(symbol)
        
        if symbol_info is None:
            raise ValueError(f"Failed to get tick for {symbol}: MT5 Error: {mt5.last_error()}")
        elif order_type == 0:
            return symbol_info.bid
        elif order_type == 1:
            return symbol_info.ask
        else:
            raise ValueError("order_type must be 0 (buy) or 1 (sell)")    
        
        
    def reverse_type(order_type):
        #This closes the trade position by reversing the order type
        if order_type == mt5.ORDER_TYPE_BUY:
            return mt5.ORDER_TYPE_SELL
        if order_type == mt5.ORDER_TYPE_SELL:
            return mt5.ORDER_TYPE_BUY


    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'position': pos_to_close.ticket,
        'symbol': symbol,
        'volume': pos_to_close.volume,
        "type": reverse_type(pos_to_close.type),
        "price": get_close_price(symbol, pos_to_close.type),
        'deviation': 20,
        'magic': 0,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    res = mt5.order_send(request)
    return res

if __name__ == "__main__":
    
    result = mt5.initialize()
    
    if result:
        account_info = mt5.account_info()
        login = account_info.login
        print(login)
        if login == login_number:
            print("Connection with MT5 established \n")
        else:
            print("Connected, but account info not available")
            print("Last error:", mt5.last_error())
    else:
        print("Connection failed:", mt5.last_error())
        mt5.shutdown()
        
    
    #GENERAL STRATEGY PARAMETERS: Symbol, timeframe, Bollinger period, standard deviations
    symbol = "BTCUSD"
    timeframe = mt5.TIMEFRAME_M1
    period = 20
    num_std = 1.5
    volume = 0.1
        
   
    while True:
        print(datetime.now())
        print("Getting data...")
        
        #Account Data
        account_info = mt5.account_info()
        balance = account_info.balance
        equity = account_info.equity
        print("Balance:", balance)
        print("Equity:", equity)
        
        #MARKET DATA   
        prices = mt5.symbol_info_tick(symbol)
        bid = prices.bid
        ask = prices.ask
               
        
        #HISTORICAL DATA: Bollinger Band Indicators
        sma, std = get_indicators()
        lower_band = sma - (std * num_std)
        upper_band = sma + (std * num_std)
        
        print("SMA:", sma)
        print("STD:", std)
        print("Lower/Upper bands: ", lower_band, upper_band)
        
        #EXPOSURE ON THE MARKET: Volume, Stop Loss, Take Profit
        exposure = get_exposure(symbol)
        
        entry_signal = None
        exit_signal = None
        
        #SIGNAL FUNCTION
        if ask < lower_band:
            entry_signal = 'buy'
        elif bid > upper_band:
            entry_signal = 'sell'
        print("Entry Signal: ", entry_signal)
        
        #Exit Signal Function
        if bid > sma:
            exit_signal = 'sell'        #Close buy position
        elif ask < sma:
            exit_signal = 'buy'         #Close sell position
        
        
        print("Exit_signal: ", exit_signal)
        
        
        #SUBMIT TRADES
        if entry_signal == 'buy' and exposure == 0:
            print( 'Entering Buy \n')
            order_result = send_market_order(symbol, mt5.ORDER_TYPE_BUY, volume)
            print(order_result, "\n")
            
        if entry_signal == 'sell' and exposure == 0:
            print('Entering Sell')
            order_result = send_market_order(symbol, mt5.ORDER_TYPE_SELL, volume)
            print(order_result, "\n")

        if exit_signal == 'buy' and exposure <= -1:
            print('Closing Sell Position')
            close_order_result = close_position(symbol, where_type=mt5.ORDER_TYPE_SELL)
            print(close_order_result, "\n")
            
        if exit_signal == 'sell' and exposure >= 1:
            print('Closing Buy Position')
            close_order_result = close_position(symbol, where_type=mt5.ORDER_TYPE_BUY)
            print(close_order_result, "\n")
        
        print(f"Exposure on {symbol}:", exposure, f"\n------------------\n")
        
        sleep(1)