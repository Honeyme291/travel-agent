"""
微信公众号签名验证 — SHA1 校验
"""
import hashlib
import os


def check_signature(signature: str, timestamp: str, nonce: str) -> bool:
    """
    验证微信服务器签名
    规则: 对 [token, timestamp, nonce] 排序后 SHA1，与 signature 比较
    """
    token = os.getenv("WECHAT_TOKEN", "")
    if not token:
        return False

    tmp_list = sorted([token, timestamp, nonce])
    tmp_str = "".join(tmp_list)
    computed = hashlib.sha1(tmp_str.encode()).hexdigest()

    return computed == signature
