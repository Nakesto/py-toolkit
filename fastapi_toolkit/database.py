"""Database connection utilities for FastAPI applications."""

import asyncio
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, Optional

try:
    import aiomysql
except ImportError:
    aiomysql = None

try:
    import asyncpg
except ImportError:
    asyncpg = None

try:
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker
except ImportError:
    AsyncSession = None
    create_async_engine = None
    sessionmaker = None


class DatabaseConnection(ABC):
    """Abstract base class for database connections."""
    
    def __init__(self, connection_string: str, **kwargs):
        self.connection_string = connection_string
        self.kwargs = kwargs
        self._pool = None
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish database connection."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    async def execute(self, query: str, params: Optional[tuple] = None) -> Any:
        """Execute a query."""
        pass
    
    @abstractmethod
    async def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict]:
        """Fetch one record."""
        pass
    
    @abstractmethod
    async def fetch_all(self, query: str, params: Optional[tuple] = None) -> list:
        """Fetch all records."""
        pass


class MySQLConnection(DatabaseConnection):
    """MySQL database connection using aiomysql."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "",
        **kwargs
    ):
        if aiomysql is None:
            raise ImportError("aiomysql is required for MySQL connections. Install with: pip install aiomysql")
        
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        super().__init__("", **kwargs)
    
    async def connect(self) -> None:
        """Create MySQL connection pool."""
        self._pool = await aiomysql.create_pool(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.database,
            **self.kwargs
        )
    
    async def disconnect(self) -> None:
        """Close MySQL connection pool."""
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool."""
        async with self._pool.acquire() as conn:
            yield conn
    
    async def execute(self, query: str, params: Optional[tuple] = None) -> Any:
        """Execute a query."""
        async with self.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                await conn.commit()
                return cursor.rowcount
    
    async def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict]:
        """Fetch one record."""
        async with self.get_connection() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchone()
    
    async def fetch_all(self, query: str, params: Optional[tuple] = None) -> list:
        """Fetch all records."""
        async with self.get_connection() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchall()


class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL database connection using asyncpg."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        user: str = "postgres",
        password: str = "",
        database: str = "postgres",
        **kwargs
    ):
        if asyncpg is None:
            raise ImportError("asyncpg is required for PostgreSQL connections. Install with: pip install asyncpg")
        
        connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        super().__init__(connection_string, **kwargs)
    
    async def connect(self) -> None:
        """Create PostgreSQL connection pool."""
        self._pool = await asyncpg.create_pool(self.connection_string, **self.kwargs)
    
    async def disconnect(self) -> None:
        """Close PostgreSQL connection pool."""
        if self._pool:
            await self._pool.close()
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool."""
        async with self._pool.acquire() as conn:
            yield conn
    
    async def execute(self, query: str, params: Optional[tuple] = None) -> Any:
        """Execute a query."""
        async with self.get_connection() as conn:
            return await conn.execute(query, *(params or ()))
    
    async def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict]:
        """Fetch one record."""
        async with self.get_connection() as conn:
            row = await conn.fetchrow(query, *(params or ()))
            return dict(row) if row else None
    
    async def fetch_all(self, query: str, params: Optional[tuple] = None) -> list:
        """Fetch all records."""
        async with self.get_connection() as conn:
            rows = await conn.fetch(query, *(params or ()))
            return [dict(row) for row in rows]


class SQLAlchemyConnection:
    """SQLAlchemy async connection wrapper."""
    
    def __init__(self, database_url: str, **engine_kwargs):
        if create_async_engine is None:
            raise ImportError("sqlalchemy[asyncio] is required. Install with: pip install sqlalchemy[asyncio]")
        
        self.database_url = database_url
        self.engine = create_async_engine(database_url, **engine_kwargs)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def disconnect(self) -> None:
        """Close the engine."""
        await self.engine.dispose()
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async session."""
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


class DatabaseManager:
    """Database manager to handle multiple database connections."""
    
    def __init__(self):
        self._connections: Dict[str, DatabaseConnection] = {}
    
    def add_connection(self, name: str, connection: DatabaseConnection) -> None:
        """Add a database connection."""
        self._connections[name] = connection
    
    def get_connection(self, name: str) -> DatabaseConnection:
        """Get a database connection by name."""
        if name not in self._connections:
            raise ValueError(f"Connection '{name}' not found")
        return self._connections[name]
    
    async def connect_all(self) -> None:
        """Connect all registered databases."""
        tasks = [conn.connect() for conn in self._connections.values()]
        await asyncio.gather(*tasks)
    
    async def disconnect_all(self) -> None:
        """Disconnect all registered databases."""
        tasks = [conn.disconnect() for conn in self._connections.values()]
        await asyncio.gather(*tasks)
    
    def create_mysql_connection(
        self,
        name: str,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "",
        **kwargs
    ) -> MySQLConnection:
        """Create and register a MySQL connection."""
        conn = MySQLConnection(host, port, user, password, database, **kwargs)
        self.add_connection(name, conn)
        return conn
    
    def create_postgresql_connection(
        self,
        name: str,
        host: str = "localhost",
        port: int = 5432,
        user: str = "postgres",
        password: str = "",
        database: str = "postgres",
        **kwargs
    ) -> PostgreSQLConnection:
        """Create and register a PostgreSQL connection."""
        conn = PostgreSQLConnection(host, port, user, password, database, **kwargs)
        self.add_connection(name, conn)
        return conn