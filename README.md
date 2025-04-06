# IFIASOFT ERP System - FastAPI Backend

A modern, scalable ERP system backend built with FastAPI, SQLAlchemy, and PostgreSQL. This backend powers the IFIASOFT ERP system, providing robust APIs for user management, organization management, product management, customer management, and invoicing.

## Features

- **Authentication & Authorization**
  - JWT-based authentication
  - Role-based access control
  - Secure password hashing
  - Session management

- **Organization Management**
  - Create and manage organizations
  - User-organization relationships
  - Organization settings and preferences

- **Product Management**
  - Product catalog
  - Inventory tracking
  - Product categories and variants
  - Pricing management

- **Customer Management**
  - Customer profiles
  - Contact information
  - Customer history
  - Relationship management

- **Invoicing System**
  - Create and manage invoices
  - Multiple invoice statuses (Draft, Pending, Paid, Cancelled)
  - Invoice items and line items
  - Tax calculations
  - Payment tracking

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **Migrations**: Alembic
- **Testing**: Pytest
- **Documentation**: Swagger UI & ReDoc

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)
- virtualenv (recommended)

## Project Structure

```
ifiasoft-fastapi/
├── alembic/                  # Database migrations
├── app/
│   ├── api/                  # API routes
│   ├── core/                 # Core functionality
│   ├── models/               # Database models
│   ├── schemas/              # Pydantic schemas
│   └── services/             # Business logic
├── tests/                    # Test files
├── .env                      # Environment variables
├── alembic.ini              # Alembic configuration
├── requirements.txt          # Project dependencies
└── main.py                  # Application entry point
```

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ifiasoft-fastapi.git
   cd ifiasoft-fastapi
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory with the following variables:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/ifiasoft
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Initialize the database**
   ```bash
   # Create database
   createdb ifiasoft

   # Run migrations
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Database Migrations with Alembic

### Initial Setup

1. **Initialize Alembic** (if not already done)
   ```bash
   alembic init alembic
   ```

2. **Configure Alembic**
   - Update `alembic.ini` with your database URL
   - Update `alembic/env.py` to use your models

### Creating Migrations

1. **Create a new migration**
   ```bash
   alembic revision --autogenerate -m "description of changes"
   ```

2. **Review the migration**
   - Check the generated migration file in `alembic/versions/`
   - Make any necessary adjustments

3. **Apply the migration**
   ```bash
   alembic upgrade head
   ```

### Common Migration Commands

- **Upgrade to latest version**
  ```bash
  alembic upgrade head
  ```

- **Downgrade one version**
  ```bash
  alembic downgrade -1
  ```

- **Upgrade to specific version**
  ```bash
  alembic upgrade <version>
  ```

- **Show current version**
  ```bash
  alembic current
  ```

- **Show migration history**
  ```bash
  alembic history
  ```

## API Documentation

The API documentation is automatically generated and available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run tests using pytest:
```bash
pytest
```
