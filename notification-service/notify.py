"""
Notification Service - Python API
为AI Agent任务提供主动通知能力，支持飞书、Webhook等多种渠道。
"""

import os
import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum


class NotificationChannel(Enum):
    """通知渠道类型"""
    FEISHU = "feishu"
    WEBHOOK = "webhook"
    DINGTALK = "dingtalk"


@dataclass
class NotificationMessage:
    """通知消息结构"""
    title: str
    content: str
    url: Optional[str] = None
    level: str = "info"  # info, warning, error, success
    
    def to_feishu_card(self) -> Dict[str, Any]:
        """转换为飞书卡片格式"""
        color_map = {
            "info": "blue",
            "warning": "orange", 
            "error": "red",
            "success": "green"
        }
        
        card = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": self.title
                    },
                    "template": color_map.get(self.level, "blue")
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": self.content
                        }
                    }
                ]
            }
        }
        
        if self.url:
            card["card"]["elements"].append({
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "plain_text",
                            "content": "查看详情"
                        },
                        "url": self.url,
                        "type": "primary"
                    }
                ]
            })
        
        return card
    
    def to_text(self) -> str:
        """转换为纯文本格式"""
        prefix_map = {
            "info": "【信息】",
            "warning": "【警告】",
            "error": "【错误】",
            "success": "【成功】"
        }
        prefix = prefix_map.get(self.level, "【信息】")
        return f"{prefix}{self.title}: {self.content}"


class NotificationService:
    """通知服务主类"""
    
    FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/{key}"
    
    def __init__(self, feishu_key: Optional[str] = None):
        """
        初始化通知服务
        
        Args:
            feishu_key: 飞书机器人Webhook密钥，默认从环境变量读取
        """
        self.feishu_key = feishu_key or os.environ.get("FEISHU_WEBHOOK_KEY")
    
    def send_feishu(self, message: Union[str, NotificationMessage], 
                    webhook_key: Optional[str] = None) -> bool:
        """
        发送飞书通知
        
        Args:
            message: 消息内容(字符串或NotificationMessage对象)
            webhook_key: 飞书Webhook密钥，默认使用初始化时的key
            
        Returns:
            bool: 发送是否成功
            
        Raises:
            ValueError: 未提供webhook_key
        """
        key = webhook_key or self.feishu_key
        if not key:
            raise ValueError("必须提供飞书Webhook密钥，可通过参数或环境变量FEISHU_WEBHOOK_KEY设置")
        
        # 转换消息格式
        if isinstance(message, str):
            msg_obj = NotificationMessage(
                title="通知",
                content=message,
                level="info"
            )
        else:
            msg_obj = message
        
        # 构建请求
        url = self.FEISHU_WEBHOOK_URL.format(key=key)
        payload = msg_obj.to_feishu_card()
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('code') == 0
                
        except urllib.error.HTTPError as e:
            print(f"飞书通知HTTP错误: {e.code} - {e.reason}")
            return False
        except urllib.error.URLError as e:
            print(f"飞书通知URL错误: {e.reason}")
            return False
        except Exception as e:
            print(f"飞书通知发送失败: {e}")
            return False
    
    def send_webhook(self, url: str, payload: Dict[str, Any],
                     headers: Optional[Dict[str, str]] = None) -> bool:
        """
        发送通用Webhook通知
        
        Args:
            url: Webhook URL
            payload: 请求体数据
            headers: 自定义请求头
            
        Returns:
            bool: 发送是否成功
        """
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers=default_headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                return 200 <= response.status < 300
                
        except Exception as e:
            print(f"Webhook通知发送失败: {e}")
            return False
    
    def notify_task_complete(self, task_name: str, result: str,
                            duration: Optional[str] = None) -> bool:
        """
        发送任务完成通知
        
        Args:
            task_name: 任务名称
            result: 任务结果摘要
            duration: 执行时长(可选)
            
        Returns:
            bool: 发送是否成功
        """
        content = result
        if duration:
            content += f"\n执行时长: {duration}"
        
        message = NotificationMessage(
            title=f"任务完成: {task_name}",
            content=content,
            level="success"
        )
        
        return self.send_feishu(message)
    
    def notify_task_error(self, task_name: str, error: str) -> bool:
        """
        发送任务错误通知
        
        Args:
            task_name: 任务名称
            error: 错误信息
            
        Returns:
            bool: 发送是否成功
        """
        message = NotificationMessage(
            title=f"任务失败: {task_name}",
            content=error,
            level="error"
        )
        
        return self.send_feishu(message)
    
    def notify_alert(self, title: str, message: str,
                    level: str = "warning") -> bool:
        """
        发送告警通知
        
        Args:
            title: 告警标题
            message: 告警内容
            level: 告警级别 (info/warning/error/success)
            
        Returns:
            bool: 发送是否成功
        """
        msg = NotificationMessage(
            title=title,
            content=message,
            level=level
        )
        
        return self.send_feishu(msg)


def send_notification(message: str, level: str = "info",
                     webhook_key: Optional[str] = None) -> bool:
    """
    快速发送通知的便捷函数
    
    Args:
        message: 消息内容
        level: 消息级别 (info/warning/error/success)
        webhook_key: 飞书Webhook密钥
        
    Returns:
        bool: 发送是否成功
        
    Example:
        >>> send_notification("任务完成啦！")
        True
        >>> send_notification("磁盘空间不足", level="warning")
        True
    """
    service = NotificationService(webhook_key)
    return service.send_feishu(message)


if __name__ == "__main__":
    # 简单测试
    import sys
    
    if len(sys.argv) > 1:
        msg = sys.argv[1]
        success = send_notification(msg)
        print(f"通知发送{'成功' if success else '失败'}")
    else:
        print("用法: python notify.py '消息内容'")
