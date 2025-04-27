# -*- coding: utf-8 -*-
"""
Author: jian wei
Create Time: 2025/4/25 10:42
File Name:gui.py
"""
# gui.py
# GUI界面模块，用于显示表单和与用户交互

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import threading
import os
import pyaudio
import wave
import io
from datetime import datetime


class FormAssistantGUI:
    def __init__(self, master, ai_model, speech_recognizer):
        """初始化GUI界面

        Args:
            master: tkinter主窗口
            ai_model: AI模型实例
            speech_recognizer: 语音识别模型实例
        """
        self.master = master
        self.ai_model = ai_model
        self.speech_recognizer = speech_recognizer

        # 窗口设置
        self.master.title("智能表单填写助手")
        self.master.geometry("2000x1400")
        self.master.configure(bg="#f0f0f0")

        # 表单变量
        self.current_form = None
        self.chat_history = []

        # 录音变量
        self.recording = False
        self.audio_frames = []
        self.audio_stream = None
        self.pyaudio_instance = None

        # 初始化界面
        self._init_ui()

        # 显示表单选择界面
        self._show_form_selection()

    def _init_ui(self):
        """初始化UI组件"""
        # 主容器
        self.main_frame = ttk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧表单选择面板
        self.left_frame = ttk.Frame(self.main_frame, width=200)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # 表单类型选择
        ttk.Label(self.left_frame, text="表单类型").pack(pady=(0, 5))
        self.form_type_var = tk.StringVar()
        self.form_type_combo = ttk.Combobox(self.left_frame, textvariable=self.form_type_var,
                                            values=["日报", "周报", "年报"])
        self.form_type_combo.pack(fill=tk.X, pady=5)
        self.form_type_combo.bind("<<ComboboxSelected>>", self._on_form_type_change)

        # 新建表单按钮
        self.new_form_btn = ttk.Button(self.left_frame, text="新建表单", command=self._create_new_form)
        self.new_form_btn.pack(fill=tk.X, pady=5)

        # 右侧主界面
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 聊天区域
        self.chat_frame = ttk.Frame(self.right_frame)
        self.chat_frame.pack(fill=tk.BOTH, expand=True)

        # 聊天历史
        self.chat_history_text = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, height=20)
        self.chat_history_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.chat_history_text.configure(state="disabled")

        # 表单预览
        self.form_preview_frame = ttk.LabelFrame(self.right_frame, text="当前表单内容")
        self.form_preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 使用Treeview组件创建表格
        self.form_preview_table = ttk.Treeview(self.form_preview_frame, columns=('字段', '值'), show='headings',
                                               height=20)
        self.form_preview_table.heading('字段', text='字段')
        self.form_preview_table.heading('值', text='值')
        self.form_preview_table.column('字段', width=150, anchor='w')
        self.form_preview_table.column('值', width=950, anchor='w')
        self.form_preview_table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 添加滚动条
        form_preview_scrollbar = ttk.Scrollbar(self.form_preview_frame, orient="vertical",
                                               command=self.form_preview_table.yview)
        self.form_preview_table.configure(yscrollcommand=form_preview_scrollbar.set)
        form_preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定双击事件来编辑表单
        self.form_preview_table.bind("<Double-1>", self._on_table_double_click)

        # 用户输入区
        self.input_frame = ttk.Frame(self.right_frame)
        self.input_frame.pack(fill=tk.X, pady=5)

        self.user_input = scrolledtext.ScrolledText(self.input_frame, wrap=tk.WORD, height=3)
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.user_input.bind("<Control-Return>", self._on_send)

        # 按钮区域
        self.buttons_frame = ttk.Frame(self.input_frame)
        self.buttons_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # 发送按钮
        self.send_btn = ttk.Button(self.buttons_frame, text="发送", command=self._on_send)
        self.send_btn.pack(fill=tk.X, pady=2)

        # 录音按钮
        self.record_btn = ttk.Button(self.buttons_frame, text="录音", command=self._toggle_recording)
        self.record_btn.pack(fill=tk.X, pady=2)

        # 提交表单按钮
        self.submit_btn = ttk.Button(self.buttons_frame, text="提交表单", command=self._submit_form)
        self.submit_btn.pack(fill=tk.X, pady=2)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪")
        self.status_bar = ttk.Label(self.master, textvariable=self.status_var, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)

    def _on_table_double_click(self, event):
        """处理表格双击事件，弹出编辑对话框"""
        # 获取点击的行
        item = self.form_preview_table.identify('item', event.x, event.y)
        if not item:
            return

        # 获取点击的列
        column = self.form_preview_table.identify('column', event.x, event.y)
        column_index = int(column.replace('#', '')) - 1  # 转换为索引

        # 如果点击的是值列（索引为1），则弹出编辑对话框
        if column_index == 1:
            # 获取当前行的字段名和值
            field_name = self.form_preview_table.item(item, 'values')[0]
            current_value = self.form_preview_table.item(item, 'values')[1]

            # 打开编辑对话框
            self._open_edit_dialog(item, field_name, current_value)

    def _open_edit_dialog(self, item, field_name, current_value):
        """打开编辑对话框"""
        # 创建对话框
        edit_dialog = tk.Toplevel(self.master)
        edit_dialog.title(f"编辑 {field_name}")
        edit_dialog.geometry("500x300")
        edit_dialog.transient(self.master)  # 设置为主窗口的子窗口
        edit_dialog.grab_set()  # 模态对话框

        # 创建文本框
        if field_name in ["今日工作内容", "工作成果", "遇到的问题", "本周工作总结", "年度工作总结", "项目回顾"]:
            # 对于这些可能需要多行输入的字段，使用Text组件
            edit_text = scrolledtext.ScrolledText(edit_dialog, wrap=tk.WORD, width=50, height=10)
            edit_text.insert("1.0", "" if current_value == "（未填写）" else current_value)
            edit_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        else:
            # 对于单行文本字段，使用Entry组件
            edit_var = tk.StringVar(value="" if current_value == "（未填写）" else current_value)
            edit_entry = ttk.Entry(edit_dialog, textvariable=edit_var, width=50)
            edit_entry.pack(fill=tk.X, padx=10, pady=10)

        # 按钮框
        button_frame = ttk.Frame(edit_dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        # 保存按钮
        def save_and_close():
            if "edit_text" in locals():
                new_value = edit_text.get("1.0", tk.END).strip()
            else:
                new_value = edit_var.get().strip()

            # 更新表格
            values = list(self.form_preview_table.item(item, 'values'))
            values[1] = new_value
            self.form_preview_table.item(item, values=values)

            # 更新表单对象
            if self.current_form:
                self.current_form.set_field_value(field_name, new_value)

            edit_dialog.destroy()

        save_btn = ttk.Button(button_frame, text="保存", command=save_and_close)
        save_btn.pack(side=tk.RIGHT, padx=5)

        # 取消按钮
        cancel_btn = ttk.Button(button_frame, text="取消", command=edit_dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

        # 设置默认焦点
        if "edit_entry" in locals():
            edit_entry.focus_set()
        else:
            edit_text.focus_set()

    def _show_form_selection(self):
        """显示表单选择界面"""
        self._append_ai_message("欢迎使用智能表单填写助手！请选择要填写的表单类型。")

    def _create_new_form(self):
        """创建新表单"""
        selected_type = self.form_type_var.get()
        if not selected_type:
            messagebox.showerror("错误", "请先选择表单类型")
            return

        # 导入forms模块
        from tkinter_version.forms import create_form

        # 创建表单
        self.current_form = create_form(selected_type)
        if not self.current_form:
            messagebox.showerror("错误", f"未能创建{selected_type}表单")
            return

        # 清空聊天历史
        self.chat_history = []
        self.chat_history_text.configure(state="normal")
        self.chat_history_text.delete("1.0", tk.END)
        self.chat_history_text.configure(state="disabled")

        # 显示欢迎信息
        welcome_msg = f"你好，我是一个表单助手，请你说出需要填写当前{selected_type}的内容，我会自动帮你整理出一个完整的表单"
        self._append_ai_message(welcome_msg)

        # 更新表单预览
        self._update_form_preview()

    def _on_form_type_change(self, event):
        """表单类型改变事件"""
        pass  # 仅选择，不立即创建

    def _update_form_preview(self):
        """更新表单预览为表格形式"""
        if not self.current_form:
            return

        # 清空现有表格
        for item in self.form_preview_table.get_children():
            self.form_preview_table.delete(item)

        # 添加表单字段
        for field in self.current_form.fields:
            value = field.value if field.value else "（未填写）"
            self.form_preview_table.insert('', 'end', values=(field.name, value))

        # 交替行颜色设置
        for i, item in enumerate(self.form_preview_table.get_children()):
            if i % 2 == 0:
                self.form_preview_table.item(item, tags=('even',))
            else:
                self.form_preview_table.item(item, tags=('odd',))

        # 设置行样式
        self.form_preview_table.tag_configure('even', background='#f0f0f0')
        self.form_preview_table.tag_configure('odd', background='#ffffff')

    def _append_user_message(self, message):
        """添加用户消息到聊天记录"""
        self.chat_history_text.configure(state="normal")
        self.chat_history_text.insert(tk.END, f"你: {message}\n\n")
        self.chat_history_text.see(tk.END)
        self.chat_history_text.configure(state="disabled")

        # 添加到聊天历史
        self.chat_history.append({"is_ai": False, "content": message})

    def _append_ai_message(self, message):
        """添加AI消息到聊天记录"""
        self.chat_history_text.configure(state="normal")
        self.chat_history_text.insert(tk.END, f"表单助手: {message}\n\n")
        self.chat_history_text.see(tk.END)
        self.chat_history_text.configure(state="disabled")

        # 添加到聊天历史
        self.chat_history.append({"is_ai": True, "content": message})

    def _on_send(self, event=None):
        """发送消息"""
        # 获取用户输入
        user_input = self.user_input.get("1.0", tk.END).strip()
        if not user_input:
            return

        # 检查是否有表单
        if not self.current_form:
            messagebox.showerror("错误", "请先创建一个表单")
            return

        # 清空输入框
        self.user_input.delete("1.0", tk.END)

        # 添加用户消息到聊天记录
        self._append_user_message(user_input)

        # 设置状态
        self.status_var.set("正在处理中...")

        # 创建线程处理AI响应
        threading.Thread(target=self._process_ai_response, args=(user_input,), daemon=True).start()

    def _process_ai_response(self, user_input):
        """处理AI响应"""
        try:
            # 解析用户输入
            result = self.ai_model.parse_form_input(self.current_form, user_input, self.chat_history)

            # 获取AI响应
            ai_response = result.get("response", "抱歉，处理您的输入时出错")

            # 更新表单预览
            self.master.after(0, self._update_form_preview)

            # 添加AI消息到聊天记录
            self.master.after(0, lambda: self._append_ai_message(ai_response))

            # 更新状态
            self.master.after(0, lambda: self.status_var.set("准备就绪"))
        except Exception as e:
            print(f"处理AI响应出错: {e}")
            self.master.after(0, lambda: self.status_var.set("处理出错"))
            self.master.after(0, lambda: self._append_ai_message(f"抱歉，处理您的输入时出错: {str(e)}"))

    def _toggle_recording(self):
        """切换录音状态"""
        if self.recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        """开始录音"""
        # 检查是否有表单
        if not self.current_form:
            messagebox.showerror("错误", "请先创建一个表单")
            return

        # 初始化PyAudio
        self.pyaudio_instance = pyaudio.PyAudio()

        # 设置录音参数
        sample_format = pyaudio.paInt16
        channels = 1
        rate = 16000
        chunk = 1024

        # 开始录音
        self.audio_stream = self.pyaudio_instance.open(
            format=sample_format,
            channels=channels,
            rate=rate,
            frames_per_buffer=chunk,
            input=True
        )

        self.audio_frames = []
        self.recording = True
        self.record_btn.configure(text="停止录音")
        self.status_var.set("正在录音...")

        # 创建线程记录音频
        threading.Thread(target=self._record_audio, args=(chunk,), daemon=True).start()

    def _record_audio(self, chunk):
        """记录音频"""
        while self.recording:
            data = self.audio_stream.read(chunk)
            self.audio_frames.append(data)

    def _stop_recording(self):
        """停止录音"""
        if not self.recording:
            return

        self.recording = False
        self.record_btn.configure(text="录音")
        self.status_var.set("处理录音中...")

        # 停止录音
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()

        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()

        # 处理录音数据
        self._process_recording()

    def _process_recording(self):
        """处理录音数据"""
        if not self.audio_frames:
            self.status_var.set("录音为空")
            return

        try:
            # 将录音数据转换为字节流
            audio_data = b''.join(self.audio_frames)

            # 将字节流写入内存文件
            audio_io = io.BytesIO()

            # 创建WAV文件
            wf = wave.open(audio_io, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16位采样
            wf.setframerate(16000)
            wf.writeframes(audio_data)
            wf.close()

            # 获取WAV文件数据
            audio_io.seek(0)
            wav_data = audio_io.read()

            # 使用语音识别模型转换为文本
            self.status_var.set("正在识别语音...")

            # 创建线程处理语音识别
            threading.Thread(target=self._process_speech_recognition, args=(wav_data,), daemon=True).start()

        except Exception as e:
            print(f"处理录音数据出错: {e}")
            self.status_var.set(f"处理录音数据出错: {str(e)}")

    def _process_speech_recognition(self, audio_data):
        """处理语音识别"""
        try:
            # 调用语音识别模型
            text = self.speech_recognizer.recognize(audio_data)

            # 更新状态
            self.master.after(0, lambda: self.status_var.set("语音识别完成"))

            # 如果识别到文本，添加到输入框
            if text:
                self.master.after(0, lambda: self.user_input.insert(tk.END, text))
                self.master.after(0, lambda: self.user_input.see(tk.END))
            else:
                self.master.after(0, lambda: self.status_var.set("未能识别语音内容"))
        except Exception as e:
            print(f"语音识别出错: {e}")
            self.master.after(0, lambda: self.status_var.set(f"语音识别出错: {str(e)}"))

    def _submit_form(self):
        """提交表单"""
        if not self.current_form:
            messagebox.showerror("错误", "没有表单可提交")
            return

        # 检查表单是否完整
        empty_fields = self.current_form.get_empty_fields()
        if empty_fields:
            field_names = [field.name for field in empty_fields]
            if messagebox.askyesno("表单未完整",
                                   f"以下字段尚未填写:\n{', '.join(field_names)}\n\n是否仍要提交表单?") == False:
                return

            # 导出表单
        try:
            # 创建导出目录
            export_dir = os.path.join(os.path.expanduser("~"), "表单助手")
            os.makedirs(export_dir, exist_ok=True)

            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.current_form.title}_{timestamp}.json"
            filepath = os.path.join(export_dir, filename)

            # 导出表单
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.current_form.to_dict(), f, ensure_ascii=False, indent=2)

            # 显示成功消息
            success_msg = f"表单已保存至: {filepath}"
            messagebox.showinfo("提交成功", success_msg)
            self._append_ai_message(f"表单已成功提交并保存。\n{success_msg}")

            # 询问是否创建新表单
            if messagebox.askyesno("创建新表单", "是否要创建一个新的表单?"):
                self._create_new_form()

        except Exception as e:
            print(f"提交表单出错: {e}")
            messagebox.showerror("提交失败", f"提交表单时出错: {str(e)}")
