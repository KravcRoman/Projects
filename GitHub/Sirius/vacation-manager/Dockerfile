# 1. Base Image
FROM python:3.12-slim

# 2. Set Environment Variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Poetry specific
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    # Path where Poetry installs packages
    PIP_DISABLE_PIP_VERSION_CHECK=on

# 3. Set Working Directory
WORKDIR /app

# 4. Install Poetry (can pin version if needed)
RUN pip install poetry

# 5. Copy dependency definition files
COPY pyproject.toml poetry.lock ./

# 6. Install dependencies (use --sync for exact lock file match)
#    --no-dev: Exclude development dependencies
#    --no-root: Don't install the project itself yet
RUN poetry install --no-dev --no-root --sync

# 7. Copy application code and Alembic files
COPY app /app/app
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini

# 8. Expose the application port
EXPOSE 8000

# 9. Command to run the application (including migrations)
#    Ensures migrations run before the server starts
CMD ["sh", "-c", "poetry run alembic upgrade head && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000"]