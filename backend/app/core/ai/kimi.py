"""
Kimi (Moonshot) AI模型提供商
根据官方文档：https://platform.moonshot.cn/docs/guide/start-using-kimi-api
"""
from typing import Optional

import httpx
from loguru import logger

from app.core.ai.base import AIModelProvider


class KimiProvider(AIModelProvider):
    """Kimi（Moonshot）提供商"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.moonshot.cn/v1", model: str = "moonshot-v1-8k"):
        """
        初始化Kimi提供商
        
        Args:
            api_key: Kimi API Key（从 https://platform.moonshot.cn 获取）
            base_url: API基础URL，默认为 https://api.moonshot.cn/v1
            model: 模型名称，可选：
                   - moonshot-v1-8k
                   - moonshot-v1-32k
                   - moonshot-v1-128k
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
    
    async def solve_question(self, question: str, context: Optional[str] = None) -> dict:
        """使用Kimi解题"""
        if not self.api_key:
            raise ValueError("Kimi API Key未配置")
        
        prompt = self._build_prompt(question, context)
        
        try:
            # 根据Moonshot官方文档构建API URL
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
                        "temperature": 0.5,
                        "max_tokens": 200000
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
                    error_msg = result.get("error", {}).get("message", "Kimi返回结果为空")
                    logger.error(f"Kimi API错误: {error_msg}")
                    raise Exception(f"Kimi返回结果为空: {error_msg}")
                
                answer_text = choices[0].get("message", {}).get("content", "")
                
                if not answer_text:
                    raise Exception("Kimi返回结果为空")
                
                return {
                    "answer": answer_text,
                    "provider": "kimi",
                    "model": self.model
                }
        except httpx.HTTPError as e:
            logger.error(f"Kimi API调用失败: {str(e)}")
            raise Exception(f"Kimi服务异常: {str(e)}")
        except Exception as e:
            logger.error(f"Kimi调用异常: {str(e)}")
            raise Exception(f"Kimi服务异常: {str(e)}")
    
    async def call_raw(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        直接调用Kimi，返回原始文本响应
        
        Args:
            prompt: 完整的用户提示词
            system_prompt: 系统提示词（可选）
            
        Returns:
            AI返回的原始文本内容
        """
        if not self.api_key:
            raise ValueError("Kimi API Key未配置")
        
        try:
            # 构建API URL
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
                        "max_tokens": 2000
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
                    error_msg = result.get("error", {}).get("message", "Kimi返回结果为空")
                    logger.error(f"Kimi API错误: {error_msg}")
                    raise Exception(f"Kimi返回结果为空: {error_msg}")
                
                answer_text = choices[0].get("message", {}).get("content", "")
                
                if not answer_text:
                    raise Exception("Kimi返回结果为空")
                
                return answer_text
        except httpx.HTTPError as e:
            logger.error(f"Kimi API调用失败: {str(e)}")
            raise Exception(f"Kimi服务异常: {str(e)}")
        except Exception as e:
            logger.error(f"Kimi call_raw调用异常: {str(e)}")
            raise Exception(f"Kimi服务异常: {str(e)}")

