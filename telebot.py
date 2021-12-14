import telepot # telepot 모듈 import 
token = "5069562183:AAHVCjQit7rWLHii2wUjOu3q_9T1MbuwQzE" # 봇 API 입력 
# mc = "454439308" # 텔레그램 숫자 ID 입력 
mc = "-771094944"
bot = telepot.Bot(token) 
bot.sendMessage(mc, "test") # 할말 적어서 메시지 보내기 