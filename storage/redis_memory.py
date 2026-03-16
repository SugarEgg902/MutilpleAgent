import redis
from typing import Any, Optional
import json
from config import Config


class RedisMemory:
    def __init__(self):
        try:
            self.client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                decode_responses=True,
                socket_connect_timeout=2,  # 2秒连接超时
                socket_timeout=2  # 2秒操作超时
            )
            # 测试连接
            self.client.ping()
            self.enabled = True
            print("[Redis] 连接成功")
        except Exception as e:
            print(f"[Redis] 连接失败: {e}，使用内存存储")
            self.enabled = False
            self.memory_store = {}  # 内存存储作为备份

    def store(self, key: str, value: Any, expire: int = 3600):
        """存储短期记忆，默认1小时过期"""
        try:
            if self.enabled:
                self.client.setex(key, expire, json.dumps(value, ensure_ascii=False))
            else:
                # 使用内存存储
                self.memory_store[key] = value
        except Exception as e:
            print(f"[Redis] 存储失败: {e}，使用内存存储")
            self.memory_store[key] = value

    def retrieve(self, key: str) -> Optional[Any]:
        """检索记忆"""
        try:
            if self.enabled:
                data = self.client.get(key)
                return json.loads(data) if data else None
            else:
                return self.memory_store.get(key)
        except Exception as e:
            print(f"[Redis] 检索失败: {e}")
            return self.memory_store.get(key)

    def delete(self, key: str):
        """删除记忆"""
        try:
            if self.enabled:
                self.client.delete(key)
            else:
                self.memory_store.pop(key, None)
        except Exception as e:
            print(f"[Redis] 删除失败: {e}")
            self.memory_store.pop(key, None)

    def store_conversation(self, session_id: str, message: dict):
        """存储对话历史"""
        try:
            if self.enabled:
                key = f"conversation:{session_id}"
                self.client.rpush(key, json.dumps(message, ensure_ascii=False))
                self.client.expire(key, 7200)  # 2小时
            else:
                key = f"conversation:{session_id}"
                if key not in self.memory_store:
                    self.memory_store[key] = []
                self.memory_store[key].append(message)
        except Exception as e:
            print(f"[Redis] 存储对话失败: {e}")

    def get_conversation(self, session_id: str) -> list:
        """获取对话历史"""
        try:
            if self.enabled:
                key = f"conversation:{session_id}"
                messages = self.client.lrange(key, 0, -1)
                return [json.loads(msg) for msg in messages]
            else:
                key = f"conversation:{session_id}"
                return self.memory_store.get(key, [])
        except Exception as e:
            print(f"[Redis] 获取对话失败: {e}")
            return []
