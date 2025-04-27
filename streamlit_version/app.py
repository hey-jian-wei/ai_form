# -*- coding: utf-8 -*-
"""
Author: jian wei
Create Time: 2025/4/27 16:45
File Name: app.py
"""
import streamlit as st

from form_definitions import get_form_structure
from ai_interface import get_ai_completion
from ui_components import (
    render_form_selector,
    render_editable_form,
    render_welcome_message,
    render_chat_input_area
)
from utils import parse_ai_response, get_current_time_info


def main():
    st.set_page_config(page_title="智能表单填写助手", layout="wide")
    st.title("智能表单填写助手")

    # 初始化会话状态
    if "form_type" not in st.session_state:
        st.session_state.form_type = None
    if "form_data" not in st.session_state:
        st.session_state.form_data = {}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False
    if "first_message_sent" not in st.session_state:
        st.session_state.first_message_sent = False
    if "speech_text" not in st.session_state:
        st.session_state.speech_text = ""
    if "use_gpu" not in st.session_state:
        st.session_state.use_gpu = False
    if "recording_status" not in st.session_state:
        st.session_state.recording_status = "ready"

    # 获取当前时间信息
    time_info = get_current_time_info()

    # 如果表单类型未选择，显示选择界面
    if st.session_state.form_type is None:
        render_form_selector()
        return

    # 如果表单已提交，显示成功信息
    if st.session_state.form_submitted:
        st.success(f"{st.session_state.form_type}已成功提交！")
        if st.button("填写新表单"):
            st.session_state.form_type = None
            st.session_state.form_data = {}
            st.session_state.chat_history = []
            st.session_state.form_submitted = False
            st.session_state.first_message_sent = False
            st.session_state.speech_text = ""
            st.session_state.recording_status = "ready"
            st.rerun()
        return

    # 获取表单结构
    form_structure = get_form_structure(st.session_state.form_type)

    # 预填充时间相关字段
    if "日报" in st.session_state.form_type:
        st.session_state.form_data["日期"] = time_info["date"]
    elif "周报" in st.session_state.form_type:
        st.session_state.form_data["周次"] = time_info["week"]
        st.session_state.form_data["开始日期"] = time_info["week_start"]
        st.session_state.form_data["结束日期"] = time_info["week_end"]
    elif "年报" in st.session_state.form_type:
        st.session_state.form_data["年份"] = time_info["year"]

    # 分栏布局
    col1, col2 = st.columns([3, 2])

    # 聊天界面
    with col1:
        st.subheader("表单助手聊天")

        # 显示聊天历史
        chat_container = st.container()
        with chat_container:
            # 如果是首次进入该表单且没有发送过欢迎消息
            if not st.session_state.first_message_sent:
                welcome_message = render_welcome_message(st.session_state.form_type)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": welcome_message
                })
                st.session_state.first_message_sent = True

            # 显示所有聊天记录
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.chat_message("user").write(message["content"])
                else:
                    st.chat_message("assistant").write(message["content"])

        # 用户输入区域（文字输入和语音输入）
        user_input = render_chat_input_area()

        if user_input:
            # 显示用户消息
            st.chat_message("user").write(user_input)

            # 将用户输入添加到聊天历史
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # 构建 AI 提示
            prompt = f"""
            当前表单类型: {st.session_state.form_type}
            当前时间信息: {time_info}
            表单结构: {form_structure}
            当前已填写内容: {st.session_state.form_data}

            用户输入: {user_input}

            请解析用户输入并更新表单内容。返回一个JSON格式的表单内容，包含所有字段。
            只需返回JSON内容，不要有其他说明文字。确保所有字段都包含在JSON中，即使某些字段没有值。
            """

            # 获取AI回复
            with st.spinner("AI正在处理..."):
                ai_response = get_ai_completion(prompt)

            # 解析AI回复，更新表单数据
            try:
                form_data = parse_ai_response(ai_response)
                # 更新表单数据，保留已有数据和时间字段
                for key, value in form_data.items():
                    if key in form_structure and value:
                        st.session_state.form_data[key] = value

                # 检查哪些字段尚未填写
                empty_fields = [field for field in form_structure if
                                not st.session_state.form_data.get(field, "") and not (
                                        "日期" in field or "周次" in field or "年份" in field or "开始日期" in field or "结束日期" in field
                                )]

                # 生成AI回复内容
                ai_reply = "我已根据您的描述更新了表单内容。\n\n"

                # 如果还有未填写的字段，提示用户
                if empty_fields:
                    ai_reply += f"以下字段尚未填写：\n- " + "\n- ".join(empty_fields) + "\n\n"
                    ai_reply += "您可以继续描述相关内容，或者在右侧表单中直接填写。\n"
                else:
                    ai_reply += "所有字段都已填写完成！您可以检查右侧表单并提交，或者告诉我需要修改的地方。\n"

                # 添加AI回复到聊天历史
                st.chat_message("assistant").write(ai_reply)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": ai_reply
                })

                # 清除语音识别结果
                st.session_state.speech_text = ""

                # 重新加载页面以更新UI
                st.rerun()

            except Exception as e:
                error_message = f"抱歉，处理您的输入时出现了问题: {str(e)}。请重试或使用不同的描述方式。"
                st.chat_message("assistant").write(error_message)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_message
                })

    # 表单预览和编辑界面
    with col2:
        st.subheader(f"当前表单: {st.session_state.form_type}")

        # 渲染可编辑表单
        submitted = render_editable_form(form_structure, st.session_state.form_data, time_info)
        if submitted:
            # 在实际应用中，这里可以添加保存表单数据到数据库的代码
            st.session_state.form_submitted = True
            st.rerun()


if __name__ == "__main__":
    main()