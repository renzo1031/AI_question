"""
通义千问AI模型提供商
使用阿里云DashScope SDK
"""
import os
from typing import Optional

import asyncio
from dashscope import Generation
from loguru import logger

from app.core.ai.base import AIModelProvider


class TongYiProvider(AIModelProvider):
    """通义千问提供商（使用DashScope SDK）"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "qwen-turbo",
        base_url: Optional[str] = None
    ):
        """
        初始化通义千问提供商
        
        Args:
            api_key: DashScope API Key
            model: 模型名称，默认为qwen-turbo，可选：qwen-plus, qwen-max, qwen-plus-2025-07-28等
            base_url: API基础URL（DashScope SDK会自动处理，此参数保留用于兼容）
        """
        self.api_key = api_key
        self.model = model
        # 设置环境变量，DashScope SDK会自动读取
        os.environ['DASHSCOPE_API_KEY'] = api_key
    
    async def solve_question(self, question: str, context: Optional[str] = None) -> dict:
        """
        使用通义千问解题
        
        根据阿里云DashScope官方文档实现
        """
        if not self.api_key:
            raise ValueError("通义千问API Key未配置")
        
        prompt = self._build_prompt(question, context)
        
        try:
            # 构建消息
            messages = [
                {
                    "role": "system",
                    "content": "你是一位经验丰富的数学老师，擅长解答中小学数学题目。请详细解答题目，包括解题步骤和最终答案。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # 在后台线程中运行同步SDK调用
            def _call_dashscope():
                gen = Generation()
                response = gen.call(
                    model=self.model,
                    messages=messages,
                    api_key=self.api_key,  # 显式传入API key
                    temperature=0.5,
                    max_tokens=200000,
                    result_format='message'  # 返回消息格式
                )
                return response
            
            response = await asyncio.to_thread(_call_dashscope)
            
            # 解析响应
            if response.status_code != 200:
                error_msg = getattr(response, 'message', '通义千问调用失败')
                logger.error(f"通义千问API调用失败 (Status: {response.status_code}): {error_msg}")
                raise Exception(f"通义千问调用失败: {error_msg}")
            
            # 获取输出文本
            # DashScope返回格式：response.output.choices[0].message.content
            answer_text = ""
            if hasattr(response, 'output'):
                output = response.output
                if hasattr(output, 'choices') and output.choices:
                    message = output.choices[0].get('message', {})
                    answer_text = message.get('content', '')
                elif hasattr(output, 'text'):
                    answer_text = output.text
                elif isinstance(output, dict):
                    # 兼容字典格式
                    if 'choices' in output and output['choices']:
                        answer_text = output['choices'][0].get('message', {}).get('content', '')
                    else:
                        answer_text = output.get('text', '')
            
            if not answer_text:
                logger.error(f"通义千问返回结果为空，响应: {response}")
                raise Exception("通义千问返回结果为空")
            
            return {
                "answer": answer_text,
                "provider": "tongyi",
                "model": self.model
            }
        except Exception as e:
            logger.error(f"通义千问API调用异常: {str(e)}")
            raise Exception(f"通义千问服务异常: {str(e)}")
    
    async def call_raw(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        直接调用通义千问，返回原始文本响应
        
        Args:
            prompt: 完整的用户提示词
            system_prompt: 系统提示词（可选）
            
        Returns:
            AI返回的原始文本内容
        """
        if not self.api_key:
            raise ValueError("通义千问API Key未配置")
        
        try:
            # 构建消息
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # 在后台线程中运行同步SDK调用
            def _call_dashscope():
                gen = Generation()
                response = gen.call(
                    model=self.model,
                    messages=messages,
                    api_key=self.api_key,
                    temperature=0.3,
                    max_tokens=2000,
                    result_format='message'
                )
                return response
            
            response = await asyncio.to_thread(_call_dashscope)
            
            # 解析响应
            if response.status_code != 200:
                error_msg = getattr(response, 'message', '通义千问调用失败')
                logger.error(f"通义千问API调用失败 (Status: {response.status_code}): {error_msg}")
                raise Exception(f"通义千问调用失败: {error_msg}")
            
            # 获取输出文本
            answer_text = ""
            if hasattr(response, 'output'):
                output = response.output
                if hasattr(output, 'choices') and output.choices:
                    message = output.choices[0].get('message', {})
                    answer_text = message.get('content', '')
                elif hasattr(output, 'text'):
                    answer_text = output.text
                elif isinstance(output, dict):
                    if 'choices' in output and output['choices']:
                        answer_text = output['choices'][0].get('message', {}).get('content', '')
                    else:
                        answer_text = output.get('text', '')
            
            if not answer_text:
                logger.error(f"通义千问返回结果为空，响应: {response}")
                raise Exception("通义千问返回结果为空")
            
            return answer_text
        except Exception as e:
            logger.error(f"通义千问call_raw调用异常: {str(e)}")
            raise Exception(f"通义千问服务异常: {str(e)}")

