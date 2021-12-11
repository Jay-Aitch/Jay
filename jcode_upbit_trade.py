import time
import pyupbit
import datetime

access = "uifsuM9KsjnYJQx5jWrjyu9YYx3ZXoXZLpV3oV3l"
secret = "5Kg7PlZvyDyog3dy80P6vj1Z2RChKuHPCDURz576"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute5", count=2)
    #print(df)
    if df.iloc[0]['volume'] < df.iloc[1]['volume'] :
        target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    else:
        target_price = 0
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
signal_buy = 0
while True:
    try:
        now = datetime.datetime.now()
        target_price = get_target_price("KRW-EOS", 0.5)
        current_price = get_current_price("KRW-EOS")
        #print(now, " target_price" , target_price, " current_price" ,current_price)
        eos = get_balance("EOS")
        if signal_buy == 0 :
            if target_price == 0 :
                pass
            elif target_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-EOS", krw*0.9995)
                    signal_buy = 1
        elif signal_buy == 1 :
            eos = get_balance("EOS")
            eos_avg_buy = upbit.get_avg_buy_price("EOS")
            ror = current_price/eos_avg_buy - 1
            #print(eos_avg_buy, " ", ror)
            
            if current_price > eos_avg_buy*1.02 :
                upbit.sell_market_order("KRW-EOS", eos)
                signal_buy = 0
            elif current_price < eos_avg_buy*0.99 :
                upbit.sell_market_order("KRW-EOS", eos)
                signal_buy = 0


        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)