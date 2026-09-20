import pytest
from fastapi.testclient import TestClient

from back.main import app
from back.main import create_db


create_db()
client = TestClient(app)



JWT_TOKEN = input("JWT token: ")

client.cookies.set(
    "access_token",
    JWT_TOKEN
)
# =========================
# テンプレート
# =========================

TEMPLATE_PROJECT = {
    "name": "テストプロジェクト",
    "overview": "テスト概要",
    "mainchat_url": "https://test.chat.example.com",
    "mainrepo_url": "https://test.hub.example.com",
    "others_url": [
        "https://other1.example.com",
        "https://other2.example.com"
    ],
    "status": "未完了",
    "project_exist": "private",
}

TEMPLATE_MEMO = {
    "name": "メモ1",
    "kinds": 1,
    "other_kinds": "その他",
    "text": "内容",
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


TEMPLATE_PROJECT_CHANGE["status"] = "途中結論"
TEMPLATE_PROJECT_CHANGE["project_exist"] = "public"

print("TEMPLATE_PROJECT:", TEMPLATE_PROJECT)
print("TEMPLATE_PROJECT_CHANGE:", TEMPLATE_PROJECT_CHANGE)




def assert_hoge(data, template):
    for key, value in template.items():
        assert data[key] == value


# =========================
# Fixture
# =========================

@pytest.fixture
def project():
    response = client.post(
        "/projects/",
        json=TEMPLATE_PROJECT
    )

    assert response.status_code == 200

    project_data = response.json()

    yield project_data

    delete_response = client.delete(
        f"/projects/{project_data['id']}"
    )

    assert delete_response.status_code in [200, 404]


@pytest.fixture
def memo(project):
    response = client.post(
        f"/projects/{project['id']}/memos",
        json=TEMPLATE_MEMO
    )

    assert response.status_code == 200

    memo_data = response.json()

    yield memo_data

    delete_response = client.delete(
        f"/memos/{memo_data['id']}"
    )

    assert delete_response.status_code in [200, 404]


# =========================
# Project
# =========================

def test_create_project():
    response = client.post(
        "/projects/",
        json=TEMPLATE_PROJECT
    )

    assert response.status_code == 200

    data = response.json()

    assert_hoge(data, TEMPLATE_PROJECT)

    delete_response = client.delete(
        f"/projects/{data['id']}"
    )

    assert delete_response.status_code in [200, 404]


def test_get_projects():
    response = client.get("/projects/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_project(project):
    project_id = project["id"]

    response = client.get(
        f"/projects/{project_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert_hoge(data, TEMPLATE_PROJECT)


def test_update_project(project):
    project_id = project["id"]

    print("========== DEBUG ==========")
    print(TEMPLATE_PROJECT_CHANGE)
    print("status =", TEMPLATE_PROJECT_CHANGE["status"])
    print("project_exist =", TEMPLATE_PROJECT_CHANGE["project_exist"])
    print("===========================")

    response = client.put(
        f"/projects/{project_id}",
        json=TEMPLATE_PROJECT_CHANGE
    )

    print("UPDATE STATUS:", response.status_code)
    print("UPDATE BODY:", response.json())

    assert response.status_code == 200


def test_delete_project(project):
    project_id = project["id"]

    response = client.delete(
        f"/projects/{project_id}"
    )

    assert response.status_code == 200

    response = client.get(
        f"/projects/{project_id}"
    )

    assert response.status_code == 404


# =========================
# Project Permission
# =========================

def test_project_permissions(project):
    project_id = project["id"]

    response = client.get(
        f"/projects/{project_id}/permissions"
    )

    assert response.status_code == 200

    permissions = response.json()["permissions"]

    assert "read" in permissions
    assert "update" in permissions
    assert "delete" in permissions

    assert "manage_read" in permissions
    assert "manage_update" in permissions
    assert "manage_delete" in permissions

    assert "owner" in permissions


# =========================
# Star
# =========================

def test_star_project(project):
    project_id = project["id"]

    response = client.post(
        f"/projects/{project_id}/star"
    )

    assert response.status_code == 200

    response = client.get(
        f"/projects/{project_id}/permissions"
    )

    assert response.status_code == 200

    permissions = response.json()["permissions"]

    assert "star" in permissions


def test_star_project_twice(project):
    project_id = project["id"]

    response = client.post(
        f"/projects/{project_id}/star"
    )

    assert response.status_code == 200

    response = client.post(
        f"/projects/{project_id}/star"
    )

    assert response.status_code == 200

    assert response.json()["detail"] == "Project already starred"


def test_unstar_project(project):
    project_id = project["id"]

    response = client.post(
        f"/projects/{project_id}/star"
    )

    assert response.status_code == 200

    response = client.delete(
        f"/projects/{project_id}/star"
    )

    assert response.status_code == 200

    response = client.get(
        f"/projects/{project_id}/permissions"
    )

    assert response.status_code == 200

    permissions = response.json()["permissions"]

    assert "star" not in permissions


def test_unstar_without_star(project):
    project_id = project["id"]

    response = client.delete(
        f"/projects/{project_id}/star"
    )

    assert response.status_code == 200

    assert response.json()["detail"] == "Project not starred"


def test_star_project_in_list(project):
    project_id = project["id"]

    response = client.post(
        f"/projects/{project_id}/star"
    )

    assert response.status_code == 200

    response = client.get("/projects/")

    assert response.status_code == 200

    projects = response.json()

    assert any(
        p["id"] == project_id
        for p in projects
    )


# =========================
# Memo
# =========================

def test_create_memo(project, memo):
    assert_hoge(
        memo,
        TEMPLATE_MEMO
    )

    assert memo["project_id"] == project["id"]


def test_create_memo_projects(project, memo):
    project_id = project["id"]

    assert_hoge(
        memo,
        TEMPLATE_MEMO
    )

    assert memo["project_id"] == project_id

    response = client.get("/projects/")

    assert response.status_code == 200

    projects = response.json()

    project_data = next(
        p for p in projects
        if p["id"] == project_id
    )

    assert_hoge(
        project_data,
        TEMPLATE_PROJECT
    )


def test_update_memo(memo):
    memo_id = memo["id"]

    response = client.put(
        f"/memos/{memo_id}",
        json=TEMPLATE_MEMO_CHANGE
    )

    assert response.status_code == 200

    data = response.json()

    assert_hoge(
        data,
        TEMPLATE_MEMO_CHANGE
    )


def test_delete_memo(memo):
    memo_id = memo["id"]

    response = client.delete(
        f"/memos/{memo_id}"
    )

    assert response.status_code == 200

    response = client.put(
        f"/memos/{memo_id}",
        json={"text": "test"}
    )

    assert response.status_code == 404


# =========================
# Chat
# =========================

def test_create_chat(memo):
    memo_id = memo["id"]

    response = client.post(
        f"/memos/{memo_id}/chats",
        params={"chat_text": "チャット1"}
    )

    print("CHAT STATUS:", response.status_code)
    print("CHAT BODY:", response.json())

    assert response.status_code == 200

def test_get_chats(memo):
    memo_id = memo["id"]

    response = client.get(
        f"/memos/{memo_id}/chats"
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_chat(memo):
    memo_id = memo["id"]

    response = client.post(
        f"/memos/{memo_id}/chats",
        params={"chat_text": "チャット1"}
    )

    assert response.status_code == 200

    chat_id = response.json()["id"]

    response = client.put(
        f"/chats/{chat_id}",
        json={"text": "変更後"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["text"] == "変更後"


def test_delete_chat(memo):
    memo_id = memo["id"]

    response = client.post(
        f"/memos/{memo_id}/chats",
        params={"chat_text": "チャット1"}
    )

    assert response.status_code == 200

    chat_id = response.json()["id"]

    response = client.delete(
        f"/chats/{chat_id}"
    )

    assert response.status_code == 200

    response = client.put(
        f"/chats/{chat_id}",
        json={"text": "test"}
    )

    assert response.status_code == 404