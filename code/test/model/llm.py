from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv
import os

load_dotenv()


DEEPSEEK_KEY = os.getenv('DEEPSEEK_KEY')
DEEPSEEK_URL = os.getenv('DEEPSEEK_URL')



llm = ChatDeepSeek(
    model="deepseek-chat",
    base_url=DEEPSEEK_URL,
    api_key=DEEPSEEK_KEY
)


#response = llm.invoke("请介绍下自己")
#print (response)