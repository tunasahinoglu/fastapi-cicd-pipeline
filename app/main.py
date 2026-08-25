from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task API",
    description="A simple task/todo API used to demo a CI/CD pipeline",
    version="1.1.0",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "version": app.version}


@app.get("/", tags=["health"])
def root():
    return {
        "message": "FastAPI CI/CD demo",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/tasks", response_model=List[schemas.TaskResponse], tags=["tasks"])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    is_done: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    return crud.get_tasks(db, skip=skip, limit=limit, is_done=is_done)


@app.post("/tasks", response_model=schemas.TaskResponse, status_code=201, tags=["tasks"])
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task)


@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse, tags=["tasks"])
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse, tags=["tasks"])
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    db_task = crud.update_task(db, task_id, task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@app.delete("/tasks/{task_id}", status_code=204, tags=["tasks"])
def delete_task(task_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
