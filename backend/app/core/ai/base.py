"""
AI模型提供商基类
定义所有AI提供商的统一接口
"""
from abc import ABC, abstractmethod
from typing import Optional


class AIModelProvider(ABC):
    """AI模型提供商基类"""
    
    @abstractmethod
    async def solve_question(self, question: str, context: Optional[str] = None) -> dict:
        """
        解题
        
        Args:
            question: 题目内容
            context: 上下文信息（可选）
            
        Returns:
            包含答案和解析的字典，格式：
            {
                "answer": str,      # 答案内容
                "provider": str,     # 提供商名称
                "model": str         # 使用的模型名称
            }
        """
    
    @abstractmethod
    async def call_raw(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        直接调用AI模型，返回原始文本响应
        
        用于需要自定义 prompt 的场景（如结构化输出）
        
        Args:
            prompt: 完整的用户提示词
            system_prompt: 系统提示词（可选，如果不提供则使用默认值）
            
        Returns:
            AI返回的原始文本内容
            
        Raises:
            Exception: 当AI服务调用失败时
        """
    
    def _build_prompt(self, question: str, context: Optional[str] = None) -> str:
        """
        构建提示词（默认实现，子类可重写）
        
        Args:
            question: 题目内容
            context: 上下文信息（可选）
            
        Returns:
            构建好的提示词
        """
        prompt = f"请解答以下题目：\n\n{question}\n\n"
        if context:
            prompt += f"上下文信息：{context}\n\n"
        prompt += "请提供详细的解题步骤和最终答案。"
        return prompt

