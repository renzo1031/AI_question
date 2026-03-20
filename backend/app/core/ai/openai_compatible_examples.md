# OpenAI 兼容 API 提供商使用示例

`OpenAICompatibleProvider` 是一个通用的提供商类，支持所有兼容 OpenAI API 格式的大模型。

## 支持的模型服务

- OpenAI (GPT-3.5, GPT-4等)
- Azure OpenAI
- DeepSeek
- Kimi (Moonshot)
- 本地部署的模型（通过vLLM、Ollama、LocalAI等）
- 其他兼容 OpenAI API 格式的服务

## 使用示例

### 1. OpenAI 官方 API

```python
from app.core.ai.openai_compatible import OpenAICompatibleProvider

provider = OpenAICompatibleProvider(
    api_key="sk-your-openai-api-key",
    base_url="https://api.openai.com/v1",
    model="gpt-4",
    provider_name="openai"
)

# 解题
result = await provider.solve_question("1+1=?")
print(result["answer"])

# 原始调用
response = await provider.call_raw(
    prompt="请解答：1+1=?",
    system_prompt="你是一位数学老师"
)
print(response)
```

### 2. DeepSeek

```python
provider = OpenAICompatibleProvider(
    api_key="your-deepseek-api-key",
    base_url="https://api.deepseek.com",
    model="deepseek-chat",
    provider_name="deepseek"
)

result = await provider.solve_question("计算圆的面积，半径为5")
```

### 3. Kimi (Moonshot)

```python
provider = OpenAICompatibleProvider(
    api_key="your-kimi-api-key",
    base_url="https://api.moonshot.cn/v1",
    model="moonshot-v1-8k",
    provider_name="kimi"
)

result = await provider.solve_question("解方程：2x + 3 = 7")
```

### 4. Azure OpenAI

```python
# Azure OpenAI 使用不同的认证方式和URL格式
# 需要在请求头中添加 api-key 而不是 Authorization Bearer
# 注意：当前实现使用标准的 Bearer token，如需支持 Azure，需要扩展

provider = OpenAICompatibleProvider(
    api_key="your-azure-api-key",
    base_url="https://your-resource.openai.azure.com/openai/deployments/your-deployment-name",
    model="gpt-4",  # 您的部署名称
    provider_name="azure_openai"
)
```

### 5. 本地模型（vLLM）

```python
# 使用 vLLM 部署的本地模型
provider = OpenAICompatibleProvider(
    api_key="",  # 本地服务可能不需要 API key
    base_url="http://localhost:8000/v1",
    model="Qwen2-7B-Instruct",  # 您部署的模型名称
    provider_name="vllm_local",
    timeout=120.0  # 本地模型可能需要更长的超时时间
)

result = await provider.solve_question("什么是机器学习？")
```

### 6. Ollama

```python
# Ollama 提供 OpenAI 兼容的 API
provider = OpenAICompatibleProvider(
    api_key="ollama",  # Ollama 不需要真实的 API key
    base_url="http://localhost:11434/v1",
    model="llama2",  # 您在 Ollama 中安装的模型名称
    provider_name="ollama"
)

result = await provider.solve_question("编写一个快速排序算法")
```

### 7. 自定义参数

```python
# 可以自定义温度、最大token数等参数
provider = OpenAICompatibleProvider(
    api_key="your-api-key",
    base_url="https://api.example.com/v1",
    model="example-model",
    provider_name="custom_provider",
    timeout=90.0,        # 90秒超时
    temperature=0.7,     # 更高的随机性
    max_tokens=4000      # 更长的输出
)

result = await provider.solve_question("写一篇关于人工智能的文章")
```

## 在 manager.py 中集成

可以在 `AIModelManager` 中添加通用的 OpenAI 兼容提供商：

```python
# 在 app/core/ai/manager.py 中

from app.core.ai.openai_compatible import OpenAICompatibleProvider

class AIModelManager:
    def _init_providers(self):
        # ... 现有的提供商初始化代码 ...
        
        # OpenAI
        if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
            self.providers["openai"] = OpenAICompatibleProvider(
                api_key=settings.openai_api_key,
                base_url=getattr(settings, "openai_base_url", "https://api.openai.com/v1"),
                model=getattr(settings, "openai_model", "gpt-3.5-turbo"),
                provider_name="openai"
            )
        
        # 通用 OpenAI 兼容提供商（用于自定义服务）
        if hasattr(settings, 'custom_ai_api_key') and settings.custom_ai_api_key:
            self.providers["custom"] = OpenAICompatibleProvider(
                api_key=settings.custom_ai_api_key,
                base_url=settings.custom_ai_base_url,
                model=getattr(settings, "custom_ai_model", "default-model"),
                provider_name="custom"
            )
```

## 环境变量配置示例

在 `.env` 文件中添加相应的配置：

```bash
# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# DeepSeek（可以继续使用专用类，或使用通用类）
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# Kimi（可以继续使用专用类，或使用通用类）
KIMI_API_KEY=your-kimi-api-key
KIMI_BASE_URL=https://api.moonshot.cn/v1
KIMI_MODEL=moonshot-v1-8k

# 自定义 OpenAI 兼容服务
CUSTOM_AI_API_KEY=your-custom-api-key
CUSTOM_AI_BASE_URL=http://your-custom-service.com/v1
CUSTOM_AI_MODEL=your-model-name
```

## 优势

1. **统一接口**：所有兼容 OpenAI API 的服务都可以使用同一个类
2. **灵活配置**：支持自定义 base_url、model、timeout 等参数
3. **易于扩展**：添加新的 OpenAI 兼容服务无需编写新代码
4. **本地开发**：支持本地部署的模型服务，方便开发和测试
5. **成本优化**：可以轻松切换到不同的模型服务以优化成本

## 注意事项

1. **API Key 认证**：大多数服务使用 `Bearer token` 认证，但某些服务（如 Azure OpenAI）可能使用不同的认证方式
2. **URL 格式**：确保 base_url 格式正确，通常以 `/v1` 结尾
3. **模型名称**：不同服务的模型名称格式可能不同，请参考相应服务的文档
4. **超时设置**：本地模型或较慢的服务可能需要增加 timeout 参数
5. **响应格式**：确保服务返回标准的 OpenAI API 响应格式
