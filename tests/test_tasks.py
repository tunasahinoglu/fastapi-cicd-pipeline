def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_task(client):
    response = client.post(
        "/tasks", json={"title": "Learn Terraform", "description": "Write the EKS module"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Learn Terraform"
    assert data["is_done"] is False
    assert "id" in data


def test_create_task_requires_title(client):
    response = client.post("/tasks", json={"description": "no title"})
    assert response.status_code == 422


def test_read_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_read_single_task(client):
    created = client.post("/tasks", json={"title": "Test task"}).json()
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_read_task_not_found(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404


def test_update_task(client):
    created = client.post("/tasks", json={"title": "Old title"}).json()
    response = client.put(f"/tasks/{created['id']}", json={"is_done": True})
    assert response.status_code == 200
    assert response.json()["is_done"] is True
    assert response.json()["title"] == "Old title"


def test_update_task_not_found(client):
    response = client.put("/tasks/999", json={"is_done": True})
    assert response.status_code == 404


def test_delete_task(client):
    created = client.post("/tasks", json={"title": "To be deleted"}).json()
    response = client.delete(f"/tasks/{created['id']}")
    assert response.status_code == 204

    get_response = client.get(f"/tasks/{created['id']}")
    assert get_response.status_code == 404


def test_delete_task_not_found(client):
    response = client.delete("/tasks/999")
    assert response.status_code == 404

def test_filter_tasks_by_is_done(client):
    done_task = client.post("/tasks", json={"title": "Completed task"}).json()
    client.put(f"/tasks/{done_task['id']}", json={"is_done": True})
    client.post("/tasks", json={"title": "Pending task"})

    response = client.get("/tasks?is_done=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Completed task"

    response = client.get("/tasks?is_done=false")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Pending task"

    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 2
