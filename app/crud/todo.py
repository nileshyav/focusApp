from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import case
from app.models.todo import Todo
from app.models.checklist import ChecklistItem
from app.schemas.todo import TodoCreate, TodoUpdate

def get_todos(db: Session, sort_by: Optional[str] = None) -> List[Todo]:
    query = db.query(Todo)
    
    if sort_by == "priority":
        priority_case = case(
            (Todo.priority == "high", 1),
            (Todo.priority == "medium", 2),
            (Todo.priority == "low", 3),
            else_=4
        )
        query = query.order_by(Todo.completed.asc(), priority_case.asc(), Todo.id.desc())
    elif sort_by == "deadline":
        deadline_case = case(
            (Todo.deadline == None, 1),
            (Todo.deadline == "", 1),
            else_=0
        )
        query = query.order_by(Todo.completed.asc(), deadline_case.asc(), Todo.deadline.asc(), Todo.id.desc())
    else:
        query = query.order_by(Todo.completed.asc(), Todo.id.desc())

    return query.all()

def get_todo(db: Session, todo_id: int) -> Optional[Todo]:
    return db.query(Todo).filter(Todo.id == todo_id).first()

def create_todo(db: Session, todo_in: TodoCreate) -> Todo:
    db_todo = Todo(
        title=todo_in.title.strip(),
        description=todo_in.description.strip() if todo_in.description else "",
        priority=todo_in.priority.lower(),
        deadline=todo_in.deadline.strip() if todo_in.deadline else "",
        karma=max(0, min(5, todo_in.karma))
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_todo(db: Session, todo_id: int, todo_in: TodoUpdate) -> Optional[Todo]:
    db_todo = get_todo(db, todo_id)
    if not db_todo:
        return None
    
    update_data = todo_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        if val is not None:
            if isinstance(val, str):
                val = val.strip()
            if field == "priority":
                val = val.lower()
            if field == "karma":
                val = max(0, min(5, val))
            setattr(db_todo, field, val)

    db.commit()
    db.refresh(db_todo)
    return db_todo

def toggle_todo(db: Session, todo_id: int) -> Optional[Todo]:
    db_todo = get_todo(db, todo_id)
    if db_todo:
        db_todo.completed = not db_todo.completed
        db.commit()
        db.refresh(db_todo)
    return db_todo

def delete_todo(db: Session, todo_id: int) -> bool:
    db_todo = get_todo(db, todo_id)
    if db_todo:
        db.delete(db_todo)
        db.commit()
        return True
    return False

# CHECKLIST ITEMS CRUD
def get_checklist_items(db: Session, todo_id: int) -> List[ChecklistItem]:
    return db.query(ChecklistItem).filter(ChecklistItem.todo_id == todo_id).order_by(ChecklistItem.id.asc()).all()

def add_checklist_item(db: Session, todo_id: int, text: str) -> ChecklistItem:
    item = ChecklistItem(todo_id=todo_id, text=text.strip(), completed=False)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def toggle_checklist_item(db: Session, item_id: int) -> Optional[ChecklistItem]:
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
    if item:
        item.completed = not item.completed
        db.commit()
        db.refresh(item)
    return item

def delete_checklist_item(db: Session, item_id: int) -> bool:
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False
