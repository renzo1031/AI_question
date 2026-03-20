"""
密码处理模块
提供密码哈希和验证功能
"""
from passlib.context import CryptContext


class PasswordHandler:
    """密码处理类"""
    
    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto"
        )
    
    def hash(self, password: str) -> str:
        """
        对密码进行哈希
        
        Args:
            password: 明文密码
            
        Returns:
            哈希后的密码
        """
        return self.pwd_context.hash(password)
    
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """
        验证密码
        
        Args:
            plain_password: 明文密码
            hashed_password: 哈希密码
            
        Returns:
            验证是否通过
        """
        return self.pwd_context.verify(plain_password, hashed_password)


# 全局密码处理器实例
password_handler = PasswordHandler()

