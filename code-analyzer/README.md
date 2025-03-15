# Code Analyzer

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-green)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-latest-green)
![Uvicorn](https://img.shields.io/badge/Uvicorn-latest-green)

A powerful code analysis service built with FastAPI that leverages AI models for code understanding, review, and conversation.

## Features

- **Code Analysis**: Analyze code repositories from various sources
- **AI-Powered Reviews**: Generate intelligent code reviews
- **Comment Integration**: Post comments to GitHub, GitLab, Bitbucket, and Azure DevOps
- **Conversation Interface**: Interact with the analysis through a conversation API
- **Authentication & Authorization**: Secure API access

## Tech Stack

- **Backend**: Python 3.9+, FastAPI, SQLAlchemy
- **Server**: Uvicorn
- **Database**: Supports various database backends through SQLAlchemy
- **AI Integration**: Connects to various LLM providers
- **Container**: Docker support

## Installation

### Prerequisites

- Python 3.9 or higher
- Docker (optional, for containerized deployment)

### Local Development Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd code-analyzer
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure API keys (see Configuration section)

5. Run the development server:

```bash
python local.py
```

The application will be accessible at http://localhost:5000 with automatic reloading and debug logs enabled.

### Docker Setup

1. Build the Docker image:

```bash
docker build -t code-analyzer .
```

2. Run the container:

```bash
docker run -d -p 5000:80 code-analyzer
```

## Configuration

### API Keys

API keys can be configured in two ways:

#### JSON Configuration File

Create an `api-keys.json` file in the project root:

```json
[
  {"value": "your-api-key", "name": "KeyName"}
]
```

Set the environment variable:
```
APPLICATION_API_KEYS=api-keys.json
```

#### Base64-Encoded Environment Variable

Alternatively, encode the JSON configuration in Base64 and set:

```
APPLICATION_API_KEYS_RAW=<base64-encoded-json>
```

### Environment Variables

- `APPLICATION_URL`: Base URL for the application
- `APPLICATION_API_KEYS`: Path to API keys JSON file
- `APPLICATION_API_KEYS_RAW`: Base64-encoded API keys JSON
- Additional environment variables for database, LLM integrations, etc.

## API Documentation

When the server is running, access the interactive API documentation at:

- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc

## Health Checks

- Liveness: http://localhost:5000/api/v1/actuator/health/liveness

## Project Structure

The project follows a clean architecture pattern:

```
code-analyzer/
├── src/                  # Main source code
│   ├── adapters/         # External interfaces adapters
│   ├── core/             # Core business logic
│   ├── domain/           # Domain models and logic
│   ├── entities/         # Data entities
│   ├── repositories/     # Data access layer
│   ├── routers/          # API routes
│   ├── services/         # Service layer
│   ├── utils/            # Utility functions
│   └── main.py           # FastAPI application setup
├── tests/                # Test suite
├── Dockerfile            # Docker configuration
├── local.py              # Local development runner
├── main.py               # Production entry point
├── pytest.ini            # PyTest configuration
└── requirements.txt      # Project dependencies
```

## Adding New Features

### Creating a New Route

1. **Create a DTO** in `src/adapters/dtos/`:

```python
from pydantic import BaseModel

class ItemDTO(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None
```

2. **Create a Service** in `src/services/`:

```python
from ..adapters.dtos import ItemDTO

class ItemService:
    def all(self) -> ItemDTO:
        item = {
            "name": "Sample item",
            "description": "This is just a demo item",
            "price": 99.99,
            "tax": 10.0
        }
        return ItemDTO(**item)
```

3. **Create a Router** in `src/routers/`:

```python
from fastapi import APIRouter
from ..adapters.dtos import ItemDTO
from ..services import ItemService

router = APIRouter(
    prefix="/items",
    tags=["items"]
)
item = ItemService()

@router.get("/")
def root() -> ItemDTO:
    return item.all()
```

4. **Register the Router** in `src/main.py`:

```python
from .routers import item
# ...
api_router.include_router(item.router)
```

## Testing

Run all tests:

```bash
pytest
```

Run specific tests:

```bash
# Run tests in a specific file
pytest tests/path/to/test_file.py

# Run tests in a specific class
pytest tests/path/to/test_file.py::TestClassName

# Run a specific test method
pytest tests/path/to/test_file.py::TestClassName::test_method_name
```

## Contributing

Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute to this project.

## License

[License information]

## References

- [Python Docs](https://www.python.org/doc/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)