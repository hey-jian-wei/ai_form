# -*- coding: utf-8 -*-
"""
Author: jian wei
Create Time: 2025/4/25 10:40
File Name:forms.py
"""


# forms.py
# 表单定义，包含各种表单类型和字段

class FormField:
    """表单字段类"""

    def __init__(self, name, description="", value=""):
        self.name = name
        self.description = description
        self.value = value

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "value": self.value
        }


class Form:
    """表单基类"""

    def __init__(self, title, description=""):
        self.title = title
        self.description = description
        self.fields = []

    def add_field(self, name, description=""):
        """添加表单字段"""
        self.fields.append(FormField(name, description))

    def get_field(self, name):
        """获取表单字段"""
        for field in self.fields:
            if field.name == name:
                return field
        return None

    def set_field_value(self, name, value):
        """设置表单字段的值"""
        field = self.get_field(name)
        if field:
            field.value = value
            return True
        return False

    def to_dict(self):
        """将表单转换为字典"""
        return {
            "title": self.title,
            "description": self.description,
            "fields": [field.to_dict() for field in self.fields]
        }

    def get_empty_fields(self):
        """获取空字段列表"""
        return [field for field in self.fields if not field.value]

    def is_complete(self):
        """检查表单是否完整填写"""
        return len(self.get_empty_fields()) == 0


# 日报表单
class DailyReport(Form):
    def __init__(self):
        super().__init__("日报", "每日工作总结与计划")
        self.add_field("日期", "填写日报的日期，格式：YYYY-MM-DD")
        self.add_field("今日工作内容", "今天完成的工作内容")
        self.add_field("工作成果", "今天的工作成果")
        self.add_field("遇到的问题", "工作中遇到的问题及解决方案")
        self.add_field("明日计划", "明天的工作计划")


# 周报表单
class WeeklyReport(Form):
    def __init__(self):
        super().__init__("周报", "每周工作总结与计划")
        self.add_field("周次", "第几周，例如：第12周")
        self.add_field("起止日期", "周报覆盖的日期范围，格式：YYYY-MM-DD 至 YYYY-MM-DD")
        self.add_field("本周工作总结", "本周完成的主要工作内容")
        self.add_field("工作成果", "本周的工作成果")
        self.add_field("问题与挑战", "本周遇到的问题及解决方案")
        self.add_field("下周计划", "下周的工作计划")
        self.add_field("需要协助", "需要团队或上级协助的事项")


# 年报表单
class AnnualReport(Form):
    def __init__(self):
        super().__init__("年报", "年度工作总结与计划")
        self.add_field("年度", "报告年份，例如：2025年")
        self.add_field("年度工作总结", "本年度完成的主要工作内容")
        self.add_field("关键成就", "本年度的主要成就")
        self.add_field("项目回顾", "本年度参与的关键项目及其成果")
        self.add_field("挑战与解决方案", "本年度遇到的挑战及解决方案")
        self.add_field("个人成长", "本年度个人成长与技能提升")
        self.add_field("来年目标", "下一年度的工作目标与计划")
        self.add_field("需要支持", "实现目标需要的支持和资源")


# 获取所有表单类型
def get_all_form_types():
    return {
        "日报": DailyReport,
        "周报": WeeklyReport,
        "年报": AnnualReport
    }


# 创建表单实例
def create_form(form_type):
    form_types = get_all_form_types()
    if form_type in form_types:
        return form_types[form_type]()
    return None