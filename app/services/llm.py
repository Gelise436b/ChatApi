from openai import OpenAI
from app.config import API_KEY,MODEL


client = OpenAI(api_key=API_KEY,base_url="https://api.deepseek.com")

def ask_llm(messages:list[dict])->str:
    response = client.chat.completions.create(model = MODEL,messages = messages)

    answer = response.choices[0].message.content
    return answer


