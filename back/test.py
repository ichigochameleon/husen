import pytest
from fastapi.testclient import TestClient
from back.main import app
from back.main import create_db

create_db()
client = TestClient(app)

TEMPLATE_PROJECT = {
    "name": "テストプロジェクト",
    "overview": "テスト概要",
    "mainchat_url": "https://test.chat.example.com",
    "mainrepo_url": "https://test.hub.example.com",
    "others_url": [
        "https://other1.example.com",
        "https://other2.example.com"
    ]
}

TEMPLATE_MEMO = {
    "name": "メモ1",
    "kinds": 1,
    "others_kinds": "その他",
    "text": "内容"
}


def template_hoge_change(template_hoge):
    result = {}
    for key, value in template_hoge.items():
        if isinstance(value, list):
            new_list = []
            for old_value in value:
                new_list.append("changed_" + str(old_value))
            result[key] = new_list
        elif isinstance(value, int):
            result[key] = value + 1
        else:
            result[key] = "changed_" + str(value)
    return result


TEMPLATE_PROJECT_CHANGE = template_hoge_change(TEMPLATE_PROJECT)
TEMPLATE_MEMO_CHANGE = template_hoge_change(TEMPLATE_MEMO)


def assert_hoge(data, template):
    for key, value in template.items():
        assert data[key] == value


@pytest.fixture
def project():
    response = client.post(
        "/projects/",
        json=TEMPLATE_PROJECT
    )
    assert response.status_code == 200

    yield response.json()

    delete_response = client.delete(f"/projects/{response.json()['id']}")

    assert delete_response.status_code in [200, 404]


@pytest.fixture
def memo(project):
    response = client.post(
        f"/projects/{project['id']}/memos",
        json=TEMPLATE_MEMO
    )
    assert response.status_code == 200

    yield response.json()

    delete_response = client.delete(f"/memos/{response.json()['id']}")

    assert delete_response.status_code in [200, 404]


def test_create_project():
    response = client.post(
        "/projects/",
        json=TEMPLATE_PROJECT
    )
    assert response.status_code == 200
    assert_hoge(response.json(), TEMPLATE_PROJECT)
    delete_response = client.delete(f"/projects/{response.json()['id']}")

    assert delete_response.status_code in [200, 404]


def test_get_projects():
    response = client.get("/projects/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_project(project):
    project_id = project["id"]

    response = client.get(f"/projects/{project_id}")

    assert response.status_code == 200

    data = response.json()

    assert_hoge(data, TEMPLATE_PROJECT)
    assert data["memos"] == []


def test_update_project(project):
    project_id = project["id"]

    response = client.put(
        f"/projects/{project_id}",
        json=TEMPLATE_PROJECT_CHANGE
    )

    assert response.status_code == 200

    data = response.json()

    assert_hoge(data, TEMPLATE_PROJECT_CHANGE)

    response = client.get(f"/projects/{project_id}")

    assert response.status_code == 200

    data = response.json()

    assert_hoge(data, TEMPLATE_PROJECT_CHANGE)


def test_create_memo(project, memo):
    assert_hoge(memo, TEMPLATE_MEMO)
    assert memo["project_id"] == project["id"]


def test_create_memo_projects(project, memo):
    project_id = project["id"]
    assert_hoge(memo, TEMPLATE_MEMO)
    assert memo["project_id"] == project_id

    response = client.get(f"/projects")
    assert response.status_code == 200
    projects = response.json()
    project = next(p for p in projects if p["id"] == project_id)

    assert_hoge(project, TEMPLATE_PROJECT)

    assert len(project["memos"]) == 1

    assert_hoge(project["memos"][0], TEMPLATE_MEMO)


def test_update_memo(memo):
    memo_id = memo["id"]

    response = client.put(
        f"/memos/{memo_id}",
        json=TEMPLATE_MEMO_CHANGE
    )

    assert response.status_code == 200

    data = response.json()

    assert_hoge(data, TEMPLATE_MEMO_CHANGE)


def test_delete_memo(memo):
    memo_id = memo["id"]

    response = client.delete(f"/memos/{memo_id}")

    assert response.status_code == 200

    response = client.put(
        f"/memos/{memo_id}",
        json={"text": "test"}
    )

    assert response.status_code == 404


def test_delete_project(project):
    project_id = project["id"]

    response = client.delete(f"/projects/{project_id}")

    assert response.status_code == 200

    response = client.get(f"/projects/{project_id}")

    assert response.status_code == 404
