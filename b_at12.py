import ccxt 
import time
import datetime
import pandas as pd
import math
import telepot   # telepot 모듈 import 

slow_k=0
slow_d=0
slow_k_30m=0
slow_d_30m=0
macd=0
macd_signal =0
macd_osc=0
macd_30m=0
macd_signal_30m =0
macd_osc_30m =0
trailing_target=0
trailing_start=0
trailing_exit=0
buy_phase=0
roe =0
SL_target = -5
TP_target = 100
roe_target = 5
trailing_limit = 2
standby_a=0

# 파일로부터 apiKey, Secret 읽기 
with open("binance_api_key.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip() 
    secret = lines[1].strip() 
    token = lines[2].strip() 
    mc = lines[3].strip() 

bot = telepot.Bot(token) # bot.sendMessage(mc, "test") # 할말 적어서 메시지 보내기 

# binance 객체 생성
binance = ccxt.binance(config={'apiKey': api_key, 'secret': secret, 'enableRateLimit': True, 'options': {'defaultType': 'future'}})
symbol = "BTC/USDT"

# 잔고 조회
balance = binance.fetch_balance(params={"type": "future"})
usdt = balance['total']['USDT']
btc = balance['total']['BTC']

op_mode = False 
position = {"type": None,"amount": 0} 

# 현재가 조회
ticker = binance.fetch_ticker(symbol)

def cal_amount(usdt_balance, cur_price):
    portion = 19 
    usdt_trade = usdt_balance * portion
    amount = math.floor((usdt_trade * 1000000)/cur_price) / 1000000
    return amount 

bot.sendMessage(mc, "START")
print("START")
while True: 
    try:
        #now = datetime.datetime.now()

        # 과거 조회
        btc_ohlcv_5m = binance.fetch_ohlcv(symbol="BTC/USDT", timeframe='5m', since=None, limit=50)
        df_5m = pd.DataFrame(btc_ohlcv_5m, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df_5m['datetime'] = pd.to_datetime(df_5m['datetime'], unit='ms')
        df_5m.set_index('datetime', inplace=True)
        close_5m = df_5m['close']
        ma5_5m = close_5m.rolling(5).mean()
        ma20_5m = close_5m.rolling(20).mean()
        ma60_5m = close_5m.rolling(60).mean()
        ma120_5m = close_5m.rolling(120).mean()
        exp1_5m = close_5m.ewm(span=12, adjust=False).mean()
        exp2_5m = close_5m.ewm(span=26, adjust=False).mean()
        macd_5m = exp1_5m-exp2_5m
        macd_signal_5m = macd_5m.ewm(span=9, adjust=False).mean()
        macd_osc_5m = macd_5m - macd_signal_5m
        Period = 20
        Period2 = 20
        SlowK_period = 3
        SlowD_period = 3
        fast_k_5m = (close_5m - df_5m['low'].rolling(Period2).min()) / (df_5m['high'].rolling(Period2).max() - df_5m['low'].rolling(Period2).min())*100
        slow_k_5m = fast_k_5m.rolling(window=SlowK_period).mean()
        slow_d_5m = slow_k_5m.rolling(window=SlowD_period).mean()

        btc_ohlcv_1m = binance.fetch_ohlcv(symbol="BTC/USDT", timeframe='1m', since=None, limit=50)
        df_1m = pd.DataFrame(btc_ohlcv_1m, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df_1m['datetime'] = pd.to_datetime(df_1m['datetime'], unit='ms')
        df_1m.set_index('datetime', inplace=True)
        close_1m = df_1m['close']
        ma5_1m = close_5m.rolling(5).mean()
        ma20_1m = close_5m.rolling(20).mean()
        ma60_1m = close_5m.rolling(60).mean()
        ma120_1m = close_5m.rolling(120).mean()
        exp1_1m = close_1m.ewm(span=12, adjust=False).mean()
        exp2_1m = close_1m.ewm(span=26, adjust=False).mean()
        macd_1m = exp1_1m-exp2_1m
        macd_signal_1m = macd_1m.ewm(span=9, adjust=False).mean()
        macd_osc_1m = macd_1m - macd_signal_1m
        fast_k_1m = (close_1m - df_1m['low'].rolling(Period).min()) / (df_1m['high'].rolling(Period).max() - df_1m['low'].rolling(Period).min())*100
        slow_k_1m = fast_k_1m.rolling(window=SlowK_period).mean()
        slow_d_1m = slow_k_1m.rolling(window=SlowD_period).mean()

        btc_ohlcv_30m = binance.fetch_ohlcv(symbol="BTC/USDT", timeframe='30m', since=None, limit=50)
        df_30m = pd.DataFrame(btc_ohlcv_30m, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df_30m['datetime'] = pd.to_datetime(df_30m['datetime'], unit='ms')
        df_30m.set_index('datetime', inplace=True)
        close_30m = df_30m['close']
        exp1_30m = close_30m.ewm(span=12, adjust=False).mean()
        exp2_30m = close_30m.ewm(span=26, adjust=False).mean()
        macd_30m = exp1_30m-exp2_30m
        macd_signal_30m = macd_30m.ewm(span=9, adjust=False).mean()
        macd_osc_30m = macd_30m - macd_signal_30m
        
        fast_k_30m = (close_30m - df_30m['low'].rolling(Period2).min()) / (df_30m['high'].rolling(Period2).max() - df_30m['low'].rolling(Period2).min())*100
        slow_k_30m = fast_k_30m.rolling(window=SlowK_period).mean()
        slow_d_30m = slow_k_30m.rolling(window=SlowD_period).mean()

        balance = binance.fetch_balance()
        usdt = balance['total']['USDT']
        btc = balance['total']['BTC']
        positions = balance['info']['positions']
        for c in positions:
            if c["symbol"] == "BTCUSDT":
                btc_position = c
        ent_price = float(btc_position['entryPrice'])
        amt_position = float(btc_position['positionAmt'])
        ticker = binance.fetch_ticker(symbol)
        cur_price = float(ticker['last'])
 
        if amt_position > 0 :
            position['type'] = 'long'
            amount = amt_position
            if buy_phase == 0 :
                buy_phase = 1
        elif amt_position < 0 :
            position['type'] = 'short'
            amount = abs(amt_position)
            if buy_phase == 0 :
                buy_phase = 1
        else :
            amount = cal_amount(usdt, cur_price)
            buy_phase = 0

        if buy_phase >= 1 :
            roe = round((float(btc_position['unrealizedProfit']) / float(btc_position['positionInitialMargin'])) *100,2)
        else :
            roe = 0

        # Enter  
        #if (position['type'] is None) or (position['type']=='long' and buy_phase <= 1 and roe < -3) :
        if (position['type'] is None) :
            #long조건1 
            if slow_k_30m[-2] <= 20 and slow_k_5m[-2] <= 20 :
                print("long1")
                # 
                if slow_k_1m[-2] <= 20 :
                    # 
                    if slow_k_1m[-2] <= slow_d_1m[-2] and slow_k_1m[-1] > slow_d_1m[-1] and macd_osc_1m[-2] < macd_osc_1m[-1] :
                        position['type'] = 'long'
                        if buy_phase == 0 :
                            buy_phase = 1
                            buy_msg = "long 진입(1차) - 조건1"
                            amt = amount
                        elif buy_phase == 1 :
                            buy_phase = 2
                            buy_msg = "long 진입(2차) - 조건1"
                            amt = amount 
                        elif buy_phase == 2 :
                            buy_phase =3
                            buy_msg = "long 진입(3차) - 조건1"
                            amt = amount 
                        position['amount'] = amt
                        binance.create_market_buy_order(symbol=symbol, amount=amt)
                        roe_target = 20
                        buy_condition = 1 
                        SL_target = -20
                        time.sleep(1)
                        bot.sendMessage(mc, buy_msg)
            #long조건2
            elif (macd_5m[-2] < macd_5m[-1] and macd_osc_5m[-2] < macd_osc_5m[-1]) or (macd_5m[-1] > macd_signal_5m[-1])  :
                print("long2")
                # and slow_k_30m[-1] > slow_d_30m[-1] and macd_30m[-2] < macd_30m[-1]
                if slow_k_5m[-1] <= 40 and slow_k_1m[-2] <= 40 :
                    # 
                    if slow_k_1m[-2] <= slow_d_1m[-2] and slow_k_1m[-1] > slow_d_1m[-1] and macd_osc_1m[-2] < macd_osc_1m[-1] :
                        position['type'] = 'long'
                        if buy_phase == 0 :
                            buy_phase = 1
                            buy_msg = "long 진입(1차) - 조건2"
                            amt = amount
                        elif buy_phase == 1 :
                            buy_phase = 2
                            buy_msg = "long 진입(2차) - 조건2"
                            amt = amount 
                        elif buy_phase == 2 :
                            buy_phase =3
                            buy_msg = "long 진입(3차) - 조건2"
                            amt = amount 
                        position['amount'] = amt
                        binance.create_market_buy_order(symbol=symbol, amount=amt)
                        roe_target = 15
                        buy_condition = 2 
                        SL_target = -15
                        time.sleep(1)
                        bot.sendMessage(mc, buy_msg) 
            #long조건3  
            elif macd_30m[-2] < macd_30m[-1] and macd_osc_30m[-2] < macd_osc_30m[-1] :
                print("long3")
                # macd_5m[-2] < macd_5m[-1] andmacd_30m[-1] > macd_signal_30m[-1] and macd_5m[-1] > macd_signal_5m[-1] 
                if slow_k_5m[-2] <= 40 and slow_k_1m[-2] <= 40  :
                    # 
                    if slow_k_1m[-2] <= slow_d_1m[-2] and slow_k_1m[-1] > slow_d_1m[-1] and macd_osc_1m[-2] < macd_osc_1m[-1] :
                        position['type'] = 'long'
                        if buy_phase == 0 :
                            buy_phase = 1
                            buy_msg = "long 진입(1차) - 조건3"
                            amt = amount
                        elif buy_phase == 1 :
                            buy_phase = 2
                            buy_msg = "long 진입(2차) - 조건3"
                            amt = amount 
                        elif buy_phase == 2 :
                            buy_phase =3
                            buy_msg = "long 진입(3차) - 조건3"
                            amt = amount 
                        position['amount'] = amt
                        binance.create_market_buy_order(symbol=symbol, amount=amt)
                        roe_target = 15
                        buy_condition = 3 
                        SL_target = -15
                        time.sleep(1)
                        bot.sendMessage(mc, buy_msg)

        #if (position['type'] is None) or (position['type']=='short' and buy_phase <= 1 and roe < -3) :
        if (position['type'] is None) :
            #short조건1
            if slow_k_30m[-2] >= 80 and slow_k_5m[-2] >= 80  :
                print("short1")
                # 
                if slow_k_1m[-2] >= 80  :
                    # 
                    if slow_k_1m[-2] >= slow_d_1m[-2] and slow_k_1m[-1] < slow_d_1m[-1] and macd_osc_1m[-2] > macd_osc_1m[-1] :
                        position['type'] = 'short'
                        if buy_phase == 0 :
                            buy_phase = 1
                            buy_msg = "short 진입(1차) - 조건1"
                            amt = amount
                        elif buy_phase == 1 :
                            buy_phase = 2
                            buy_msg = "short 진입(2차) - 조건1"
                            amt = amount 
                        elif buy_phase == 2 :
                            buy_phase = 3
                            buy_msg = "short 진입(3차) - 조건1"
                            amt = amount 
                        position['amount'] = amt
                        binance.create_market_sell_order(symbol=symbol, amount=amt)
                        roe_target = 20
                        buy_condition = 1 
                        SL_target = -20
                        time.sleep(1)
                        bot.sendMessage(mc, buy_msg )
            #short조건2
            elif macd_5m[-2] > macd_5m[-1] and macd_osc_5m[-2] > macd_osc_5m[-1] and macd_5m[-1] < macd_signal_5m[-1]  :
                print("short2")
                #and slow_k_30m[-1] < slow_d_30m[-1] and macd_30m[-2] > macd_30m[-1]
                if slow_k_5m[-1] >= 60 and slow_k_1m[-2] >= 60  :
                    
                    # 
                    if slow_k_1m[-2] >= slow_d_1m[-2] and slow_k_1m[-1] < slow_d_1m[-1] and macd_osc_1m[-2] > macd_osc_1m[-1] :
                        position['type'] = 'short'
                        if buy_phase == 0 :
                            buy_phase = 1
                            buy_msg = "short 진입(1차) - 조건2"
                            amt = amount
                        elif buy_phase == 1 :
                            buy_phase = 2
                            buy_msg = "short 진입(2차) - 조건2"
                            amt = amount 
                        elif buy_phase == 2 :
                            buy_phase = 3
                            buy_msg = "short 진입(3차) - 조건2"
                            amt = amount 
                        position['amount'] = amt
                        binance.create_market_sell_order(symbol=symbol, amount=amt)
                        roe_target = 15
                        buy_condition = 2 
                        SL_target = -15
                        time.sleep(1)
                        bot.sendMessage(mc, buy_msg )
            #short조건3
            elif macd_30m[-2] > macd_30m[-1] and macd_osc_30m[-2] > macd_osc_30m[-1]  :
                print("short3")
                # 
                if slow_k_5m[-2] >= 60 and slow_k_1m[-2] >= 60 :
                    # 
                    if slow_k_1m[-2] >= slow_d_1m[-2] and slow_k_1m[-1] < slow_d_1m[-1] and macd_osc_1m[-2] > macd_osc_1m[-1] :
                        position['type'] = 'short'
                        if buy_phase == 0 :
                            buy_phase = 1
                            buy_msg = "short 진입(1차) - 조건3"
                            amt = amount
                        elif buy_phase == 1 :
                            buy_phase = 2
                            buy_msg = "short 진입(2차) - 조건3"
                            amt = amount 
                        elif buy_phase == 2 :
                            buy_phase = 3
                            buy_msg = "short 진입(3차) - 조건3"
                            amt = amount 
                        position['amount'] = amt
                        binance.create_market_sell_order(symbol=symbol, amount=amt)
                        roe_target = 15
                        buy_condition = 3
                        SL_target = -15
                        time.sleep(1)
                        bot.sendMessage(mc, buy_msg )

        
        if position['type'] is None :
            trailing_start =0
            trailing_target=0
            trailing_exit=0
        

        # Exit 
        if buy_phase >= 1 :
            if roe >= roe_target :
                trailing_start =1 
            if trailing_start == 1 :
                if roe > trailing_target :
                    trailing_target = roe
                    trailing_exit = 0
                elif roe < trailing_target:
                    if roe < trailing_target - trailing_limit :
                        trailing_exit = 1
                        trailing_target = 0     
            if position['type'] == 'long':  # or slow_k_30m[-1] <= slow_d_30m[-1] and slow_k_5m[-1] >= 50 and slow_k_1m[-2] >= 50
                if buy_condition == 1 and slow_k_30m[-1] >= 80 and slow_k_5m[-1] >= 80 and slow_k_1m[-2] >= 80 and slow_k_1m[-2] >= slow_d_1m[-2] and slow_k_1m[-1] < slow_d_1m[-1] and macd_osc_1m[-2] > macd_osc_1m[-1]  :
                    binance.create_market_sell_order(symbol=symbol, amount=amount)
                    time.sleep(1)
                    position['type'] = None 
                    bot.sendMessage(mc, "long 청산(1) : "+str(roe)+"%")
                    buy_phase=0
                elif buy_condition == 1 and slow_k_30m[-2] >= slow_d_30m[-2] and slow_k_30m[-1] < slow_d_30m[-1] :
                    binance.create_market_sell_order(symbol=symbol, amount=amount)
                    time.sleep(1)
                    position['type'] = None 
                    bot.sendMessage(mc, "long 청산(2) : "+str(roe)+"%")
                    buy_phase=0
                elif buy_condition == 2 and slow_k_5m[-1] >= 80 and slow_k_1m[-2] >= slow_d_1m[-2] and slow_k_1m[-1] < slow_d_1m[-1] and macd_osc_1m[-2] > macd_osc_1m[-1] :
                    binance.create_market_sell_order(symbol=symbol, amount=amount)
                    time.sleep(1)
                    position['type'] = None 
                    bot.sendMessage(mc, "long 청산(3) : "+str(roe)+"%")
                    buy_phase=0
                elif buy_condition == 3 and slow_k_5m[-1] >= 80 and slow_k_1m[-2] >= slow_d_1m[-2] and slow_k_1m[-1] < slow_d_1m[-1] and macd_osc_1m[-2] > macd_osc_1m[-1]  :
                    binance.create_market_sell_order(symbol=symbol, amount=amount)
                    time.sleep(1)
                    position['type'] = None 
                    bot.sendMessage(mc, "long 청산(4) : "+str(roe)+"%")
                    buy_phase=0
                elif buy_condition == 3 and slow_k_5m[-2] >= slow_d_5m[-2] and slow_k_5m[-1] < slow_d_5m[-1] :
                    binance.create_market_sell_order(symbol=symbol, amount=amount)
                    time.sleep(1)
                    position['type'] = None 
                    bot.sendMessage(mc, "long 청산(5) : "+str(roe)+"%")
                    buy_phase=0
                elif roe > TP_target :
                    binance.create_market_sell_order(symbol=symbol, amount=amount)
                    time.sleep(1)
                    position['type'] = None 
                    bot.sendMessage(mc, "long 청산(TP) : "+str(roe)+"%")
                    buy_phase=0   
                elif roe < SL_target :
                    binance.create_market_sell_order(symbol=symbol, amount=amount)
                    time.sleep(1)
                    position['type'] = None 
                    bot.sendMessage(mc, "long 청산(SL) : "+str(roe)+"%")
                    buy_phase=0
                elif trailing_exit==1 :
                    binance.create_market_sell_order(symbol=symbol, amount=amount)
                    time.sleep(1)
                    position['type'] = None 
                    bot.sendMessage(mc, "long 청산(trailing) : "+str(roe)+"%" )
                    buy_phase=0
                
            if position['type'] == 'short':  #   or slow_k_30m[-1] >= slow_d_30m[-1])
                if buy_condition == 1 and slow_k_30m[-1] <= 20 and slow_k_5m[-1] <= 20 and slow_k_1m[-2] <= 20 and slow_k_1m[-2] <= slow_d_1m[-2] and slow_k_1m[-1] > slow_d_1m[-1] and macd_osc_1m[-2] < macd_osc_1m[-1]  :
                    binance.create_market_buy_order(symbol=symbol, amount=amount)
                    time.sleep(1)
                    position['type'] = None 
                    bot.sendMessage(mc, "short 청산(1) : "+str(roe)+"%")
                    buy_phase=0
                elif buy_condition == 1 and slow_k_30m[-2] <= slow_d_30m[-2] and slow_k_30m[-1] > slow_d_30m[-1] :
                    binance.create_market_buy_order(symbol=symbol, amount=amount)
                    time.sleep(1)
                    position['type'] = None 
                    bot.sendMessage(mc, "short 청산(2) : "+str(roe)+"%")
                    buy_phase=0
                elif buy_condition == 2 and slow_k_5m[-1] <= 20 and slow_k_1m[-2] <= slow_d_1m[-2] and slow_k_1m[-1] > slow_d_1m[-1] and macd_osc_1m[-2] < macd_osc_1m[-1]  :
                    binance.create_market_buy_order(symbol=symbol, amount=amount)
                    time.sleep(1)
                    position['type'] = None 
                    bot.sendMessage(mc, "short 청산(3) : "+str(roe)+"%")
                    buy_phase=0   
                elif buy_condition == 3 and slow_k_5m[-1] <= 20 and slow_k_1m[-2] <= slow_d_1m[-2] and slow_k_1m[-1] > slow_d_1m[-1] and macd_osc_1m[-2] < macd_osc_1m[-1]  :
                    binance.create_market_buy_order(symbol=symbol, amount=amount)
                    time.sleep(1)
                    position['type'] = None 
                    bot.sendMessage(mc, "short 청산(4) : "+str(roe)+"%")
                    buy_phase=0
                elif buy_condition == 3 and slow_k_5m[-2] <= slow_d_5m[-2] and slow_k_5m[-1] > slow_d_5m[-1] :
                    binance.create_market_buy_order(symbol=symbol, amount=amount)
                    time.sleep(1)
                    position['type'] = None 
                    bot.sendMessage(mc, "short 청산(5) : "+str(roe)+"%")
                    buy_phase=0 
                elif roe > TP_target : 
                    binance.create_market_buy_order(symbol=symbol, amount=amount)
                    time.sleep(1)
                    position['type'] = None 
                    bot.sendMessage(mc, "short 청산(TP) : "+str(roe)+"%")
                    buy_phase=0
                elif roe < SL_target : 
                    binance.create_market_buy_order(symbol=symbol, amount=amount)
                    time.sleep(1)
                    position['type'] = None 
                    bot.sendMessage(mc, "short 청산(SL) : "+str(roe)+"%")
                    buy_phase=0
                elif trailing_exit==1 :
                    binance.create_market_buy_order(symbol=symbol, amount=amount)
                    time.sleep(1)
                    position['type'] = None 
                    bot.sendMessage(mc, "short 청산(trailing) : "+str(roe)+"%")
                    buy_phase=0
        

        #print(SL_target,roe_target,buy_phase )
        time.sleep(1)
    except Exception as e:
        print(str(e))
        bot.sendMessage(mc, str(e))
        time.sleep(5)
