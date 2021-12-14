import time
import pyupbit
import datetime
import telepot   # telepot 모듈 import 
token = "" # 봇 API 입력 
# mc = "" # 텔레그램 숫자 ID 입력 
mc = ""
bot = telepot.Bot(token) 
# bot.sendMessage(mc, "test") # 할말 적어서 메시지 보내기 


access = ""
secret = ""



def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
bot.sendMessage(mc, "auto trade start")

# 자동매매 시작
signal_buy = 0
while True:
    try:
        now = datetime.datetime.now()
        ticker = "EOS"
        df = pyupbit.get_ohlcv("KRW-"+ticker, interval="minute5", count=200)
        if df.iloc[-2]['volume'] < df.iloc[-1]['volume'] :
            target_price = df.iloc[-2]['close'] + (df.iloc[-2]['high'] - df.iloc[-2]['low']) * 0.3
        else:
            target_price = 0

        close = df['close']
        ma5 = close.rolling(5).mean()
        ma20 = close.rolling(20).mean()
        ma60 = close.rolling(60).mean()
        ma120 = close.rolling(120).mean()
        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        macd = exp1-exp2
        exp3 = macd.ewm(span=9, adjust=False).mean()

        #print(df)
        #print('ma5:',ma5[-1], 'ma20:',ma20[-1],'ma60:',ma60[-1],'ma120:',ma120[-1])
        #print('MACD: ',macd[-1], 'Signal: ',exp3[-1])
        #print('MACD: ',macd[-2], 'Signal: ',exp3[-2])
    
        

        #잔고조회
        balances = upbit.get_balances()
        for b in balances:
            if b['currency'] == "KRW":
                krw = float(b['balance'])
            if b['currency'] == ticker:
                if b['balance'] is not None:
                    ticker_b = float(b['balance'])
                else:
                    ticker_b = 0
                if b['avg_buy_price'] is not None:
                    ticker_avg_buy = float(b['avg_buy_price'])
                else:
                    ticker_avg_buy = 0    
                       
        #분할매수
        if signal_buy == 0 :
            buy_1st = (krw*0.9995)*0.1
            buy_2nd = (krw*0.9995)*0.2
            buy_3rd = (krw*0.9995)*0.7
            phase_buy = 0
        
        current_price = get_current_price("KRW-"+ticker)
        
        if signal_buy != 0 : 
            #ror = current_price/ticker_avg_buy - 1

            if (macd[-2]>=80 and macd[-2] >= exp3[-2] and macd[-1] < exp3[-1]) or current_price > ticker_avg_buy*1.05  :
                upbit.sell_market_order("KRW-"+ticker, ticker_b)
                signal_buy = 0
                bot.sendMessage(mc, "sell +")
            elif current_price < ticker_avg_buy*0.97 :
                upbit.sell_market_order("KRW-"+ticker, ticker_b)
                bot.sendMessage(mc, "sell -")
                signal_buy = 0

        
        if (target_price < current_price) and (macd[-1] > exp3[-1]) and (krw > 5000):
            if (phase_buy == 2) and (ticker_avg_buy*0.98 > current_price) :
                upbit.buy_market_order("KRW-"+ticker, buy_3rd)
                bot.sendMessage(mc, "buy 3")
                phase_buy = 3
                    
            elif (phase_buy == 1) and (ticker_avg_buy*0.98 > current_price) :
                upbit.buy_market_order("KRW-"+ticker, buy_2nd)
                bot.sendMessage(mc, "buy 2")
                phase_buy = 2

            elif (phase_buy == 0)  :
                upbit.buy_market_order("KRW-"+ticker, buy_1st)
                bot.sendMessage(mc, "buy 1")
                phase_buy = 1
                signal_buy = 1
        #print(now,"current:",current_price,"target:",target_price,"avg:",ticker_avg_buy,"krw:",krw)
        time.sleep(0.5)
    except Exception as e:
        print(e)
        bot.sendMessage(mc, "error")
        time.sleep(0.5)
