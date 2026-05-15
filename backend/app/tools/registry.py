"""
工具注册中心 — 统一管理和创建所有 Agent 工具
"""
from typing import List

from langchain_classic.tools import Tool

from app.tools.train_query import create_train_query_tool
from app.tools.weather import create_weather_tool
from app.tools.geo import create_geo_tool
from app.tools.hotel import create_hotel_tool
from app.tools.poi import create_poi_tool
from app.tools.driving import create_driving_tool
from app.tools.transit import create_transit_tool
from app.tools.lucky_day import create_lucky_day_tool
from app.tools.r1_analysis import create_r1_tool


class ToolRegistry:
    """工具注册中心 — 延迟初始化以避免循环依赖"""

    def __init__(self):
        self._factories = {
            "train_query": create_train_query_tool,
            "gaode_weather": create_weather_tool,
            "gaode_geo": create_geo_tool,
            "gaode_hotel_search": create_hotel_tool,
            "gaode_poi_search": create_poi_tool,
            "gaode_driving": create_driving_tool,
            "gaode_transit": create_transit_tool,
            "lucky_day": create_lucky_day_tool,
            "r1_analysis": create_r1_tool,
        }
        self._cache: dict[str, Tool] = {}

    def get_all(self) -> List[Tool]:
        """返回所有已注册的工具实例"""
        if not self._cache:
            for name, factory in self._factories.items():
                try:
                    self._cache[name] = factory()
                except Exception as e:
                    print(f"[ToolRegistry] Failed to create '{name}': {e}")
        return list(self._cache.values())

    def get(self, name: str) -> Tool | None:
        tools = self.get_all()
        for t in tools:
            if t.name == name:
                return t
        return None

    def list_names(self) -> List[str]:
        return list(self._factories.keys())


tool_registry = ToolRegistry()
