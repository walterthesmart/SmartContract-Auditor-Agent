from setuptools import setup, find_packages

setup(
    name="hedera_audit_ai",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn>=0.34.0",
        "python-dotenv>=1.1.0",
        "slither-analyzer>=0.10.0",
        "langgraph>=0.4.5",
        "groq>=0.5.0",
        "hedera-sdk-py>=2.19.0",
        "reportlab>=4.4.0",
        "pygments>=2.17.0",
        "python-multipart>=0.0.9",
        "pydantic>=2.10.0",
        "xxhash>=3.5.0",  # Required for HCS-10 integration
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "isort>=5.12.0",
            "mypy>=1.7.0",
            "flake8>=6.1.0",
        ],
    },
    python_requires=">=3.10",
)
