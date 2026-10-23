"""
Todo domain database access repository.
Handles low-level persistence queries using SQLAlchemy ORM.
"""

from typing import List, Optional
from sqlalchemy import case
from sqlalchemy.orm import Session

from app.todos.models import Todo, ChecklistItem
from app.todos.schemas import TodoCreate, TodoUpdate


def get_all_todos(db: Session, sort_by: Optional[str] = None, user_id: Optional[str] = None) -> List[Todo]:
    """Retrieves all todos from database with optional user_id scoping and sorting."""
    query = db.query(Todo)

    if user_id:
        query = query.filter(Todo.user_id == user_id)

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


def get_todo_by_id(db: Session, todo_id: int) -> Optional[Todo]:
    """Retrieves a single todo task by ID."""
    return db.query(Todo).filter(Todo.id == todo_id).first()


def create_todo(db: Session, todo_in: TodoCreate, user_id: Optional[str] = None) -> Todo:
    """Inserts a new todo record into the database stamped with user_id."""
    db_todo = Todo(
        user_id=user_id,
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
    """Updates an existing todo record."""
    db_todo = get_todo_by_id(db, todo_id)
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


def toggle_todo_completion(db: Session, todo_id: int) -> Optional[Todo]:
    """Toggles completed boolean field on a todo."""
    db_todo = get_todo_by_id(db, todo_id)
    if db_todo:
        db_todo.completed = not db_todo.completed
        db.commit()
        db.refresh(db_todo)
    return db_todo


def delete_todo(db: Session, todo_id: int) -> bool:
    """Deletes a todo record and cascading sub-checklist items."""
    db_todo = get_todo_by_id(db, todo_id)
    if db_todo:
        db.delete(db_todo)
        db.commit()
        return True
    return False


# SUB-CHECKLIST ITEMS persistance
def get_checklist_items(db: Session, todo_id: int) -> List[ChecklistItem]:
    """Retrieves sub-checklist items for a specific todo."""
    return db.query(ChecklistItem).filter(ChecklistItem.todo_id == todo_id).order_by(ChecklistItem.id.asc()).all()


def add_checklist_item(db: Session, todo_id: int, text: str) -> ChecklistItem:
    """Adds a sub-checklist item."""
    item = ChecklistItem(todo_id=todo_id, text=text.strip(), completed=False)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def toggle_checklist_item(db: Session, item_id: int) -> Optional[ChecklistItem]:
    """Toggles checklist item completion state."""
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
    if item:
        item.completed = not item.completed
        db.commit()
        db.refresh(item)
    return item


def delete_checklist_item(db: Session, item_id: int) -> bool:
    """Deletes a sub-checklist item."""
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False
