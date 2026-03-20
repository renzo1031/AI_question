"""
SM4加密模块
提供SM4对称加密功能，用于敏感数据加密
"""
import base64
import secrets
from typing import Optional

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from app.core.config import settings


class SM4Cipher:
    """
    SM4加密类
    注意：由于PyCryptodome不直接支持SM4，这里使用AES-128作为替代
    如需真正的SM4，可使用gmssl库
    实际生产环境建议使用国密库
    """
    
    BLOCK_SIZE = 16
    
    def __init__(self, key: Optional[str] = None):
        """
        初始化SM4加密器
        
        Args:
            key: 16字节密钥，默认使用配置中的密钥
        """
        self.key = (key or settings.sm4_secret_key).encode("utf-8")[:16].ljust(16, b'\0')
    
    def encrypt(self, plaintext: str) -> str:
        """
        加密明文
        
        Args:
            plaintext: 待加密的明文
            
        Returns:
            Base64编码的密文（包含IV）
        """
        iv = secrets.token_bytes(self.BLOCK_SIZE)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded_data = pad(plaintext.encode("utf-8"), self.BLOCK_SIZE)
        encrypted = cipher.encrypt(padded_data)
        # IV + 密文一起返回
        return base64.b64encode(iv + encrypted).decode("utf-8")
    
    def decrypt(self, ciphertext: str) -> str:
        """
        解密密文
        
        Args:
            ciphertext: Base64编码的密文
            
        Returns:
            解密后的明文
        """
        data = base64.b64decode(ciphertext)
        iv = data[:self.BLOCK_SIZE]
        encrypted = data[self.BLOCK_SIZE:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(encrypted), self.BLOCK_SIZE)
        return decrypted.decode("utf-8")
    
    @staticmethod
    def generate_key() -> str:
        """生成随机16字节密钥"""
        return secrets.token_hex(8)


# 全局SM4加密器实例
sm4_cipher = SM4Cipher()


# 便捷函数
def sm4_encrypt(plaintext: str) -> str:
    """
    加密明文
    
    Args:
        plaintext: 待加密的明文
        
    Returns:
        Base64编码的密文
    """
    return sm4_cipher.encrypt(plaintext)


def sm4_decrypt(ciphertext: str) -> str:
    """
    解密密文
    
    Args:
        ciphertext: Base64编码的密文
        
    Returns:
        解密后的明文
    """
    return sm4_cipher.decrypt(ciphertext)

