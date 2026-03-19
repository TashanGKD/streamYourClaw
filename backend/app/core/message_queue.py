"""Redis Streams wrapper for inter-agent communication."""

import json
from datetime import datetime, date
from typing import Any, AsyncIterator, Dict, List, Optional

import redis.asyncio as redis

from ..config import settings


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime and date objects."""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


class MessageQueue:
    """Redis Streams based message queue for agent communication."""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.redis_url
        self.prefix = settings.redis_stream_prefix
        self._redis: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Initialize Redis connection."""
        if self._redis is None:
            self._redis = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None

    def _get_stream_key(self, stream: str) -> str:
        """Get full stream key with prefix."""
        return f"{self.prefix}:{stream}"

    async def publish(
        self,
        stream: str,
        data: Dict[str, Any],
        max_len: int = 1000,
    ) -> str:
        """
        Publish a message to a stream.

        Args:
            stream: Stream name (without prefix)
            data: Message data to publish
            max_len: Maximum length of stream (old messages trimmed)

        Returns:
            Message ID
        """
        if self._redis is None:
            await self.connect()

        stream_key = self._get_stream_key(stream)
        message = json.dumps(data, cls=DateTimeEncoder)

        msg_id = await self._redis.xadd(
            stream_key,
            {"data": message},
            maxlen=max_len,
        )
        return msg_id

    async def read(
        self,
        streams: List[str],
        block: int = 5000,
        count: int = 10,
        last_ids: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Read messages from multiple streams.

        Args:
            streams: List of stream names (without prefix)
            block: Block time in milliseconds
            count: Maximum number of messages to read
            last_ids: Last read ID for each stream (default: new messages only)

        Returns:
            List of messages with stream, id, and data
        """
        if self._redis is None:
            await self.connect()

        stream_keys = [self._get_stream_key(s) for s in streams]

        if last_ids is None:
            ids = ["$" for _ in streams]  # New messages only
        else:
            ids = [last_ids.get(s, "$") for s in streams]

        results = await self._redis.xread(
            dict(zip(stream_keys, ids)),
            block=block,
            count=count,
        )

        messages = []
        if results:
            for stream_key, msgs in results:
                stream_name = stream_key.replace(f"{self.prefix}:", "")
                for msg_id, msg_data in msgs:
                    try:
                        data = json.loads(msg_data.get("data", "{}"))
                        messages.append({
                            "stream": stream_name,
                            "id": msg_id,
                            "data": data,
                        })
                    except json.JSONDecodeError:
                        continue

        return messages

    async def subscribe(
        self,
        streams: List[str],
        block: int = 5000,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Subscribe to streams and yield messages as they arrive.

        Args:
            streams: List of stream names to subscribe to
            block: Block time in milliseconds

        Yields:
            Message dictionaries
        """
        last_ids: Dict[str, str] = {}

        while True:
            messages = await self.read(streams, block=block, last_ids=last_ids)

            for msg in messages:
                last_ids[msg["stream"]] = msg["id"]
                yield msg

    async def get_stream_length(self, stream: str) -> int:
        """Get the number of messages in a stream."""
        if self._redis is None:
            await self.connect()

        stream_key = self._get_stream_key(stream)
        return await self._redis.xlen(stream_key)

    async def trim_stream(self, stream: str, max_len: int = 1000) -> int:
        """Trim a stream to maximum length. Returns number of messages removed."""
        if self._redis is None:
            await self.connect()

        stream_key = self._get_stream_key(stream)
        return await self._redis.xtrim(stream_key, maxlen=max_len)


# Singleton instance
_queue: Optional[MessageQueue] = None


async def get_message_queue() -> MessageQueue:
    """Get the singleton message queue instance."""
    global _queue
    if _queue is None:
        _queue = MessageQueue()
        await _queue.connect()
    return _queue