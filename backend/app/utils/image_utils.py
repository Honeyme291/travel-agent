"""
图片工具 — 下载、缓存、处理
"""
import os
import hashlib
from pathlib import Path

import requests

CACHE_DIR = Path(os.getenv("IMAGE_CACHE_DIR", "/tmp/travel_images"))


async def download_image(url: str, filename: str = None) -> str:
    """
    下载图片到本地缓存

    Returns: 本地文件路径
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if filename is None:
        filename = hashlib.md5(url.encode()).hexdigest() + ".jpg"

    filepath = CACHE_DIR / filename
    if filepath.exists():
        return str(filepath)

    resp = requests.get(url, timeout=15, stream=True)
    resp.raise_for_status()
    with open(filepath, "wb") as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)

    return str(filepath)
