"""
JWT认证模块
用于普通用户的Token认证
"""
from datetime import datetime, timedelta
from typing import Any, Optional
from zoneinfo import ZoneInfo

import jwt

from app.core.config import settings
from app.core.security.sm4 import sm4_cipher


class JWTHandler:
    """JWT处理类"""
    
    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire = settings.jwt_access_token_expire_minutes
        self.refresh_token_expire = settings.jwt_refresh_token_expire_days
    
    def create_access_token(
        self, 
        data: dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建访问Token
        
        Args:
            data: Token负载数据
            expires_delta: 自定义过期时间
            
        Returns:
            加密后的JWT Token
        """
        to_encode = data.copy()
        expire = datetime.now(ZoneInfo("Asia/Shanghai")) + (
            expires_delta or timedelta(minutes=self.access_token_expire)
        )
        to_encode.update({
            "exp": expire,
            "type": "access"
        })
        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        # 使用SM4加密Token
        return sm4_cipher.encrypt(token)
    
    def create_refresh_token(
        self, 
        data: dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建刷新Token
        
        Args:
            data: Token负载数据
            expires_delta: 自定义过期时间
            
        Returns:
            加密后的JWT Token
        """
        to_encode = data.copy()
        expire = datetime.now(ZoneInfo("Asia/Shanghai")) + (
            expires_delta or timedelta(days=self.refresh_token_expire)
        )
        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })
        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return sm4_cipher.encrypt(token)
    
    def decode_token(self, encrypted_token: str) -> Optional[dict[str, Any]]:
        """
        解码Token
        
        Args:
            encrypted_token: SM4加密的JWT Token
            
        Returns:
            Token负载数据，解码失败返回None
        """
        try:
            # 先解密SM4
            token = sm4_cipher.decrypt(encrypted_token)
            # 再解码JWT
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            return payload
        except Exception:
            return None
    
    def verify_access_token(self, encrypted_token: str) -> Optional[dict[str, Any]]:
        """
        验证访问Token
        
        Args:
            encrypted_token: SM4加密的JWT Token
            
        Returns:
            Token负载数据，验证失败返回None
        """
        payload = self.decode_token(encrypted_token)
        if payload and payload.get("type") == "access":
            return payload
        return None
    
    def verify_refresh_token(self, encrypted_token: str) -> Optional[dict[str, Any]]:
        """
        验证刷新Token
        
        Args:
            encrypted_token: SM4加密的JWT Token
            
        Returns:
            Token负载数据，验证失败返回None
        """
        payload = self.decode_token(encrypted_token)
        if payload and payload.get("type") == "refresh":
            return payload
        return None
    
    def get_token_expiry(self, encrypted_token: str) -> Optional[datetime]:
        """获取Token过期时间"""
        payload = self.decode_token(encrypted_token)
        if payload and "exp" in payload:
            return datetime.fromtimestamp(payload["exp"], tz=ZoneInfo("Asia/Shanghai"))
        return None


# 全局JWT处理器实例
jwt_handler = JWTHandler()

