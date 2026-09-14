"""
阶段0 · 调通大模型（DeepSeek，走 OpenAI 兼容接口）
先让它能【脱离 FastAPI 独立跑】：在 chatapi 目录运行   python services/llm.py

你要填下面 4 处 TODO（每处做什么，见对话里教你的 4 步）。
别翻我的答案抄——照理解自己敲，跑通才算会。
"""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 把 .env 里的 DEEPSEEK_API_KEY 读进环境变量


# TODO 1：造客户端
#   用 OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
client = OpenAI(api_key = os.getenv("DEEPSEEK_API_KEY"),base_url = "https://api.deepseek.com" )


def ask_llm(user_message: str) -> str:
    """发一句话给模型，拿回它的回答字符串。"""
    # TODO 2：调 client.chat.completions.create(...)
    #   model="deepseek-chat"，messages=[{"role": "user", "content": user_message}]
    # 你写（把返回结果存进一个变量 resp）
    response = client.chat.completions.create(model="deepseek-chat",messages=[{"role":"user","content":user_message}])
   

    # TODO 3：从 resp 里取回答文本（提示：resp.choices[0].message.content）
    answer = response.choices[0].message.content  # 你写
    return answer


if __name__ == "__main__":
    # TODO 4：调用 ask_llm("用一句话解释什么是 API")，把返回值 print 出来
    result = ask_llm("用一句话解释什么是API") # 你写
    print(result)
