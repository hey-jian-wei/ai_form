# -*- coding: utf-8 -*-
"""
Author: jian wei
Create Time: 2025/4/25 10:44
File Name:main.py
"""
# main.py
# 主程序，用于启动应用

import tkinter as tk
import os
import sys


def resource_path(relative_path):
    """获取资源绝对路径，兼容开发环境和打包后的环境"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(".."), relative_path)


def main():
    """主函数"""
    # 设置API密钥
    api_key = os.environ.get("OPENAI_API_KEY", "sk-rmXrDwDncONSn8TQ91A1E544Bd85433d98A2300319D19823")
    if not api_key:
        print("警告: 未设置OPENAI_API_KEY环境变量，请在启动应用前设置")
        print("可以通过以下命令设置（Windows CMD）: set OPENAI_API_KEY=您的API密钥")
        print("或者（Linux/Mac）: export OPENAI_API_KEY=您的API密钥")

    # 导入模块
    from tkinter_version.ai_model import AIModel
    from speech_recognition import SpeechRecognizer
    from tkinter_version.gui import FormAssistantGUI

    # 初始化模型
    print("正在初始化AI模型...")
    ai_model = AIModel(api_key)

    print("正在初始化语音识别模型...")
    # 检测是否有CUDA可用
    try:
        import torch
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
    except:
        device = "cpu"
    speech_recognizer = SpeechRecognizer(device=device)

    # 创建GUI
    print("正在启动GUI界面...")
    root = tk.Tk()

    # 设置应用图标（如果存在）
    icon_path = resource_path("icon.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)

    # 创建应用实例
    app = FormAssistantGUI(root, ai_model, speech_recognizer)

    # 运行主循环
    root.mainloop()


if __name__ == "__main__":
    main()
