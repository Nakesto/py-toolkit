# FastAPI Toolkit

A comprehensive toolkit for FastAPI applications that provides essential components for building robust APIs quickly and efficiently.

## Features

- **Dependency Injection**: Simple and powerful DI container for managing dependencies
- **Middleware**: Ready-to-use middleware for timeout, logging, error handling, and CORS
- **Database Connections**: Easy setup for MySQL and PostgreSQL with connection pooling
- **Response Helpers**: Consistent API response formatting with built-in models
- **Cache Connections**: Redis and Memcache support with simple interfaces
- **Easy Integration**: Designed to work seamlessly with existing FastAPI applications

## Installation

### Basic Installation

```bash
pip install fastapi-toolkit
```

### With Optional Dependencies

```bash
# For MySQL support
pip install fastapi-toolkit[mysql]

# For PostgreSQL support
pip install fastapi-toolkit[postgresql]

# For Redis support
pip install fastapi-toolkit[redis]

# For Memcache support
pip install fastapi-toolkit[memcache]

# For SQLAlchemy ORM support
pip install fastapi-toolkit[sqlalchemy]

# Install everything
pip install fastapi-toolkit[all]
```

## Quick Start

```python
from fastapi import FastAPI, Depends
from fastapi_toolkit import (
    setup_middleware,
    DatabaseManager,
    CacheManager,
    DIContainer,
    inject,
    success,
    error
)

# Create FastAPI app
app = FastAPI(title="My API")

# Setup middleware
setup_middleware(app, enable_cors=True, enable_logging=True)

# Setup database
db_manager = DatabaseManager()
db_manager.create_postgresql_connection(
    "main",
    host="localhost",
    user="postgres",
    password="password",
    database="mydb"
)

# Setup cache
cache_manager = CacheManager()
cache_manager.create_redis_connection("main", host="localhost")

# Dependency injection
container = DIContainer()
container.register_instance(DatabaseManager, db_manager)
container.register_instance(CacheManager, cache_manager)

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: DatabaseManager = Depends(inject(DatabaseManager))
):
    try:
        conn = db.get_connection("main")
        user = await conn.fetch_one(
            "SELECT * FROM users WHERE id = $1",
            (user_id,)
        )

        if user:
            return success(data=user, message="User found")
        else:
            return error(message="User not found")
    except Exception as e:
        return error(message=str(e))

@app.on_event("startup")
async def startup():
    await db_manager.connect_all()
    await cache_manager.connect_all()

@app.on_event("shutdown")
async def shutdown():
    await db_manager.disconnect_all()
    await cache_manager.disconnect_all()
```

## Components

### Dependency Injection

```python
from fastapi_toolkit import DIContainer, inject, injectable

# Create container
container = DIContainer()

# Register services
container.register_singleton(MyService, MyService())
container.register_transient(MyRepository, lambda: MyRepository())

# Use in FastAPI
@app.get("/")
async def endpoint(service: MyService = Depends(inject(MyService))):
    return service.do_something()

# Auto-injectable classes
@injectable
class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
```

### Middleware

```python
from fastapi_toolkit import (
    setup_middleware,
    TimeoutMiddleware,
    LoggingMiddleware,
    ErrorHandlerMiddleware,
    CORSMiddleware
)

# Quick setup with defaults
setup_middleware(app)

# Custom setup
app.add_middleware(TimeoutMiddleware, timeout_seconds=60)
app.add_middleware(LoggingMiddleware, log_request_body=True)
app.add_middleware(ErrorHandlerMiddleware, include_traceback=True)
CORSMiddleware.add_cors(app, allow_origins=["http://localhost:3000"])
```

### Database Connections

```python
from fastapi_toolkit import DatabaseManager, MySQLConnection, PostgreSQLConnection

# Database manager
db_manager = DatabaseManager()

# Add connections
db_manager.create_mysql_connection(
    "mysql_main",
    host="localhost",
    user="root",
    password="password",
    database="myapp"
)

db_manager.create_postgresql_connection(
    "postgres_main",
    host="localhost",
    user="postgres",
    password="password",
    database="myapp"
)

# Use connections
async def get_users():
    conn = db_manager.get_connection("postgres_main")
    users = await conn.fetch_all("SELECT * FROM users")
    return users

# Connect/disconnect all
await db_manager.connect_all()
await db_manager.disconnect_all()
```

### Response Helpers

```python
from fastapi_toolkit import (
    success,
    error,
    paginated,
    validation_error,
    not_found,
    unauthorized
)

@app.get("/users")
async def get_users():
    users = await get_users_from_db()
    return success(data=users, message="Users retrieved successfully")

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await get_user_from_db(user_id)
    if not user:
        return not_found(message="User not found")
    return success(data=user)

@app.get("/users/paginated")
async def get_users_paginated(page: int = 1, per_page: int = 10):
    users, total = await get_paginated_users(page, per_page)
    return paginated(data=users, page=page, per_page=per_page, total=total)
```

### Cache Connections

```python
from fastapi_toolkit import CacheManager, cache_result

# Cache manager
cache_manager = CacheManager()

# Add connections
cache_manager.create_redis_connection(
    "redis_main",
    host="localhost",
    port=6379,
    db=0
)

cache_manager.create_memcache_connection(
    "memcache_main",
    host="localhost",
    port=11211
)

# Use cache
async def cache_user_data(user_id: int, data: dict):
    cache = cache_manager.get_connection("redis_main")
    await cache.set(f"user:{user_id}", data, expire=3600)

async def get_cached_user_data(user_id: int):
    cache = cache_manager.get_connection("redis_main")
    return await cache.get(f"user:{user_id}")

# Cache decorator
@cache_result(cache_manager, "redis_main", expire=3600)
async def expensive_operation(param1: str, param2: int):
    # This result will be cached
    return await some_expensive_computation(param1, param2)
```

## Response Models

All response helpers return Pydantic models with consistent structure:

```json
{
  "success": true,
  "message": "Success",
  "timestamp": "2023-12-07T10:30:00Z",
  "data": {...},
  "errors": null,
  "meta": null
}
```

### Paginated Response

```json
{
  "success": true,
  "message": "Success",
  "timestamp": "2023-12-07T10:30:00Z",
  "data": [...],
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 100,
      "total_pages": 10,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

## Configuration

### Environment Variables

You can use environment variables for configuration:

```python
import os
from fastapi_toolkit import DatabaseManager

db_manager = DatabaseManager()
db_manager.create_postgresql_connection(
    "main",
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "myapp")
)
```

## Best Practices

1. **Use dependency injection** for better testability and maintainability
2. **Setup middleware early** in your application lifecycle
3. **Handle connections properly** using startup/shutdown events
4. **Use consistent response formats** with the provided response helpers
5. **Cache expensive operations** to improve performance
6. **Log requests and responses** for debugging and monitoring

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions, please file an issue on the GitHub repository.
