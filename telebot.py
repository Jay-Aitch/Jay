import telepot # telepot 모듈 import 
token = "" # 봇 API 입력 
# mc = "" # 텔레그램 숫자 ID 입력 
mc = ""
bot = telepot.Bot(token) 
bot.sendMessage(mc, "test") # 할말 적어서 메시지 보내기 
