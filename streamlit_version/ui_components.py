# -*- coding: utf-8 -*-
"""
Author: jian wei
Create Time: 2025/4/27 15:39
File Name:ui_components.py
"""
import streamlit as st
from typing import Dict, Any, List
from form_definitions import get_form_types, get_form_structure


def render_form_selector():
    """
    渲染表单类型选择界面
    """
    st.subheader("请选择要填写的表单类型")

    form_types = get_form_types()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("日报", use_container_width=True):
            st.session_state.form_type = "日报"
            st.rerun()

    with col2:
        if st.button("周报", use_container_width=True):
            st.session_state.form_type = "周报"
            st.rerun()

    with col3:
        if st.button("年报", use_container_width=True):
            st.session_state.form_type = "年报"
            st.rerun()

    st.markdown("""
    ### 使用说明

    1. 选择要填写的表单类型
    2. 在聊天框中描述您的工作内容
    3. AI将帮助您自动填写表单
    4. 检查并编辑表单内容
    5. 确认无误后提交表单

    **示例输入:**
    - "我今天完成了项目A的代码审查，解决了5个bug，明天计划开始新功能开发"
    - "本周我主要负责客户支持工作，解决了12个客户投诉，下周将进行团队培训"
    """)


def render_welcome_message(form_type: str) -> str:
    """
    根据表单类型生成欢迎消息
    """
    messages = {
        "日报": "你好！我是你的表单填写助手。请告诉我今天的工作内容，我会帮你整理成一份完整的日报。\n\n你可以这样描述：'今天我完成了XX项目的开发，解决了几个问题...'",
        "周报": "你好！我是你的表单填写助手。请告诉我本周的工作内容和成果，我会帮你整理成一份完整的周报。\n\n你可以这样描述：'本周我主要负责了XX项目，完成了哪些任务，遇到了什么问题...'",
        "年报": "你好！我是你的表单填写助手。请告诉我今年的工作成果、项目完成情况和未来规划，我会帮你整理成一份完整的年报。\n\n你可以分多次告诉我不同部分的内容，我会逐步完善你的年报。"
    }

    return messages.get(form_type, "你好！我是你的表单填写助手。请告诉我需要填写的内容，我会帮你整理成一份完整的表单。")


def render_editable_form(form_structure: Dict[str, str], form_data: Dict[str, str], time_info: Dict[str, str]):
    """
    渲染可编辑的表单
    """
    with st.form(key="editable_form"):
        # 显示时间相关信息
        if "日报" in st.session_state.form_type:
            form_data["日期"] = time_info["date"]
        elif "周报" in st.session_state.form_type:
            form_data["周次"] = time_info["week"]
            form_data["开始日期"] = time_info["week_start"]
            form_data["结束日期"] = time_info["week_end"]
        elif "年报" in st.session_state.form_type:
            form_data["年份"] = time_info["year"]

        # 显示并允许编辑表单字段
        edited_form_data = {}
        for field in form_structure:
            if "日期" in field or "周次" in field or "年份" in field or "开始日期" in field or "结束日期" in field:
                # 时间相关字段不允许编辑
                st.text_input(field, value=form_data.get(field, ""), disabled=True, key=f"field_{field}")
                edited_form_data[field] = form_data.get(field, "")
            elif "总结" in field or "内容" in field or "成果" in field or "计划" in field:
                # 长文本字段使用文本区域
                edited_form_data[field] = st.text_area(
                    field,
                    value=form_data.get(field, ""),
                    height=100,
                    key=f"field_{field}"
                )
            else:
                # 普通文本字段
                edited_form_data[field] = st.text_input(
                    field,
                    value=form_data.get(field, ""),
                    key=f"field_{field}"
                )

        # 更新表单数据
        for key, value in edited_form_data.items():
            st.session_state.form_data[key] = value

        # 提交按钮
        submitted = st.form_submit_button("提交表单")

        return submitted