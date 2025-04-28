# -*- coding: utf-8 -*-
"""
Author: jian wei
Create Time: 2025/4/27 15:38
File Name:ai_interface.py
"""
import os
import json
import streamlit as st
from openai import OpenAI
from typing import Dict, Any, List


# 尝试获取API密钥，如果不存在，则使用示例模式
def get_api_key():
    api_key = os.environ.get("OPENAI_API_KEY","sk-rmXrDwDncONSn8TQ91A1E544Bd85433d98A2300319D19823") or st.secrets.get("OPENAI_API_KEY", None)

    if not api_key:
        if "api_key" not in st.session_state:
            st.session_state.api_key = None

        if st.session_state.api_key is None:
            api_key = st.sidebar.text_input("请输入您的OpenAI API密钥:", type="password")
            if api_key:
                st.session_state.api_key = api_key
        else:
            api_key = st.session_state.api_key

    return api_key


def get_ai_completion(prompt: str) -> str:
    """
    使用OpenAI SDK调用AI接口获取完成结果
    """
    api_key = get_api_key()

    # 如果没有API密钥，则使用示例模式
    if not api_key:
        return simulate_ai_response(prompt)

    try:
        # 初始化OpenAI客户端
        client = OpenAI(api_key=api_key,base_url="https://xiaoai.plus/v1")

        # 创建聊天完成请求
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """你是一个专业的表单填写助手。你的任务是解析用户输入，并根据表单结构生成JSON格式的表单内容。
                    仅返回JSON格式数据，不要有其他解释或说明。确保所有字段都包含在JSON中，即使某些字段没有值。用户可能会发送一些错别字，你需要自己鉴别做适当的修改和语义调整"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )
        print(prompt)
        print("-"*50)
        print(response.choices[0].message.content)

        # 返回AI回复的内容
        return response.choices[0].message.content

    except Exception as e:
        st.error(f"调用AI接口时出错: {str(e)}")
        return simulate_ai_response(prompt)


def simulate_ai_response(prompt: str) -> str:
    """
    模拟AI响应（当API密钥不可用时使用）
    """
    # 解析提示中的表单类型和用户输入
    form_type = None
    form_structure = {}
    user_input = ""

    for line in prompt.split("\n"):
        line = line.strip()
        if "当前表单类型:" in line:
            form_type = line.split("当前表单类型:")[1].strip()
        elif "表单结构:" in line:
            try:
                form_structure_str = line.split("表单结构:")[1].strip()
                form_structure = json.loads(form_structure_str.replace("'", '"'))
            except:
                pass
        elif "用户输入:" in line:
            user_input = line.split("用户输入:")[1].strip()

    # 根据表单类型和用户输入生成模拟回复
    if not form_structure:
        from form_definitions import get_form_structure
        form_structure = get_form_structure(form_type)

    # 分析用户输入并填充相关字段
    result = {}
    for field in form_structure:
        result[field] = form_structure[field]

        # 根据用户输入填充可能相关的字段
        if "姓名" in field and "我是" in user_input:
            parts = user_input.split("我是")
            if len(parts) > 1:
                name_part = parts[1].split()[0]
                result[field] = name_part

        elif "部门" in field and "部门" in user_input:
            parts = user_input.split("部门")
            if len(parts) > 1:
                dept_part = parts[1].strip().split()[0]
                result[field] = dept_part

        elif any(k in field.lower() for k in ["工作内容", "工作总结", "成果"]) and any(
                k in user_input for k in ["完成", "做了", "工作"]):
            result[field] = "根据用户输入提取的工作内容"

        elif any(k in field.lower() for k in ["问题", "困难", "挑战"]) and any(
                k in user_input for k in ["问题", "困难", "卡住"]):
            result[field] = "根据用户输入提取的问题内容"

        elif any(k in field.lower() for k in ["计划", "目标"]) and any(
                k in user_input for k in ["计划", "准备", "明天"]):
            result[field] = "根据用户输入提取的计划内容"

    return json.dumps(result, ensure_ascii=False)