"""Cache connection utilities for FastAPI applications."""

import json
import pickle
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

try:
    import aioredis
except ImportError:
    aioredis = None

try:
    import aiomcache
except ImportError:
    aiomcache = None


class CacheConnection(ABC):
    """Abstract base class for cache connections."""
    
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self._client = None
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish cache connection."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close cache connection."""
        pass
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        pass
    
    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """Set value with optional expiration."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete key."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all keys."""
        pass


class RedisConnection(CacheConnection):
    """Redis cache connection using aioredis."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0,
        encoding: str = "utf-8",
        serializer: str = "json",  # "json" or "pickle"
        **kwargs
    ):
        if aioredis is None:
            raise ImportError("aioredis is required for Redis connections. Install with: pip install aioredis")
        
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.encoding = encoding
        self.serializer = serializer
        super().__init__(**kwargs)
    
    async def connect(self) -> None:
        """Create Redis connection."""
        self._client = aioredis.Redis(
            host=self.host,
            port=self.port,
            password=self.password,
            db=self.db,
            encoding=self.encoding,
            decode_responses=True,
            **self.kwargs
        )
        # Test connection
        await self._client.ping()
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
    
    def _serialize(self, value: Any) -> str:
        """Serialize value for storage."""
        if self.serializer == "json":
            return json.dumps(value)
        elif self.serializer == "pickle":
            return pickle.dumps(value).hex()
        else:
            return str(value)
    
    def _deserialize(self, value: str) -> Any:
        """Deserialize value from storage."""
        if value is None:
            return None
        
        try:
            if self.serializer == "json":
                return json.loads(value)
            elif self.serializer == "pickle":
                return pickle.loads(bytes.fromhex(value))
            else:
                return value
        except Exception:
            return value
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        value = await self._client.get(key)
        return self._deserialize(value)
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """Set value with optional expiration."""
        serialized_value = self._serialize(value)
        result = await self._client.set(key, serialized_value, ex=expire)
        return result is True
    
    async def delete(self, key: str) -> bool:
        """Delete key."""
        result = await self._client.delete(key)
        return result > 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        result = await self._client.exists(key)
        return result > 0
    
    async def clear(self) -> bool:
        """Clear all keys in current database."""
        result = await self._client.flushdb()
        return result is True
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment key by amount."""
        return await self._client.incrby(key, amount)
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key."""
        result = await self._client.expire(key, seconds)
        return result is True
    
    async def ttl(self, key: str) -> int:
        """Get time to live for key."""
        return await self._client.ttl(key)


class MemcacheConnection(CacheConnection):
    """Memcache connection using aiomcache."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 11211,
        serializer: str = "json",  # "json" or "pickle"
        **kwargs
    ):
        if aiomcache is None:
            raise ImportError("aiomcache is required for Memcache connections. Install with: pip install aiomcache")
        
        self.host = host
        self.port = port
        self.serializer = serializer
        super().__init__(**kwargs)
    
    async def connect(self) -> None:
        """Create Memcache connection."""
        self._client = aiomcache.Client(self.host, self.port, **self.kwargs)
    
    async def disconnect(self) -> None:
        """Close Memcache connection."""
        if self._client:
            self._client.close()
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage."""
        if self.serializer == "json":
            return json.dumps(value).encode('utf-8')
        elif self.serializer == "pickle":
            return pickle.dumps(value)
        else:
            return str(value).encode('utf-8')
    
    def _deserialize(self, value: bytes) -> Any:
        """Deserialize value from storage."""
        if value is None:
            return None
        
        try:
            if self.serializer == "json":
                return json.loads(value.decode('utf-8'))
            elif self.serializer == "pickle":
                return pickle.loads(value)
            else:
                return value.decode('utf-8')
        except Exception:
            return value
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value by key."""
        value = await self._client.get(key.encode('utf-8'))
        return self._deserialize(value)
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """Set value with optional expiration."""
        serialized_value = self._serialize(value)
        result = await self._client.set(
            key.encode('utf-8'),
            serialized_value,
            exptime=expire or 0
        )
        return result is True
    
    async def delete(self, key: str) -> bool:
        """Delete key."""
        result = await self._client.delete(key.encode('utf-8'))
        return result is True
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        value = await self._client.get(key.encode('utf-8'))
        return value is not None
    
    async def clear(self) -> bool:
        """Clear all keys (flush all)."""
        result = await self._client.flush_all()
        return result is True


class CacheManager:
    """Cache manager to handle multiple cache connections."""
    
    def __init__(self):
        self._connections: Dict[str, CacheConnection] = {}
    
    def add_connection(self, name: str, connection: CacheConnection) -> None:
        """Add a cache connection."""
        self._connections[name] = connection
    
    def get_connection(self, name: str) -> CacheConnection:
        """Get a cache connection by name."""
        if name not in self._connections:
            raise ValueError(f"Cache connection '{name}' not found")
        return self._connections[name]
    
    async def connect_all(self) -> None:
        """Connect all registered caches."""
        for connection in self._connections.values():
            await connection.connect()
    
    async def disconnect_all(self) -> None:
        """Disconnect all registered caches."""
        for connection in self._connections.values():
            await connection.disconnect()
    
    def create_redis_connection(
        self,
        name: str,
        host: str = "localhost",
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0,
        **kwargs
    ) -> RedisConnection:
        """Create and register a Redis connection."""
        conn = RedisConnection(host, port, password, db, **kwargs)
        self.add_connection(name, conn)
        return conn
    
    def create_memcache_connection(
        self,
        name: str,
        host: str = "localhost",
        port: int = 11211,
        **kwargs
    ) -> MemcacheConnection:
        """Create and register a Memcache connection."""
        conn = MemcacheConnection(host, port, **kwargs)
        self.add_connection(name, conn)
        return conn


# Decorator for caching function results
def cache_result(
    cache_manager: CacheManager,
    connection_name: str = "default",
    expire: Optional[int] = None,
    key_prefix: str = ""
):
    """Decorator to cache function results."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            if args:
                key_parts.extend(str(arg) for arg in args)
            if kwargs:
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(filter(None, key_parts))
            
            # Try to get from cache
            cache = cache_manager.get_connection(connection_name)
            cached_result = await cache.get(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, expire)
            
            return result
        
        return wrapper
    return decorator