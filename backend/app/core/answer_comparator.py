"""
答案比较策略模块
支持不同题型的判题策略，可扩展
"""
import re
from abc import ABC, abstractmethod
from typing import Optional


class AnswerComparator(ABC):
    """答案比较器基类"""
    
    @abstractmethod
    def compare(self, user_answer: str, correct_answer: str) -> bool:
        """
        比较用户答案和正确答案
        
        Args:
            user_answer: 用户答案
            correct_answer: 正确答案
            
        Returns:
            是否匹配
        """


class ChoiceAnswerComparator(AnswerComparator):
    """选择题判题策略（支持单选和多选）"""
    
    def compare(self, user_answer: str, correct_answer: str) -> bool:
        """
        比较选择题答案
        
        支持格式：
        - 单选：A, B, C, D
        - 多选：A,B 或 A, B 或 AB（顺序无关）
        """
        # 去除首尾空白
        user_ans = user_answer.strip().upper()
        correct_ans = correct_answer.strip().upper()
        
        # 如果包含逗号，按多选处理
        if "," in user_ans or "," in correct_ans:
            # 分割并去重，转换为集合比较（顺序无关）
            user_set = set(re.split(r'[,\s]+', user_ans))
            correct_set = set(re.split(r'[,\s]+', correct_ans))
            # 移除空字符串
            user_set.discard("")
            correct_set.discard("")
            return user_set == correct_set
        else:
            # 单选：直接比较（忽略大小写）
            return user_ans == correct_ans


class FillBlankAnswerComparator(AnswerComparator):
    """填空题判题策略"""
    
    def compare(self, user_answer: str, correct_answer: str) -> bool:
        """
        比较填空题答案
        
        策略：
        - 忽略空格、大小写、标点符号
        - 只比较字母和数字
        """
        # 去除首尾空白
        user_ans = user_answer.strip()
        correct_ans = correct_answer.strip()
        
        # 移除所有非字母数字字符，转换为小写
        user_normalized = re.sub(r'[^\w]', '', user_ans.lower())
        correct_normalized = re.sub(r'[^\w]', '', correct_ans.lower())
        
        return user_normalized == correct_normalized


class NumericAnswerComparator(AnswerComparator):
    """数值题判题策略（支持容差）"""
    
    def __init__(self, tolerance: float = 0.01):
        """
        初始化数值题比较器
        
        Args:
            tolerance: 允许的误差范围（默认0.01）
        """
        self.tolerance = tolerance
    
    def compare(self, user_answer: str, correct_answer: str) -> bool:
        """
        比较数值题答案
        
        策略：
        - 转换为浮点数比较
        - 允许一定的误差范围
        """
        try:
            user_num = float(user_answer.strip())
            correct_num = float(correct_answer.strip())
            return abs(user_num - correct_num) < self.tolerance
        except (ValueError, TypeError):
            # 如果无法转换为数字，回退到字符串比较
            return user_answer.strip() == correct_answer.strip()


class JudgmentAnswerComparator(AnswerComparator):
    """判断题判题策略"""
    
    def compare(self, user_answer: str, correct_answer: str) -> bool:
        """
        比较判断题答案
        
        支持格式：
        - 正确/错误
        - 对/错
        - True/False
        - T/F
        """
        # 标准化答案
        user_ans = user_answer.strip().lower()
        correct_ans = correct_answer.strip().lower()
        
        # 映射到标准格式
        true_values = {"正确", "对", "true", "t", "是", "yes", "y", "1"}
        false_values = {"错误", "错", "false", "f", "否", "no", "n", "0"}
        
        user_bool = user_ans in true_values
        correct_bool = correct_ans in true_values
        
        # 如果用户答案是false值，则为False
        if user_ans in false_values:
            user_bool = False
        if correct_ans in false_values:
            correct_bool = False
        
        return user_bool == correct_bool


class DefaultAnswerComparator(AnswerComparator):
    """默认判题策略（用于未匹配的题型）"""
    
    def compare(self, user_answer: str, correct_answer: str) -> bool:
        """
        默认比较策略
        
        策略：
        - 忽略空格和大小写
        """
        user_ans = user_answer.strip().replace(" ", "").lower()
        correct_ans = correct_answer.strip().replace(" ", "").lower()
        return user_ans == correct_ans


class AnswerComparatorFactory:
    """答案比较器工厂"""
    
    # 题型到比较器的映射
    _comparators: dict[str, AnswerComparator] = {}
    
    @classmethod
    def register(cls, question_type: str, comparator: AnswerComparator):
        """注册题型对应的比较器"""
        cls._comparators[question_type] = comparator
    
    @classmethod
    def get_comparator(cls, question_type: Optional[str] = None) -> AnswerComparator:
        """
        获取对应的比较器
        
        Args:
            question_type: 题目类型（可选）
            
        Returns:
            答案比较器实例
        """
        if not question_type:
            return DefaultAnswerComparator()
        
        # 标准化题目类型（去除空格，转换为小写）
        normalized_type = question_type.strip().lower()
        
        # 精确匹配
        if normalized_type in cls._comparators:
            return cls._comparators[normalized_type]
        
        # 模糊匹配（包含关键词）
        for key, comparator in cls._comparators.items():
            if key in normalized_type or normalized_type in key:
                return comparator
        
        # 默认比较器
        return DefaultAnswerComparator()
    
    @classmethod
    def initialize_defaults(cls):
        """初始化默认比较器"""
        if not cls._comparators:
            cls.register("选择题", ChoiceAnswerComparator())
            cls.register("单选题", ChoiceAnswerComparator())
            cls.register("多选题", ChoiceAnswerComparator())
            cls.register("填空题", FillBlankAnswerComparator())
            cls.register("简答题", FillBlankAnswerComparator())
            cls.register("计算题", NumericAnswerComparator())
            cls.register("数值题", NumericAnswerComparator())
            cls.register("判断题", JudgmentAnswerComparator())


# 初始化默认比较器
AnswerComparatorFactory.initialize_defaults()

