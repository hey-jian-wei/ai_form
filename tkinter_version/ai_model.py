# -*- coding: utf-8 -*-
"""
Author: jian wei
Create Time: 2025/4/25 10:41
File Name:ai_model.py
"""
# ai_model.py
# 大模型接口，用于解析用户输入并填写表单

import os
from openai import OpenAI
import json
import re


class AIModel:
    def __init__(self, api_key=None):
        """初始化大模型接口

        Args:
            api_key: OpenAI API密钥，如果为None则从环境变量获取
        """
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")

        self.client = OpenAI(api_key=api_key,base_url="https://xiaoai.plus/v1")
        self.model = "gpt-4o"

    def parse_form_input(self, form, user_input, chat_history=[]):
        """解析用户输入并填写表单

        Args:
            form: 表单对象
            user_input: 用户输入的文本
            chat_history: 聊天历史

        Returns:
            dict: 包含填写结果的字典
        """
        # 构建表单字段信息
        fields_info = []
        for field in form.fields:
            fields_info.append({
                "name": field.name,
                "description": field.description,
                "current_value": field.value
            })

        # 构建提示信息
        prompt = f"""
        你是一个智能表单助手，需要帮助用户填写"{form.title}"。

        表单字段如下：
        {json.dumps(fields_info, ensure_ascii=False, indent=2)}

        用户的输入是："{user_input}"

        请分析用户输入，提取相关信息填入表单。对于用户没有提及的字段，请保持原值。
        返回JSON格式，包含以下内容：
        1. updated_fields: 更新的字段列表，每个字段包含name和value
        2. missing_fields: 仍然为空的字段列表
        3. response: 对用户的回复，告知已填写的内容和缺少的内容

        示例返回：
        {{"updated_fields": [{{"name": "日期", "value": "2025-04-25"}}], "missing_fields": ["今日工作内容", "工作成果"], "response": "我已帮你填写了日期，还需要填写今日工作内容和工作成果。"}}
        """

        # 构建消息历史
        messages = []
        for msg in chat_history:
            role = "assistant" if msg["is_ai"] else "user"
            messages.append({"role": role, "content": msg["content"]})

        # 添加当前提示
        messages.append({"role": "user", "content": prompt})

        try:
            # 调用大模型API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"}
            )

            # 解析响应
            result = json.loads(response.choices[0].message.content)

            # 更新表单字段
            if "updated_fields" in result:
                for field_update in result["updated_fields"]:
                    field_name = field_update.get("name")
                    field_value = field_update.get("value")
                    if field_name and field_value:
                        form.set_field_value(field_name, field_value)

            return result
        except Exception as e:
            print(f"调用大模型API出错: {e}")
            return {
                "updated_fields": [],
                "missing_fields": [field.name for field in form.get_empty_fields()],
                "response": f"抱歉，处理您的输入时出错: {str(e)}"
            }

    def get_form_summary(self, form):
        """获取表单摘要

        Args:
            form: 表单对象

        Returns:
            str: 表单摘要
        """
        fields_text = []
        for field in form.fields:
            value = field.value if field.value else "（未填写）"
            fields_text.append(f"{field.name}: {value}")

        return "\n".join(fields_text)