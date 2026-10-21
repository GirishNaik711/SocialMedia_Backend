from app import schemas, models
import pytest
from jose import jwt
from app.config import settings
from app.oauth2 import create_access_token


def test_root(client):
    res = client.get("/")
    assert res.status_code == 200


def test_create_user(client):
    res = client.post("/users/", json={"email": "5th@gmail.com", "password": "12343"})

    new_user = schemas.UserOut(**res.json())
    assert res.status_code == 201
    assert new_user.email == "5th@gmail.com"


def test_create_user_stores_hashed_password(client, session):
    client.post("/users/", json={"email": "5th@gmail.com", "password": "12343"})

    stored = session.query(models.User).filter(models.User.email == "5th@gmail.com").one()
    assert stored.password != "12343"


def test_create_user_duplicate_email(client, test_user):
    res = client.post("/users/", json={"email": test_user["email"], "password": "another"})

    assert res.status_code == 409


def test_create_user_invalid_email(client):
    res = client.post("/users/", json={"email": "not-an-email", "password": "12343"})

    assert res.status_code == 422


def test_get_user(client, test_user):
    res = client.get(f"/users/{test_user['id']}")

    assert res.status_code == 200
    assert res.json()["email"] == test_user["email"]
    assert "password" not in res.json()


def test_get_user_not_exist(client):
    res = client.get("/users/8000000")

    assert res.status_code == 404


def test_login_user(test_user, client):
    res = client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
    login_res = schemas.Token(**res.json())

    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")

    assert id == test_user["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200


@pytest.mark.parametrize("email, password", [
    ('wrongemail@gmail.com', '12345'),
    ('7th@gmail.com', 'wrongpassword'),
    ('wrongemail@gmail.com', 'wrongpassword'),
])
def test_incorrect_login(test_user, client, email, password):
    res = client.post("/login", data={"username": email, "password": password})

    assert res.status_code == 403
    assert res.json().get("detail") == "Invalid credentials"


@pytest.mark.parametrize("form", [
    {"username": "7th@gmail.com"},
    {"password": "12345"},
])
def test_login_missing_field(test_user, client, form):
    res = client.post("/login", data=form)

    assert res.status_code == 422


def test_token_for_deleted_user_rejected(client, session):
    token = create_access_token({"user_id": 8000000})

    res = client.get("/posts/", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 401


def test_tampered_token_rejected(client, token):
    res = client.get("/posts/", headers={"Authorization": f"Bearer {token}x"})

    assert res.status_code == 401
