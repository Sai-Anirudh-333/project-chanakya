# API Architecture Plan

This document outlines the planned multi-tier architecture for the FastAPI application.

## 1. Domain-Driven Routing (`app/api/endpoints/`)
Instead of one massive `main.py` file handling all requests, we will split routes by domain.
*   `app/api/endpoints/briefings.py`: Handles `/api/briefings`
*   `app/api/endpoints/entities.py`: Handles `/api/entities`
*   `app/api/endpoints/topics.py`: Handles `/api/topics`
*   `app/api/endpoints/forecast.py`: Handles `/api/forecast`

These will all be registered into a single router.

## 2. API Router Definition (`app/api/routes.py`)
This file will import the individual endpoint routers and connect them into one `api_router`. `main.py` will then import and use `api_router`.

## 3. Database Operations (`app/crud/`)
The database functions should be separated from the routes, maintaining the separation of concerns. 
Instead of `app/databases/crud.py`, we will have:
*   `app/crud/briefings.py`
*   `app/crud/entities.py`
*   `app/crud/topics.py`

## 4. Models and Schemas (`app/models/` and `app/schemas/`)
Likewise, instead of `app/databases/models.py`, we can separate:
*   `app/models/`: SQLAlchemy models (Database schema)
*   `app/schemas/`: Pydantic models (API schema)

This structure follows standard FastAPI best practices and scales well.
