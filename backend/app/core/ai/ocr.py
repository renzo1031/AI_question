"""
OCR识别服务
使用阿里云OCR SDK进行题目识别
参考文档: https://help.aliyun.com/zh/ocr/developer-reference/api-ocr-api-2021-07-07-recognizeeduquestionocr
"""
import base64
import json
import re
from typing import Optional

from alibabacloud_ocr_api20210707.client import Client as OcrApi20210707Client
from alibabacloud_ocr_api20210707 import models as ocr_api_20210707_models
from alibabacloud_tea_openapi import models as open_api_models
from loguru import logger

from app.core.config import settings


class AliOCRService:
    """阿里云OCR服务"""
    
    def __init__(self):
        self.access_key_id = settings.aliyun_access_key_id
        self.access_key_secret = settings.aliyun_access_key_secret
        # 端点配置：去掉https://前缀（SDK会自动添加）
        endpoint = getattr(settings, "aliyun_ocr_endpoint", "ocr-api.cn-hangzhou.aliyuncs.com")
        # 如果包含协议前缀，去掉它
        if endpoint.startswith("https://"):
            endpoint = endpoint[8:]
        elif endpoint.startswith("http://"):
            endpoint = endpoint[7:]
        self.endpoint = endpoint
        self.region_id = "cn-hangzhou"  # OCR服务区域
        self._client = None
    
    def _get_client(self) -> OcrApi20210707Client:
        """获取OCR客户端（单例）"""
        if self._client is None:
            if not self.access_key_id or not self.access_key_secret:
                raise ValueError("阿里云AccessKey未配置")
            
            # 配置客户端
            config = open_api_models.Config(
                access_key_id=self.access_key_id,
                access_key_secret=self.access_key_secret
            )
            # 设置服务端点
            config.endpoint = self.endpoint
            self._client = OcrApi20210707Client(config)
        
        return self._client
    
    async def recognize_question(
        self,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        image_bytes: Optional[bytes] = None
    ) -> dict:
        """
        识别题目
        
        Args:
            image_url: 图片URL
            image_base64: 图片Base64编码（需要解码为二进制数据）
            image_bytes: 图片二进制数据（与image_url、image_base64三选一）
            
        Returns:
            识别结果字典，包含：
            - content: 题目文本内容
            - figure: 配图位置信息
            - width/height: 图片尺寸
            - prism_wordsInfo: 文字位置信息
            
        Note:
            根据阿里云官方文档，RecognizeEduQuestionOcr接口的body参数需要二进制数据，
            不支持Base64字符串。如果传入image_base64，会自动解码为二进制数据。
        """
        if not image_url and not image_base64 and not image_bytes:
            raise ValueError("image_url、image_base64 和 image_bytes 至少提供一个")
        
        try:
            client = self._get_client()
            
            # 创建请求
            request = ocr_api_20210707_models.RecognizeEduQuestionOcrRequest()
            
            if image_url:
                # 使用URL方式
                request.url = image_url
                logger.debug(f"使用图片URL进行OCR识别: {image_url[:50]}...")
            else:
                # 使用二进制数据方式
                if image_bytes:
                    # 直接使用二进制数据
                    request.body = image_bytes
                    logger.debug(f"使用二进制数据进行OCR识别，大小: {len(image_bytes)} bytes")
                elif image_base64:
                    # 将Base64解码为二进制数据
                    cleaned_base64 = self._clean_base64(image_base64)
                    try:
                        image_bytes = base64.b64decode(cleaned_base64)
                        request.body = image_bytes
                        logger.debug(f"Base64解码成功，使用二进制数据进行OCR识别，大小: {len(image_bytes)} bytes")
                    except Exception as e:
                        logger.error(f"Base64解码失败: {str(e)}")
                        raise ValueError(f"Base64编码格式错误: {str(e)}")
            
            # 调用API（SDK是同步的，需要在异步环境中运行）
            # 使用asyncio.to_thread在后台线程中运行同步SDK调用
            import asyncio
            response = await asyncio.to_thread(client.recognize_edu_question_ocr, request)
            
            # 解析响应
            # 根据官方文档和SDK，响应结构：response.body 包含响应体
            # response.body.data 包含识别结果（可能是JSON字符串）
            if not hasattr(response, 'body'):
                logger.error(f"OCR响应格式错误：缺少body字段，响应类型: {type(response)}")
                raise Exception("OCR响应格式错误：缺少body字段")
            
            response_body = response.body
            
            # 检查响应体中的错误码（阿里云API错误码）
            # 根据官方文档，成功时code为200或不存在，失败时code为错误码
            if hasattr(response_body, 'code'):
                code = response_body.code
                # code可能是字符串或数字
                code_str = str(code) if code is not None else ""
                if code_str and code_str not in ("200", "None"):
                    error_msg = getattr(response_body, 'message', 'OCR识别失败')
                    request_id = getattr(response_body, 'request_id', '')
                    logger.error(f"OCR识别失败 (Code: {code}, RequestId: {request_id}): {error_msg}")
                    raise Exception(f"OCR识别失败: {error_msg}")
            
            # 获取Data字段（识别结果）
            # 根据官方文档，Data是JSON字符串
            data = getattr(response_body, 'data', None)
            if data is None:
                error_msg = getattr(response_body, 'message', 'OCR响应中缺少Data字段')
                logger.error(f"OCR响应中缺少Data字段: {error_msg}")
                raise Exception(f"OCR响应中缺少Data字段: {error_msg}")
            
            # 如果Data是字符串，需要解析为JSON
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    logger.error(f"OCR返回Data字段不是有效的JSON，前100字符: {data[:100]}")
                    raise Exception(f"OCR返回数据格式错误: {str(e)}")
            elif not isinstance(data, dict):
                # 如果Data不是字符串也不是字典，尝试转换为字符串再解析
                data_str = str(data)
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    # 如果还是无法解析，尝试直接使用
                    logger.warning(f"OCR返回Data格式异常，尝试直接使用: {type(data)}")
                    data = {"content": str(data)}
            
            # 提取识别结果
            content = data.get("content", "")
            if not content:
                logger.warning("OCR识别结果中content为空")
            
            return {
                "content": content,
                "figure": data.get("figure", []),
                "width": data.get("width", 0),
                "height": data.get("height", 0),
                "prism_wordsInfo": data.get("prism_wordsInfo", [])
            }
        except Exception as e:
            logger.error(f"OCR识别异常: {str(e)}", exc_info=True)
            raise Exception(f"OCR识别失败: {str(e)}")
    
    def _clean_base64(self, base64_str: str) -> str:
        """
        清理Base64字符串，去掉data:image/xxx;base64,前缀
        
        Args:
            base64_str: 原始Base64字符串
            
        Returns:
            清理后的Base64字符串
        """
        # 去掉可能存在的data:image/xxx;base64,前缀
        pattern = r'^data:image/[^;]+;base64,'
        cleaned = re.sub(pattern, '', base64_str, flags=re.IGNORECASE)
        return cleaned.strip()
    
    def encode_image_to_base64(self, image_bytes: bytes) -> str:
        """将图片字节编码为Base64"""
        return base64.b64encode(image_bytes).decode("utf-8")


# 全局OCR服务实例
ocr_service = AliOCRService()
