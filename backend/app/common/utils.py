"""
通用工具函数模块
"""
import random
import re
import string
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo


def generate_verify_code(length: int = 6) -> str:
    """
    生成数字验证码
    
    Args:
        length: 验证码长度
        
    Returns:
        数字验证码字符串
    """
    return "".join(random.choices(string.digits, k=length))


def generate_random_string(length: int = 16) -> str:
    """
    生成随机字符串
    
    Args:
        length: 字符串长度
        
    Returns:
        随机字符串
    """
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def is_valid_phone(phone: str) -> bool:
    """
    验证手机号格式（中国大陆）
    
    Args:
        phone: 手机号
        
    Returns:
        是否有效
    """
    pattern = r"^1[3-9]\d{9}$"
    return bool(re.match(pattern, phone))


def is_valid_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        是否有效
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def mask_phone(phone: str) -> str:
    """
    手机号脱敏
    
    Args:
        phone: 手机号
        
    Returns:
        脱敏后的手机号，如 138****8888
    """
    if len(phone) >= 11:
        return f"{phone[:3]}****{phone[-4:]}"
    return phone


def mask_email(email: str) -> str:
    """
    邮箱脱敏
    
    Args:
        email: 邮箱地址
        
    Returns:
        脱敏后的邮箱，如 t***t@example.com
    """
    if "@" in email:
        local, domain = email.split("@", 1)
        if len(local) > 2:
            masked_local = f"{local[0]}***{local[-1]}"
        else:
            masked_local = f"{local[0]}***"
        return f"{masked_local}@{domain}"
    return email


def get_utc_now() -> datetime:
    """获取当前UTC时间（已废弃，请使用get_beijing_now）"""
    # 为避免项目内时区混用，统一返回上海时区时间
    return get_beijing_now()


def get_beijing_now() -> datetime:
    """获取当前上海时间（Asia/Shanghai）"""
    beijing_tz = ZoneInfo("Asia/Shanghai")
    return datetime.now(beijing_tz)


def get_current_time() -> datetime:
    """获取当前时间（北京时间，不带时区信息）"""
    beijing_tz = ZoneInfo("Asia/Shanghai")
    return datetime.now(beijing_tz).replace(tzinfo=None)


def to_naive_datetime(dt: datetime) -> datetime:
    """
    将datetime对象转换为naive datetime（不带时区）
    
    用于存储到PostgreSQL的TIMESTAMP WITHOUT TIME ZONE字段
    
    Args:
        dt: datetime对象（可以是aware或naive）
        
    Returns:
        naive datetime对象（北京时间）
    """
    if dt.tzinfo is not None:
        # 如果是aware datetime，转换为北京时间后移除时区信息
        beijing_tz = ZoneInfo("Asia/Shanghai")
        return dt.astimezone(beijing_tz).replace(tzinfo=None)
    return dt


def format_datetime(
    dt: Optional[datetime], 
    fmt: str = "%Y-%m-%d %H:%M:%S"
) -> Optional[str]:
    """
    格式化日期时间
    
    Args:
        dt: 日期时间对象
        fmt: 格式化字符串
        
    Returns:
        格式化后的字符串
    """
    if dt:
        return dt.strftime(fmt)
    return None


def calculate_age(birthday: datetime) -> int:
    """
    根据生日计算年龄
    
    Args:
        birthday: 生日日期
        
    Returns:
        年龄
    """
    beijing_tz = ZoneInfo("Asia/Shanghai")
    today = datetime.now(beijing_tz).date()
    birth_date = birthday.date() if isinstance(birthday, datetime) else birthday
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def get_grade_from_enrollment_year(enrollment_year: int) -> str:
    """
    根据入学年份计算当前年级
    
    Args:
        enrollment_year: 入学年份
        
    Returns:
        年级描述
    """
    beijing_tz = ZoneInfo("Asia/Shanghai")
    now = datetime.now(beijing_tz)
    current_year = now.year
    current_month = now.month
    
    # 9月开学
    school_year = current_year if current_month >= 9 else current_year - 1
    years = school_year - enrollment_year + 1
    
    if years <= 0:
        return "未入学"
    elif years <= 6:
        return f"小学{years}年级"
    elif years <= 9:
        return f"初中{years - 6}年级"
    elif years <= 12:
        return f"高中{years - 9}年级"
    else:
        return "已毕业"

