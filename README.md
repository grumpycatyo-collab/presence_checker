# iot_student_presence_tool

A FastAPI application with ESP32 wifi and cable connection support

## Features

- FastAPI framework
- Health check endpoints
- API versioning
- Configuration with pydantic_settings
- Docker setup with dynamic reloading

## Requirements

- Python 3.11
- Docker and Docker Compose (optional)

## Installation

### Local development

1. To create a virtual environment:
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```
2. Or just run the application with Docker:
```bash
   docker compose up --build
```
This will record your changes dynamically and reload the application.

**NOTE:**
Please when you need an additional package, add it to the requirements.txt file and run:
```bash
   docker compose up --build
```

E.g, you need to add `fastapi` to the requirements.txt file, then run `docker compose up --build`.
