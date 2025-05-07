# -*- coding: utf-8 -*-
"""
Author: jian wei
Create Time: 2025/4/27 15:38
File Name:ai_interface.py
"""
import os
import time
import streamlit as st
from abc import ABC, abstractmethod
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class LLM(ABC):
    @abstractmethod
    def chat(self, prompt, temperature=0, system='', stop=None):
        pass

    async def a_chat(self, prompt, temperature=0, system='', stop=None):
        pass

    def stream_chat(self, prompt, temperature=0, system='', stop=None):
        pass

    async def a_stream_chat(self, prompt, temperature=0, system='', stop=None):
        pass


class AzureAiLLM(LLM):
    def __init__(self, base_url, api_key, model):
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model

    def chat(self, prompt, temperature=0.8, system='', stop=None):
        if system:
            messages = [SystemMessage(content=system), UserMessage(content=prompt)]
        else:
            messages = [UserMessage(content=prompt)]

        client = ChatCompletionsClient(endpoint=self.base_url, credential=AzureKeyCredential(self.api_key))
        for i in range(10):
            try:
                response = client.complete(
                    messages=messages,
                    model=self.model_name,
                    temperature=temperature,
                    stop=stop,
                    timeout=60 * 10
                )
                print(response.choices[0].message.content)
                if response.choices[0].message.content:
                    # 去除掉<think> </think>包裹的内容，只要</think>后面的内容
                    content = response.choices[0].message.content.split('</think>')[1]
                    return content
                else:
                    print("response.choices[0].message.content is None")
                    time.sleep(20)
                    continue
            except Exception as e:
                print(f"Attempt {i + 1} failed with error: {e}")
                time.sleep(20)

        print("All attempts failed.")
        return None

    async def a_chat(self, prompt, temperature=0.8, system='', stop=None):
        if system:
            messages = [SystemMessage(content=system), UserMessage(content=prompt)]
        else:
            messages = [UserMessage(content=prompt)]
        from azure.ai.inference.aio import ChatCompletionsClient
        for i in range(10):
            try:
                async with ChatCompletionsClient(endpoint=self.base_url,
                                                 credential=AzureKeyCredential(self.api_key)) as client:
                    response = await client.complete(
                        messages=messages,
                        model=self.model_name,
                        temperature=temperature,
                        stop=stop
                    )
                    # print(response.choices[0].message.content)
                    if response.choices[0].message.content:
                        content = response.choices[0].message.content
                        return content
                    else:
                        print("response.choices[0].message.content is None")
                        continue
            except Exception as e:
                print(f"Attempt {i + 1} failed with error: {e}")
                time.sleep(10)
        print("All attempts failed.")
        return None

    def stream_chat(self, prompt, temperature=0, system='', stop=None):
        if system:
            messages = [SystemMessage(content=system), UserMessage(content=prompt)]
        else:
            messages = [UserMessage(content=prompt)]
        client = ChatCompletionsClient(endpoint=self.base_url, credential=AzureKeyCredential(self.api_key))
        for i in range(10):
            try:
                response = client.complete(
                    messages=messages,
                    model=self.model_name,
                    temperature=temperature,
                    stop=stop,
                    stream=True
                )
                return response
            except Exception as e:
                print(f"Attempt {i + 1} failed with error: {e}")
                time.sleep(10)
        print("All attempts failed.")
        return None


def get_ai_completion(prompt: str) -> str:
    deepseek_azure_ai_config = {
        'api_key': os.getenv("AZURE_AI_DEEPSEEK_R1_API_KEY"),
        'model': os.getenv("AZURE_AI_DEEPSEEK_R1_MODEL"),
        'base_url': os.getenv("AZURE_AI_DEEPSEEK_R1_BASE_URL")
    }

    try:
        # 初始化OpenAI客户端
        # deepseek_azure = AzureAiLLM(**deepseek_azure_ai_config)
        client = OpenAI(api_key="sk-rmXrDwDncONSn8TQ91A1E544Bd85433d98A2300319D19823", base_url="https://xiaoai.plus/v1")
        system = """"
你是一个专业的表单填写助手。你的任务是解析用户输入，并根据表单结构生成JSON格式的表单内容。
仅返回JSON格式数据，不要有其他解释或说明。确保所有字段都包含在JSON中，即使某些字段没有值。用户可能会发送一些错别字，你需要自己鉴别做适当的修改和语义调整
"""
        # 创建聊天完成请求
        # response = deepseek_azure.chat(system=system,prompt=prompt)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )
        response = response.choices[0].message.content
        print(prompt)
        print("-" * 50)
        print(response)
        return response

    except Exception as e:
        st.error(f"调用AI接口时出错: {str(e)}")
