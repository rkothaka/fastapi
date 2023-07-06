from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional, Tuple
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session


models.Base.metadata.create_all(bind=engine)


app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres',
                                password='root', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful!")
        break
    except Exception as error:
        print("Connecting to Database failed")
        print("Error", error)
        time.sleep(5)


my_posts = [{"title": "Title1", "content": "Content1", "id": 1}, {"title": "Title2", "content": "Content2", "id": 2}]


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/posts")
def get_posts():
    return {"data": my_posts}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    return {"status": "success"}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict['id'] = randrange(0, 100_000_000)
    my_posts.append(post_dict)
    return {"data": post_dict}


def find_post(id: int) -> Tuple[int, dict]:
    for idx, post in enumerate(my_posts):
        if post['id'] == id:
            return idx, post


@app.get("/posts/{id}")
def get_post(id: int):
    post = find_post(id)[1]
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    idx = find_post(id)

    # Post with id not found
    if idx is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    else:
        idx = idx[0]

    my_posts.pop(idx)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    idx = find_post(id)
    # Post with id not found
    if idx is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    else:
        idx = idx[0]

    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[idx] = post_dict

    return {"message": "updated post"}

