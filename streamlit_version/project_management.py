# -*- coding: utf-8 -*-
"""
Author: jian wei
Create Time: 2025/5/06
File Name: project_management.py
"""
import pandas as pd
import streamlit as st
import os
from fuzzywuzzy import process


def load_projects_from_excel(excel_path=None):
    """
    从Excel文件加载项目列表
    如果没有指定文件路径，则返回默认项目列表（仅用于测试）
    """
    try:
        if excel_path and os.path.exists(excel_path):
            df = pd.read_excel(excel_path)
            # 假设Excel有一个名为"项目名称"的列
            if "项目名称" in df.columns:
                projects = df["项目名称"].tolist()
                return projects
            else:
                st.warning("Excel文件中未找到'项目名称'列，请检查格式")
                return get_default_projects()
        else:
            return get_default_projects()
    except Exception as e:
        st.error(f"加载项目列表时出错: {str(e)}")
        return get_default_projects()


def get_default_projects():
    """
    返回默认项目列表（当无法从Excel加载时使用）
    """
    return [
        "智能客服系统开发",
        "企业数据中台建设",
        "移动应用性能优化",
        "网络安全防护升级",
        "大数据分析平台",
        "云原生应用迁移",
        "人工智能算法研发",
        "微服务架构重构",
        "区块链溯源系统",
        "物联网设备管理"
    ]


def search_projects(query, projects_list, limit=6):
    """
    使用模糊匹配搜索项目列表，返回最相关的项目
    """
    if not query or len(query) < 2:
        return []

    # 使用fuzzywuzzy进行模糊匹配
    matches = process.extract(query, projects_list, limit=limit)
    return [match[0] for match in matches]