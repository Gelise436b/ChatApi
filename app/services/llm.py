from openai import OpenAI
from app.config import API_KEY,MODEL


client = OpenAI(api_key=API_KEY,base_url="https://api.deepseek.com")

def ask_llm(messages:list[dict])->str:
    response = client.chat.completions.create(model = MODEL,messages = messages)

    answer = response.choices[0].message.content
    return answer

def ask_llm_stream(messages:list[dict]):
    stream = client.chat.completions.create(model = MODEL,messages=messages,stream=True)
    for chunk in stream:
        piece = chunk.choices[0].delta.content   # ⚠️❌ 流式里是 .delta.content，不是 .messages（实测 AttributeError: 'ChoiceDelta' object has no attribute 'messages'）
        if piece:
            yield piece

    

