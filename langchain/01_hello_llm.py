'''
langchain/01_hello_llm.py
----------------------------
가장 단순한 호출 - 프롬프트 템플릿 없이 문자열 하나로 바로 질문

이 파일의 목적
- Langchain을 통해 모델을 직접 부르면 어떤 모습인지 확인
- .invoke() --> 질문을 보내고 응답을 받는다.
'''
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(model='gemini-3.6-flash',api_key=os.getenv("GOOGLE_API_KEY"))


response = llm.invoke('우울해 위로해줘')
print(response)