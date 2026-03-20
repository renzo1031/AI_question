"""
DeepSeek AI模型提供商
根据官方文档：https://api-docs.deepseek.com/zh-cn/
DeepSeek API使用与OpenAI兼容的API格式
"""
from typing import Optional

import httpx
from loguru import logger

from app.core.ai.base import AIModelProvider


class DeepSeekProvider(AIModelProvider):
    """DeepSeek提供商（与OpenAI API兼容）"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com", model: str = "deepseek-chat"):
        """
        初始化DeepSeek提供商
        
        Args:
            api_key: DeepSeek API Key（从 https://platform.deepseek.com/api_keys 获取）
            base_url: API基础URL，默认为 https://api.deepseek.com
                      也可以使用 https://api.deepseek.com/v1（出于兼容性考虑）
            model: 模型名称，可选：
                   - deepseek-chat: DeepSeek-V3.2 非思考模式
                   - deepseek-reasoner: DeepSeek-V3.2 思考模式
        """
        self.api_key = api_key
        # 保存原始base_url，在调用时构建完整URL
        self.base_url = base_url.rstrip('/')
        self.model = model
    
    async def solve_question(self, question: str, context: Optional[str] = None) -> dict:
        """使用DeepSeek解题"""
        if not self.api_key:
            raise ValueError("DeepSeek API Key未配置")
        
        prompt = self._build_prompt(question, context)
        
        try:
            # 根据DeepSeek官方文档，API格式与OpenAI兼容
            # base_url可以是 https://api.deepseek.com 或 https://api.deepseek.com/v1
            # 构建完整的API URL
            if self.base_url.endswith('/v1'):
                api_url = f"{self.base_url}/chat/completions"
            else:
                # 如果base_url不包含/v1，直接添加/chat/completions
                api_url = f"{self.base_url}/chat/completions"
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    api_url,
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "你是一位经验丰富的数学老师，擅长解答中小学数学题目。请详细解答题目，包括解题步骤和最终答案。"
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 2000,
                        "stream": False  # 非流式输出
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                # 解析响应（与OpenAI格式兼容）
                choices = result.get("choices", [])
                if not choices:
                    error_msg = result.get("error", {}).get("message", "DeepSeek返回结果为空")
                    logger.error(f"DeepSeek API错误: {error_msg}")
                    raise Exception(f"DeepSeek返回结果为空: {error_msg}")
                
                answer_text = choices[0].get("message", {}).get("content", "")
                
                if not answer_text:
                    raise Exception("DeepSeek返回结果为空")
                
                return {
                    "answer": answer_text,
                    "provider": "deepseek",
                    "model": self.model
                }
        except httpx.HTTPError as e:
            logger.error(f"DeepSeek API调用失败: {str(e)}")
            raise Exception(f"DeepSeek服务异常: {str(e)}")
        except Exception as e:
            logger.error(f"DeepSeek调用异常: {str(e)}")
            raise Exception(f"DeepSeek服务异常: {str(e)}")
    
    async def call_raw(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        直接调用DeepSeek，返回原始文本响应
        
        Args:
            prompt: 完整的用户提示词
            system_prompt: 系统提示词（可选）
            
        Returns:
            AI返回的原始文本内容
        """
        if not self.api_key:
            raise ValueError("DeepSeek API Key未配置")
        
        try:
            # 构建API URL
            if self.base_url.endswith('/v1'):
                api_url = f"{self.base_url}/chat/completions"
            else:
                api_url = f"{self.base_url}/chat/completions"
            
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
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    api_url,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.3,
                        "max_tokens": 2000,
                        "stream": False
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                # 解析响应
                choices = result.get("choices", [])
                if not choices:
                    error_msg = result.get("error", {}).get("message", "DeepSeek返回结果为空")
                    logger.error(f"DeepSeek API错误: {error_msg}")
                    raise Exception(f"DeepSeek返回结果为空: {error_msg}")
                
                answer_text = choices[0].get("message", {}).get("content", "")
                
                if not answer_text:
                    raise Exception("DeepSeek返回结果为空")
                
                return answer_text
        except httpx.HTTPError as e:
            logger.error(f"DeepSeek API调用失败: {str(e)}")
            raise Exception(f"DeepSeek服务异常: {str(e)}")
        except Exception as e:
            logger.error(f"DeepSeek call_raw调用异常: {str(e)}")
            raise Exception(f"DeepSeek服务异常: {str(e)}")

