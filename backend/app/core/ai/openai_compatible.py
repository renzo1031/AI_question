"""
通用的OpenAI兼容API提供商
支持所有兼容OpenAI API格式的大模型，包括：
- OpenAI (GPT-3.5, GPT-4等)
- Azure OpenAI
- DeepSeek
- Kimi (Moonshot)
- 本地部署的模型（如通过vLLM、Ollama等部署的模型）
- 其他兼容OpenAI API格式的服务
"""
from typing import Optional

import httpx
from loguru import logger

from app.core.ai.base import AIModelProvider


class OpenAICompatibleProvider(AIModelProvider):
    """通用的OpenAI兼容API提供商"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        provider_name: str = "openai_compatible",
        timeout: float = 60.0,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ):
        """
        初始化OpenAI兼容提供商
        
        Args:
            api_key: API Key（如果服务不需要认证，可以传入空字符串或任意值）
            base_url: API基础URL，例如：
                     - OpenAI: https://api.openai.com/v1
                     - Azure OpenAI: https://your-resource.openai.azure.com
                     - DeepSeek: https://api.deepseek.com
                     - Kimi: https://api.moonshot.cn/v1
                     - 本地模型: http://localhost:8000/v1
            model: 模型名称，例如：
                   - OpenAI: gpt-3.5-turbo, gpt-4, gpt-4-turbo等
                   - Azure OpenAI: 您部署的模型名称
                   - DeepSeek: deepseek-chat, deepseek-reasoner
                   - Kimi: moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k
                   - 本地模型: 根据部署的模型名称
            provider_name: 提供商名称，用于标识和日志记录，默认为"openai_compatible"
            timeout: 请求超时时间（秒），默认60秒
            temperature: 温度参数，控制输出随机性，默认0.3
            max_tokens: 最大输出token数，默认2000
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.provider_name = provider_name
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def _build_api_url(self, endpoint: str = "chat/completions") -> str:
        """
        构建完整的API URL
        
        Args:
            endpoint: API端点，默认为"chat/completions"
            
        Returns:
            完整的API URL
        """
        # 如果base_url已经包含了端点，直接返回
        if self.base_url.endswith(f"/{endpoint}"):
            return self.base_url
        
        # 如果base_url已经包含/v1，直接拼接端点
        if self.base_url.endswith('/v1'):
            return f"{self.base_url}/{endpoint}"
        
        # 否则，假设需要添加端点
        return f"{self.base_url}/{endpoint}"
    
    def _build_headers(self) -> dict:
        """
        构建请求头
        
        Returns:
            请求头字典
        """
        headers = {
            "Content-Type": "application/json"
        }
        
        # 如果提供了API Key，添加Authorization头
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    async def solve_question(self, question: str, context: Optional[str] = None) -> dict:
        """使用OpenAI兼容API解题"""
        prompt = self._build_prompt(question, context)
        
        try:
            api_url = self._build_api_url()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
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
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens,
                        "stream": False
                    },
                    headers=self._build_headers()
                )
                response.raise_for_status()
                result = response.json()
                
                # 解析OpenAI格式的响应
                choices = result.get("choices", [])
                if not choices:
                    error_msg = result.get("error", {}).get("message", f"{self.provider_name}返回结果为空")
                    logger.error(f"{self.provider_name} API错误: {error_msg}")
                    raise Exception(f"{self.provider_name}返回结果为空: {error_msg}")
                
                answer_text = choices[0].get("message", {}).get("content", "")
                
                if not answer_text:
                    raise Exception(f"{self.provider_name}返回结果为空")
                
                return {
                    "answer": answer_text,
                    "provider": self.provider_name,
                    "model": self.model
                }
        except httpx.HTTPError as e:
            logger.error(f"{self.provider_name} API调用失败: {str(e)}")
            raise Exception(f"{self.provider_name}服务异常: {str(e)}")
        except Exception as e:
            logger.error(f"{self.provider_name}调用异常: {str(e)}")
            raise Exception(f"{self.provider_name}服务异常: {str(e)}")
    
    async def call_raw(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        直接调用OpenAI兼容API，返回原始文本响应
        
        Args:
            prompt: 完整的用户提示词
            system_prompt: 系统提示词（可选）
            
        Returns:
            AI返回的原始文本内容
        """
        try:
            api_url = self._build_api_url()
            
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
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    api_url,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens,
                        "stream": False
                    },
                    headers=self._build_headers()
                )
                response.raise_for_status()
                result = response.json()
                
                # 解析响应
                choices = result.get("choices", [])
                if not choices:
                    error_msg = result.get("error", {}).get("message", f"{self.provider_name}返回结果为空")
                    logger.error(f"{self.provider_name} API错误: {error_msg}")
                    raise Exception(f"{self.provider_name}返回结果为空: {error_msg}")
                
                answer_text = choices[0].get("message", {}).get("content", "")
                
                if not answer_text:
                    raise Exception(f"{self.provider_name}返回结果为空")
                
                return answer_text
        except httpx.HTTPError as e:
            logger.error(f"{self.provider_name} API调用失败: {str(e)}")
            raise Exception(f"{self.provider_name}服务异常: {str(e)}")
        except Exception as e:
            logger.error(f"{self.provider_name} call_raw调用异常: {str(e)}")
            raise Exception(f"{self.provider_name}服务异常: {str(e)}")
