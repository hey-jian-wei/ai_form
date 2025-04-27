# -*- coding: utf-8 -*-
"""
Author: jian wei
Create Time: 2025/4/27 15:39
File Name:utils.py
"""
import json
from datetime import datetime, timedelta
from typing import Dict, Any


def parse_ai_response(response: str) -> Dict[str, str]:
    """
    解析AI回复，提取JSON数据
    """
    try:
        # 尝试直接解析整个响应
        return json.loads(response)
    except json.JSONDecodeError:
        # 如果失败，尝试提取JSON部分
        try:
            # 查找可能的JSON部分（在```json和```之间，或者在{和}之间）
            if "```json" in response:
                json_part = response.split("```json")[1].split("```")[0].strip()
                return json.loads(json_part)
            elif "```" in response and "{" in response and "}" in response:
                json_part = response.split("```")[1].split("```")[0].strip()
                return json.loads(json_part)
            elif "{" in response and "}" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_part = response[json_start:json_end]
                return json.loads(json_part)
            else:
                return {}
        except Exception as e:
            print(f"解析JSON时出错: {str(e)}")
            return {}


def get_current_time_info() -> Dict[str, str]:
    """
    获取当前时间信息，包括日期、周次、年份等
    """
    now = datetime.now()

    # 计算当前周的开始和结束日期
    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=6)

    # 计算当前是第几周
    week_number = now.isocalendar()[1]

    return {
        "date": now.strftime("%Y-%m-%d"),
        "year": now.strftime("%Y"),
        "month": now.strftime("%m"),
        "day": now.strftime("%d"),
        "week": f"{now.year}年第{week_number}周",
        "week_start": week_start.strftime("%Y-%m-%d"),
        "week_end": week_end.strftime("%Y-%m-%d"),
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
    }


def format_chat_history(chat_history):
    """
    格式化聊天历史为适合AI输入的格式
    """
    formatted = []
    for message in chat_history:
        formatted.append({
            "role": message["role"],
            "content": message["content"]
        })
    return formatted