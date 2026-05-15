"""
微信公众号消息处理器 — XML 解析、消息路由、回复生成
"""
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WechatMessage:
    """微信消息数据结构"""
    to_user: str = ""
    from_user: str = ""  # OpenID
    msg_type: str = "text"
    content: str = ""
    msg_id: str = ""
    create_time: str = ""
    # 事件类型
    event: str = ""
    event_key: str = ""


@dataclass
class WechatReply:
    """微信回复数据结构"""
    to_user: str
    from_user: str
    msg_type: str = "text"
    content: str = ""
    articles: list = field(default_factory=list)

    def to_xml(self) -> str:
        """转为微信 XML 格式"""
        template = "<xml>"
        template += f"<ToUserName><![CDATA[{self.to_user}]]></ToUserName>"
        template += f"<FromUserName><![CDATA[{self.from_user}]]></FromUserName>"
        template += f"<CreateTime>{int(time.time())}</CreateTime>"

        if self.msg_type == "text":
            template += "<MsgType><![CDATA[text]]></MsgType>"
            template += f"<Content><![CDATA[{self.content}]]></Content>"

        elif self.msg_type == "image":
            template += "<MsgType><![CDATA[image]]></MsgType>"
            template += f"<Image><MediaId><![CDATA[{self.content}]]></MediaId></Image>"

        elif self.msg_type == "news" and self.articles:
            template += "<MsgType><![CDATA[news]]></MsgType>"
            template += f"<ArticleCount>{len(self.articles)}</ArticleCount>"
            template += "<Articles>"
            for art in self.articles:
                template += "<item>"
                template += f"<Title><![CDATA[{art.get('title', '')}]]></Title>"
                template += f"<Description><![CDATA[{art.get('description', '')}]]></Description>"
                template += f"<PicUrl><![CDATA[{art.get('pic_url', '')}]]></PicUrl>"
                template += f"<Url><![CDATA[{art.get('url', '')}]]></Url>"
                template += "</item>"
            template += "</Articles>"

        template += "</xml>"
        return template


def parse_wechat_message(xml_data: str) -> WechatMessage:
    """解析微信 XML 消息"""
    root = ET.fromstring(xml_data)

    def get_text(tag: str) -> str:
        elem = root.find(tag)
        return elem.text or "" if elem is not None else ""

    return WechatMessage(
        to_user=get_text("ToUserName"),
        from_user=get_text("FromUserName"),
        msg_type=get_text("MsgType"),
        content=get_text("Content"),
        msg_id=get_text("MsgId"),
        create_time=get_text("CreateTime"),
        event=get_text("Event"),
        event_key=get_text("EventKey"),
    )


async def handle_wechat_message(msg: WechatMessage) -> WechatReply:
    """
    核心消息路由 — 根据消息类型分发处理

    当前支持:
    - text: 调用 Agent 生成回复
    - event: 关注/取消关注等事件
    - image/voice: 暂不支持，返回提示
    """
    reply = WechatReply(to_user=msg.from_user, from_user=msg.to_user)

    if msg.msg_type == "event":
        if msg.event == "subscribe":
            reply.content = (
                "欢迎关注智慧旅行助手! \n\n"
                "我可以帮您:\n"
                "📍 规划旅游路线\n"
                "☀️ 查询天气预报\n"
                "🚆 查询火车票\n"
                "🗓️ 查看黄历吉日\n"
                "🏨 推荐酒店住宿\n\n"
                "直接告诉我您的旅行需求吧!"
            )
        elif msg.event == "unsubscribe":
            reply.content = ""
        else:
            reply.content = "收到您的事件消息"

    elif msg.msg_type == "text":
        # 交给 Agent 处理（由 API 层调用 travel_service）
        reply.content = "__AGENT_PROCESSING__"  # 标记，由上层替换

    elif msg.msg_type == "image":
        reply.content = "暂不支持图片消息，请用文字告诉我您的需求"
    elif msg.msg_type == "voice":
        reply.content = "暂不支持语音消息，请用文字告诉我您的需求"
    else:
        reply.content = "暂不支持该消息类型"

    return reply
