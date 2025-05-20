import pytest
from httpx import AsyncClient
from fastapi import status
import datetime

# Mark all tests in this module as async
pytestmark = pytest.mark.asyncio

async def test_create_vacation_success(client: AsyncClient):
    """Test creating a vacation successfully."""
    employee_id = 101
    start_date = (datetime.date.today() + datetime.timedelta(days=10)).isoformat()
    end_date = (datetime.date.today() + datetime.timedelta(days=15)).isoformat()

    response = await client.post(
        "/api/v1/vacations/",
        json={
            "employee_id": employee_id,
            "start_date": start_date,
            "end_date": end_date
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["employee_id"] == employee_id
    assert data["start_date"] == start_date
    assert data["end_date"] == end_date
    assert "id" in data
    assert "created_at" in data

async def test_create_vacation_overlap_conflict(client: AsyncClient):
    """Test creating a vacation that overlaps with an existing one."""
    employee_id = 102
    # First vacation
    await client.post("/api/v1/vacations/", json={
        "employee_id": employee_id,
        "start_date": "2025-07-01",
        "end_date": "2025-07-10"
    })
    # Second (overlapping) vacation attempt
    response = await client.post("/api/v1/vacations/", json={
        "employee_id": employee_id,
        "start_date": "2025-07-05", # Overlaps
        "end_date": "2025-07-15"
    })
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "overlaps with an existing vacation" in response.json()["detail"]

async def test_create_vacation_invalid_dates(client: AsyncClient):
    """Test creating a vacation with end_date before start_date."""
    response = await client.post("/api/v1/vacations/", json={
        "employee_id": 103,
        "start_date": "2025-08-10",
        "end_date": "2025-08-05" # Invalid
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    # Pydantic validation error details might vary slightly
    assert "End date must be on or after start date" in str(response.json())

async def test_get_vacations_by_employee(client: AsyncClient):
    """Test retrieving the last N vacations for an employee."""
    employee_id = 104
    # Create some vacations (ensure order for testing latest)
    await client.post("/api/v1/vacations/", json={"employee_id": employee_id, "start_date": "2025-05-01", "end_date": "2025-05-05"}) # 3rd latest
    await client.post("/api/v1/vacations/", json={"employee_id": employee_id, "start_date": "2025-06-01", "end_date": "2025-06-05"}) # 2nd latest
    resp3 = await client.post("/api/v1/vacations/", json={"employee_id": employee_id, "start_date": "2025-07-01", "end_date": "2025-07-05"}) # latest
    latest_id = resp3.json()["id"]

    # Get latest 2
    response = await client.get(f"/api/v1/vacations/employees/{employee_id}?limit=2")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["start_date"] == "2025-07-01" # Latest first
    assert data[1]["start_date"] == "2025-06-01"

    # Get default (3)
    response_default = await client.get(f"/api/v1/vacations/employees/{employee_id}")
    assert response_default.status_code == status.HTTP_200_OK
    data_default = response_default.json()
    assert len(data_default) == 3
    assert data_default[0]["start_date"] == "2025-07-01"

async def test_get_vacations_by_period(client: AsyncClient):
    """Test retrieving vacations within a specific date range."""
    # Add test data
    await client.post("/api/v1/vacations/", json={"employee_id": 201, "start_date": "2025-09-01", "end_date": "2025-09-10"}) # Inside
    await client.post("/api/v1/vacations/", json={"employee_id": 202, "start_date": "2025-09-15", "end_date": "2025-09-25"}) # Overlaps end
    await client.post("/api/v1/vacations/", json={"employee_id": 203, "start_date": "2025-08-25", "end_date": "2025-09-05"}) # Overlaps start
    await client.post("/api/v1/vacations/", json={"employee_id": 204, "start_date": "2025-10-01", "end_date": "2025-10-10"}) # Outside

    filter_start = "2025-09-03"
    filter_end = "2025-09-20"
    response = await client.get(f"/api/v1/vacations/?start_date={filter_start}&end_date={filter_end}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3 # Should find the three overlapping/inside vacations
    employee_ids_found = {v["employee_id"] for v in data}
    assert employee_ids_found == {201, 202, 203}

async def test_delete_vacation_success(client: AsyncClient):
    """Test deleting an existing vacation."""
    resp = await client.post("/api/v1/vacations/", json={
        "employee_id": 301,
        "start_date": "2025-11-01",
        "end_date": "2025-11-05"
    })
    vacation_id = resp.json()["id"]

    delete_response = await client.delete(f"/api/v1/vacations/{vacation_id}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # Verify deletion
    get_response = await client.get(f"/api/v1/vacations/employees/{301}") # Check if it appears for employee
    assert get_response.status_code == status.HTTP_200_OK
    assert vacation_id not in [v["id"] for v in get_response.json()] # Check it's gone

async def test_delete_vacation_not_found(client: AsyncClient):
    """Test deleting a non-existent vacation."""
    non_existent_id = 99999
    delete_response = await client.delete(f"/api/v1/vacations/{non_existent_id}")
    assert delete_response.status_code == status.HTTP_404_NOT_FOUND
    assert f"Vacation with id {non_existent_id} not found" in delete_response.json()["detail"]