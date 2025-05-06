# -*- coding: utf-8 -*-
"""
Author: jian wei
Create Time: 2025/4/27 15:39
File Name:ui_components.py
"""
import streamlit as st
from typing import Dict, Any, List
from form_definitions import get_form_types, get_form_structure
from speech_recognition import speech_to_text_widget


def render_project_selector():
    """
    渲染项目选择界面
    """
    st.subheader(f"您已选择 {st.session_state.form_type}，请选择项目")

    # 搜索框
    search_query = st.text_input("输入项目关键词搜索", key="project_search")

    if search_query:
        # 执行模糊搜索
        from project_management import search_projects
        search_results = search_projects(search_query, st.session_state.projects_list)

        if search_results:
            st.write("搜索结果:")

            # 显示搜索结果按钮
            cols = st.columns(min(len(search_results), 3))
            for i, project in enumerate(search_results):
                with cols[i % 3]:
                    if st.button(project, key=f"proj_{i}", use_container_width=True):
                        st.session_state.project = project
                        st.rerun()
        else:
            st.info("未找到匹配的项目，请尝试其他关键词")
    # 添加返回表单选择的按钮
    st.markdown("---")
    if st.button("返回表单选择", key="back_to_form"):
        st.session_state.form_type = None
        st.rerun()


# 2. 修改表单选择器，只显示日报和周报
def render_form_selector():
    """
    渲染表单类型选择界面
    """
    st.subheader(f"当前项目: {st.session_state.project}")
    st.subheader("请选择要填写的表单类型")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("日报", use_container_width=True):
            st.session_state.form_type = "日报"
            st.rerun()

    with col2:
        if st.button("周报", use_container_width=True):
            st.session_state.form_type = "周报"
            st.rerun()

    st.markdown("""
    ### 使用说明

    1. 选择要填写的表单类型
    2. 在聊天框中描述您的工作内容或使用语音输入
    3. AI将帮助您自动填写表单
    4. 检查并编辑表单内容
    5. 确认无误后提交表单

    **示例输入:**
    - "我今天完成了项目A的代码审查，解决了5个bug，明天计划开始新功能开发"
    - "本周我主要负责客户支持工作，解决了12个客户投诉，下周将进行团队培训"
    """)


# 3. 修改欢迎消息以包含项目信息
def render_welcome_message(form_type: str) -> str:
    """
    根据表单类型生成欢迎消息
    """
    project = st.session_state.project
    messages = {
        "日报": f"你好！我是你的{form_type}填写助手。请告诉我今天在「{project}」项目上的工作内容，我会帮你整理成一份完整的日报。\n\n你可以这样描述：'今天我完成了XX功能的开发，解决了几个问题...'或者使用语音输入功能。",
        "周报": f"你好！我是你的{form_type}填写助手。请告诉我本周在「{project}」项目上的工作内容和成果，我会帮你整理成一份完整的周报。\n\n你可以这样描述：'本周我主要负责了XX模块，完成了哪些任务，遇到了什么问题...'或者使用语音输入功能。"
    }

    return messages.get(form_type,
                        f"你好！我是你的{form_type}填写助手。请告诉我在「{project}」项目上需要填写的内容，我会帮你整理成一份完整的表单。你可以文字输入或语音输入。")


def render_chat_input_area():
    """
    渲染包含语音输入功能的聊天输入区域
    """
    # 使用选项卡分隔文字输入和语音输入
    tab1, tab2 = st.tabs(["文字输入", "语音输入"])

    user_input = None

    with tab1:
        # 普通文字输入
        text_input = st.chat_input("请描述您要填写的内容...", key="text_chat_input")
        if text_input:
            user_input = text_input

    with tab2:
        # 语音输入
        speech_text = speech_to_text_widget()

        # 如果有识别结果，显示可编辑的文本区域
        if speech_text or st.session_state.speech_text:
            # 使用可编辑的文本区域让用户修改识别结果
            edited_text = st.text_area(
                "识别结果",
                value=speech_text or st.session_state.speech_text,
                height=100,
                key="editable_speech_text"
            )

            # 更新session state中的语音文本为编辑后的文本
            st.session_state.speech_text = edited_text

            col1, col2 = st.columns(2)
            with col1:
                if st.button("发送", key="send_speech"):
                    if edited_text.strip():  # 确保文本不为空
                        user_input = edited_text
            with col2:
                if st.button("清除", key="clear_speech"):
                    st.session_state.speech_text = ""
                    st.rerun()

    return user_input


def render_editable_form(form_structure: Dict[str, str], form_data: Dict[str, str], time_info: Dict[str, str]):
    """
    渲染可编辑的表单
    """
    with st.form(key="editable_form"):
        # 显示项目信息
        st.write(f"**当前项目:** {st.session_state.project}")
        # 显示时间相关信息
        if "日报" in st.session_state.form_type:
            form_data["日期"] = time_info["date"]
        elif "周报" in st.session_state.form_type:
            form_data["周次"] = time_info["week"]
            form_data["开始日期"] = time_info["week_start"]
            form_data["结束日期"] = time_info["week_end"]

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
