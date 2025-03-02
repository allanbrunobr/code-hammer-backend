# Code Processor

A FastAPI-based service for processing and analyzing code, part of the larger code-analyzer system.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-latest-orange.svg)
![Uvicorn](https://img.shields.io/badge/Uvicorn-latest-blue.svg)

## Overview

The Code Processor service provides a RESTful API for analyzing code and processing requests. It is designed using clean architecture principles, with clear separation between domain logic, application services, and infrastructure adapters.

## Features

- Code analysis processing
- User preference management
- Message processing
- PubSub integration
- API client adapter for external services

## Tech Stack

- **Backend**: Python 3.9+, FastAPI, SQLAlchemy, Uvicorn
- **Architecture**: Clean architecture with domain, services, routers, repositories, entities, and utils
- **Testing**: PyTest for unit and integration tests
- **Containerization**: Docker

## Project Structure

```
code-processor/
├── src/
│   ├── adapters/         # External interfaces and DTOs
│   │   └── dtos/         # Data Transfer Objects
│   ├── core/             # Core application components
│   │   └── db/           # Database configuration
│   ├── domain/           # Business logic and entities
│   ├── entities/         # Domain entities
│   ├── routers/          # API endpoints
│   ├── services/         # Application services
│   └── utils/            # Utility functions
├── tests/                # Test suite
├── Dockerfile            # Docker configuration
├── local.py              # Local development script
├── main.py               # Application entry point
└── requirements.txt      # Project dependencies
```

## Configuration

### API Keys

API Keys are required for accessing the API. These can be configured in two ways:

1. **JSON Format**: Create an `api-keys.json` file in the project root with the following structure:
   ```json
   [
     {"value": "your-api-key", "name": "Key Name"}
   ]
   ```

2. **Environment Variables**:
   - For JSON format: `APPLICATION_API_KEYS` - Path to the JSON file containing API keys
   - For RAW format: `APPLICATION_API_KEYS_RAW` - Base64 encoded JSON containing API keys

## Running Locally

### Using Python

```sh
python local.py
```

This will start the application in development mode with auto-reload enabled on port 5000.

### Using Docker

1. Build the Docker image:
   ```sh
   docker build -t code-processor .
   ```

2. Run the container:
   ```sh
   docker run -d -p 5000:80 code-processor
   ```

3. Or, using Docker Compose:
   ```sh
   docker-compose up
   ```

## API Endpoints

### Health Checks

- **Liveness**: `GET /api/v1/actuator/health/liveness`

### Documentation

- **Swagger UI**: `GET /docs`
- **OpenAPI Spec**: `GET /openapi.json`

## Development

### Adding New Routes

1. Create a Data Transfer Object (DTO) in `src/adapters/dtos/`
2. Create a Service in `src/services/`
3. Create a Router in `src/routers/`
4. Register the router in `src/main.py`

### Running Tests

```sh
# Run all tests
pytest

# Run a specific test file
pytest tests/path/to/test_file.py

# Run a specific test class
pytest tests/path/to/test_file.py::TestClassName

# Run a specific test method
pytest tests/path/to/test_file.py::TestClassName::test_method_name
```

## Contributing

Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute to this project.

## References

- [Python Documentation](https://www.python.org/doc/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Uvicorn Documentation](https://www.uvicorn.org/)