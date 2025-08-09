"""Setup configuration for FastAPI Toolkit package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="fastapi-toolkit",
    version="1.0.0",
    author="FastAPI Toolkit",
    author_email="contact@fastapi-toolkit.com",
    description="A comprehensive toolkit for FastAPI applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fastapi-toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: FastAPI",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.0.0",
        "starlette>=0.27.0",
    ],
    extras_require={
        "mysql": ["aiomysql>=0.2.0"],
        "postgresql": ["asyncpg>=0.29.0"],
        "sqlalchemy": ["sqlalchemy[asyncio]>=2.0.0"],
        "redis": ["aioredis>=2.0.0"],
        "memcache": ["aiomcache>=0.7.0"],
        "auth": [
            "python-jose[cryptography]>=3.3.0",
            "passlib[bcrypt]>=1.7.4",
        ],
        "all": [
            "aiomysql>=0.2.0",
            "asyncpg>=0.29.0",
            "sqlalchemy[asyncio]>=2.0.0",
            "aioredis>=2.0.0",
            "aiomcache>=0.7.0",
            "python-jose[cryptography]>=3.3.0",
            "passlib[bcrypt]>=1.7.4",
            "python-multipart>=0.0.6",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    keywords="fastapi, toolkit, middleware, database, cache, dependency-injection",
)