# FastAPI Toolkit - Quick Start Guide

## Installation

### From Source (Development)
```bash
# Clone the repository
git clone https://github.com/yourusername/fastapi-toolkit.git
cd fastapi-toolkit

# Install in development mode
pip install -e .

# Or install with all dependencies
pip install -e ".[all]"
```

### From PyPI (When Published)
```bash
# Basic installation
pip install fastapi-toolkit

# With all optional dependencies
pip install fastapi-toolkit[all]
```

## Building the Package

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI (when ready)
twine upload dist/*
```

## Running the Example

1. **Setup Database (PostgreSQL)**
   ```bash
   # Using Docker
   docker run --name postgres-example -e POSTGRES_PASSWORD=password -e POSTGRES_DB=example_db -p 5432:5432 -d postgres:13
   ```

2. **Setup Cache (Redis)**
   ```bash
   # Using Docker
   docker run --name redis-example -p 6379:6379 -d redis:7-alpine
   ```

3. **Install Dependencies**
   ```bash
   pip install fastapi-toolkit[postgresql,redis]
   ```

4. **Run the Example App**
   ```bash
   python example_app.py
   ```

5. **Test the API**
   ```bash
   # Health check
   curl http://localhost:8000/health
   
   # Create a user
   curl -X POST http://localhost:8000/users \
     -H "Content-Type: application/json" \
     -d '{"name": "John Doe", "email": "john@example.com", "age": 30}'
   
   # Get users
   curl http://localhost:8000/users
   
   # Get specific user
   curl http://localhost:8000/users/1
   ```

## Environment Variables

Create a `.env` file for configuration:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=example_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## API Documentation

Once the example app is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Package Structure

```
fastapi-toolkit/
├── fastapi_toolkit/           # Main package
│   ├── __init__.py           # Package exports
│   ├── dependency_injection.py  # DI container
│   ├── middleware.py         # Middleware components
│   ├── database.py          # Database connections
│   ├── response.py          # Response helpers
│   └── cache.py             # Cache connections
├── example_app.py           # Example application
├── README.md               # Full documentation
├── QUICKSTART.md          # This file
├── requirements.txt       # Dependencies
├── pyproject.toml        # Modern Python packaging
├── setup.py             # Legacy packaging
└── LICENSE             # MIT License
```

## Next Steps

1. **Customize the toolkit** for your specific needs
2. **Add tests** using pytest
3. **Publish to PyPI** when ready
4. **Create documentation** website
5. **Add CI/CD** pipeline

## Support

For issues and questions:
- Check the [README.md](README.md) for detailed documentation
- Look at the [example_app.py](example_app.py) for usage examples
- File issues on GitHub repository