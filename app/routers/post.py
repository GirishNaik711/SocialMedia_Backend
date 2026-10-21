from .. import models, schemas
from fastapi import Response, status, HTTPException, Depends, APIRouter, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from ..database import get_db
from typing import List
from .. import oauth2
from typing import Optional

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


def posts_with_votes(db: Session):
    return db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).options(
        selectinload(models.Post.owner)).group_by(models.Post.id)


@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user),
              limit: int = Query(10, ge=1, le=100), skip: int = Query(0, ge=0), search: Optional[str] = ""):
    posts = posts_with_votes(db).filter(models.Post.title.contains(search, autoescape=True)).order_by(models.Post.id).limit(limit).offset(skip).all()

    return [{"Post": post, "Votes": votes} for post, votes in posts]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post:schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    new_post = models.Post(owner_id = current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    result = posts_with_votes(db).filter(models.Post.id == id).first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")

    post, votes = result
    return {"Post": post, "Votes": votes}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post with id {id} does not exist".format(id=id))

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this post")

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.Post)
def update_post(id:int, updated_post:schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post with id {id} does not exist".format(id=id))

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update this post")

    post_query.update(updated_post.model_dump(),synchronize_session=False)

    db.commit()
    return  post_query.first()
