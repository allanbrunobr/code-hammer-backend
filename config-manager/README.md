# Config Manager

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-green)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-blue)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

A comprehensive configuration management service that provides a RESTful API for billing, subscription, user, and integration management.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Development](#-development)
  - [Running Locally](#running-locally)
  - [Docker Setup](#docker-setup)
  - [Database Setup](#database-setup)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Adding New Features](#-adding-new-features)
  - [Creating DTOs](#creating-dtos)
  - [Adding Services](#adding-services)
  - [Creating Routes](#creating-routes)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)
- [References](#-references)

## 🚀 Features

- User authentication and authorization
- Billing and subscription management
- Integration with external services
- Plan management and configuration
- Code analysis capabilities
- Robust API with comprehensive error handling

## 🏗 Architecture

This project follows Clean Architecture principles with clear separation of concerns:

- **Domain Layer**: Core business logic and entities
- **Service Layer**: Application services implementing business rules
- **Repository Layer**: Data access layer
- **API Layer**: RESTful endpoints using FastAPI
- **Adapter Layer**: External integrations and DTOs

## 💻 Tech Stack

- **Backend**: Python 3.8+
- **Web Framework**: FastAPI
- **ORM**: SQLAlchemy
- **ASGI Server**: Uvicorn
- **Authentication**: JWT
- **Database**: PostgreSQL
- **Containerization**: Docker
- **Testing**: pytest

## 🏁 Getting Started

### Prerequisites

- Python 3.8 or higher
- Docker (optional for containerized deployment)
- PostgreSQL (or compatible database)

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/your-organization/config-manager.git
   cd config-manager
   ```

2. Create and activate a virtual environment:
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Configuration

#### Environment Variables

Configure the application using environment variables or create a `.env` file in the project root:

```
# Database configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Authentication
SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# API Configuration
API_PREFIX=/api/v1
API_DEBUG=True

# Logging
LOG_LEVEL=INFO
```

#### API Keys Configuration

API keys can be configured in two ways:

1. **JSON file** - Create an `api-keys.json` file:
   ```json
   [
     {"value": "your-api-key", "name": "ServiceName"}
   ]
   ```

2. **Environment variables**:
   - `APPLICATION_API_KEYS`: Path to JSON file with API keys
   - `APPLICATION_API_KEYS_RAW`: Base64 encoded JSON with API keys

## 💻 Development

### Running Locally

To run the application in development mode with hot reload:

```sh
python local.py
```

The server will start at http://localhost:5000 with:
- API documentation available at http://localhost:5000/docs
- Health check endpoint at http://localhost:5000/api/v1/actuator/health/liveness

### Docker Setup

Build and run using Docker:

```sh
# Build the Docker image
docker build -t config-manager .

# Run the container
docker run -d -p 5000:80 --env-file .env config-manager
```

Alternatively, use Docker Compose:

```sh
docker-compose up -d
```

### Database Setup

Initialize database tables:

```sh
python create_tables.py
```

## 📚 API Documentation

Once the application is running, comprehensive API documentation is available at:

- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc

## 📁 Project Structure

```
config-manager/
├── keys/                  # Service account keys and credentials
├── src/                   # Main application code
│   ├── adapters/          # External adapters and DTOs
│   │   └── dtos/          # Data Transfer Objects
│   ├── core/              # Core application components
│   │   └── db/            # Database configuration
│   ├── domain/            # Business domain models
│   ├── entities/          # Entity definitions
│   ├── repositories/      # Data access layer
│   ├── routers/           # API endpoints
│   ├── services/          # Business logic implementation
│   └── utils/             # Utility functions
├── tests/                 # Test suite
├── Dockerfile             # Docker configuration
├── requirements.txt       # Python dependencies
├── main.py                # Application entry point
└── local.py               # Development server script
```

## 🛠 Adding New Features

### Creating DTOs

1. Create a new file in `src/adapters/dtos/` with your DTO model:
   ```python
   from pydantic import BaseModel
   
   class NewFeatureDTO(BaseModel):
       name: str
       description: str = None
       active: bool = True
   ```

2. Export it in `src/adapters/dtos/__init__.py`:
   ```python
   from .new_feature import NewFeatureDTO as NewFeatureDTO
   ```

### Adding Services

1. Create a service in `src/services/`:
   ```python
   from ..adapters.dtos import NewFeatureDTO
   
   class NewFeatureService:
       def get_feature(self, feature_id: str) -> NewFeatureDTO:
           # Implementation
           pass
   ```

2. Export it in `src/services/__init__.py`:
   ```python
   from .new_feature import NewFeatureService as NewFeatureService
   ```

### Creating Routes

1. Create a router in `src/routers/`:
   ```python
   from fastapi import APIRouter
   from ..adapters.dtos import NewFeatureDTO
   from ..services import NewFeatureService
   
   router = APIRouter(
       prefix="/features",
       tags=["features"]
   )
   service = NewFeatureService()
   
   @router.get("/{feature_id}")
   def get_feature(feature_id: str) -> NewFeatureDTO:
       return service.get_feature(feature_id)
   ```

2. Register the router in `src/main.py`:
   ```python
   from .routers import new_feature
   
   # Add to router registration
   api_router.include_router(new_feature.router)
   ```

## 🧪 Testing

Run the test suite:

```sh
# Run all tests
pytest

# Run specific tests
pytest tests/path/to/test_file.py
pytest tests/path/to/test_file.py::TestClassName
pytest tests/path/to/test_file.py::TestClassName::test_method_name
```

## 🤝 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📚 References

- [Python Documentation](https://www.python.org/doc/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)