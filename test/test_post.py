from app import schemas
import pytest


def test_get_all_posts(authorized_client, test_post):
    res = authorized_client.get("/posts/")
    posts = [schemas.PostOut(**post) for post in res.json()]

    assert res.status_code == 200
    assert len(posts) == len(test_post)


def test_get_all_posts_search(authorized_client, test_post):
    res = authorized_client.get("/posts/", params={"search": "title2"})

    assert res.status_code == 200
    assert [p["Post"]["title"] for p in res.json()] == ["test title2"]


def test_get_all_posts_search_wildcard_is_literal(authorized_client, test_post):
    res = authorized_client.get("/posts/", params={"search": "%"})

    assert res.status_code == 200
    assert res.json() == []


def test_get_all_posts_limit_and_skip(authorized_client, test_post):
    res = authorized_client.get("/posts/", params={"limit": 2, "skip": 1})

    assert res.status_code == 200
    assert len(res.json()) == 2


def test_get_all_posts_limit_capped(authorized_client, test_post):
    res = authorized_client.get("/posts/", params={"limit": 1000})
    assert res.status_code == 422


def test_unauthorized_user_get_all_posts(client, test_post):
    res = client.get("/posts/")
    assert res.status_code == 401


def test_unauthorized_user_get_one_posts(client, test_post):
    res = client.get(f"/posts/{test_post[0].id}")
    assert res.status_code == 401


def test_get_one_post_not_exist(authorized_client, test_post):
    res = authorized_client.get("/posts/100")

    assert res.status_code == 404


def test_get_one_post(authorized_client, test_post):
    res = authorized_client.get(f"/posts/{test_post[0].id}")
    post = schemas.PostOut(**res.json())

    assert res.status_code == 200
    assert post.Post.id == test_post[0].id
    assert post.Post.content == test_post[0].content
    assert post.Post.title == test_post[0].title


def test_get_one_post_counts_votes(authorized_client, test_post):
    post_id = test_post[0].id
    authorized_client.post("/vote/", json={"post_id": post_id, "dir": 1})

    res = authorized_client.get(f"/posts/{post_id}")

    assert res.json()["Votes"] == 1


@pytest.mark.parametrize("title, content, published", [
    ("awesome new title", "awesome new content", True),
    ("favorite pizza", "i love pepperoni", False),
    ("tallest skyscrapers", "wahoo", True),
])
def test_create_post(authorized_client, test_user, test_post, title, content, published):
    res = authorized_client.post("/posts/", json={"title": title, "content": content, "published": published})
    created_post = schemas.Post(**res.json())

    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_user["id"]


def test_create_post_default_published_true(authorized_client, test_user, test_post):
    res = authorized_client.post("/posts/", json={"title": "arbitary title", "content": "arbitary content"})
    created_post = schemas.Post(**res.json())

    assert res.status_code == 201
    assert created_post.title == "arbitary title"
    assert created_post.content == "arbitary content"
    assert created_post.published == True
    assert created_post.owner_id == test_user["id"]


def test_unauthorized_user_create_post(client, test_user, test_post):
    res = client.post("/posts/", json={"title": "arbitary title", "content": "arbitary content"})
    assert res.status_code == 401


def test_unauthorized_user_delete_post(client, test_post):
    res = client.delete(f"/posts/{test_post[0].id}")
    assert res.status_code == 401


def test_delete_post_success(authorized_client, test_user, test_post):
    post_id = test_post[0].id
    res = authorized_client.delete(f"/posts/{post_id}")

    assert res.status_code == 204
    assert authorized_client.get(f"/posts/{post_id}").status_code == 404


def test_delete_post_non_exist(authorized_client, test_user, test_post):
    res = authorized_client.delete("/posts/8000000")

    assert res.status_code == 404


def test_delete_other_user_post(authorized_client, test_user, test_post):
    res = authorized_client.delete(f"/posts/{test_post[3].id}")
    assert res.status_code == 403


def test_update_post(authorized_client, test_user, test_post):
    data = {"title": "updated title", "content": "updated content", "id": test_post[0].id}

    res = authorized_client.put(f"/posts/{test_post[0].id}", json=data)
    updated_post = schemas.Post(**res.json())

    assert res.status_code == 200
    assert updated_post.title == data["title"]
    assert updated_post.content == data["content"]


def test_update_other_user_post(authorized_client, test_user, test_post):
    data = {"title": "updated title", "content": "updated content"}

    res = authorized_client.put(f"/posts/{test_post[3].id}", json=data)

    assert res.status_code == 403


def test_update_post_non_exist(authorized_client, test_user, test_post):
    data = {"title": "updated title", "content": "updated content"}

    res = authorized_client.put("/posts/8000000", json=data)

    assert res.status_code == 404


def test_unauthorized_user_update_post(client, test_user, test_post):
    data = {"title": "updated title", "content": "updated content"}

    res = client.put(f"/posts/{test_post[0].id}", json=data)

    assert res.status_code == 401
