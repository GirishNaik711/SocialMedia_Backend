from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.database import get_db
from app.database import Base
import pytest
from app.oauth2 import create_access_token
from app import models

# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:REMOVED_DB_PASSWORD@localhost:5432/fastapi_test'
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    #rub our code after we run our test finshes
@pytest.fixture
def test_user(client):
    user_data = {"email":"7th@gmail.com", "password":"12345"}
    res = client.post("/users/", json = user_data)

    assert res.status_code == 201
    print(res.json())
    
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user

@pytest.fixture
def test_user2(client):
    user_data = {"email":"8th@gmail.com", "password":"12345"}
    res = client.post("/users/", json = user_data)

    assert res.status_code == 201
    print(res.json())
    
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user

@pytest.fixture
def test_user(client):
    user_data = {"email":"7th@gmail.com", "password":"12345"}
    res = client.post("/users/", json = user_data)

    assert res.status_code == 201
    print(res.json())
    
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user

@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})

@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client

@pytest.fixture
def test_post(session, test_user, test_user2):
    post_data = [
        {"title": "test title", "content": "test content", "owner_id": test_user["id"]},
        {"title": "test title2", "content": "test content2","owner_id": test_user["id"]},
        {"title": "test title3", "content": "test content3", "owner_id": test_user["id"]},
        {"title": "test title3", "content": "test content3", "owner_id": test_user["id"]}
        ]

    def create_post_model(post):
        return models.Post(**post)
    
    post_map = map(create_post_model, post_data)
    posts = list(post_map)
    session.add_all(posts)

    # session.add_all([models.Post(title= "test title", content= "test content", owner_id= test_user["id"]),
    #                 models.Post(title= "test title2", content= "test content2",owner_id= test_user["id"]),
    #                 models.Post(title= "test title3", content= "test content3", owner_id= test_user["id"])
    #                 ])
    
    session.commit()
    posts = session.query(models.Post).all()
    return posts