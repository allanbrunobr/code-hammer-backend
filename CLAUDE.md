# Development Guidelines

## Commands
- **Local development**: `python local.py` (runs uvicorn with reload)
- **Docker**: `docker-compose up` (builds and runs all services)
- **Run all tests**: `pytest`
- **Run specific test file**: `pytest tests/path/to/test_file.py`
- **Run specific test class**: `pytest tests/path/to/test_file.py::TestClassName`
- **Run specific test method**: `pytest tests/path/to/test_file.py::TestClassName::test_method_name`

## Code Style Guidelines
- **Architecture**: Clean architecture with domain, services, routers, repositories, entities, utils
- **Imports**: Standard library → third-party → local modules, alphabetically ordered
- **Types**: Always use type hints (from typing import Optional, Union, Any, List, Dict)
- **Naming**: Classes: PascalCase, functions/variables: snake_case, constants: ALL_CAPS
- **Models**: Use Pydantic for data validation and serialization
- **Error handling**: Catch specific exceptions, log appropriately, return clear error messages
- **Documentation**: Docstrings for classes and non-trivial functions, use Google style
- **Line length**: Max 100 characters per line
- **Spacing**: 4 spaces for indentation (no tabs)