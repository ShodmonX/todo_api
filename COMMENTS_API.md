# Comments Feature API Documentation

## Overview
Complete REST API implementation for task comments with 5 endpoints following the established project patterns.

## Endpoints

### Task-Scoped Endpoints (under /api/v1/tasks/{task_id})

#### 1. List Comments
- **Method**: `GET`
- **Path**: `/api/v1/tasks/{task_id}/comments`
- **Response**: `list[CommentOut]`
- **Description**: Get all comments for a specific task (newest first)
- **Authorization**: Task owner or superuser

#### 2. Create Comment
- **Method**: `POST`
- **Path**: `/api/v1/tasks/{task_id}/comments`
- **Body**: `CommentCreate` (content: str)
- **Response**: `CommentOut`
- **Status**: `201 Created`
- **Description**: Add a new comment to a task
- **Authorization**: Task owner or superuser

### Standalone Endpoints (under /api/v1/comments/{comment_id})

#### 3. Get Comment
- **Method**: `GET`
- **Path**: `/api/v1/comments/{comment_id}`
- **Response**: `CommentOut`
- **Description**: Retrieve a specific comment by ID
- **Authorization**: Task owner or superuser

#### 4. Update Comment
- **Method**: `PUT`
- **Path**: `/api/v1/comments/{comment_id}`
- **Body**: `CommentUpdate` (content: str)
- **Response**: `CommentOut`
- **Description**: Update an existing comment (author-only)
- **Authorization**: Comment author or superuser

#### 5. Delete Comment
- **Method**: `DELETE`
- **Path**: `/api/v1/comments/{comment_id}`
- **Response**: `{"status": "ok", "message": "Comment deleted"}`
- **Status**: `200 OK`
- **Description**: Delete a comment (author-only)
- **Authorization**: Comment author or superuser

## Data Models

### CommentCreate
```python
{
  "content": "string"  # Required, non-empty after strip
}
```

### CommentUpdate
```python
{
  "content": "string"  # Required, non-empty after strip
}
```

### CommentOut
```python
{
  "id": 1,
  "content": "string",
  "task_id": 1,
  "user_id": 1,
  "created_at": "2024-01-27T12:00:00",
  "updated_at": "2024-01-27T12:00:00"
}
```

## Authorization Rules

1. **Task Access**: User must be task owner or superuser to view/create comments
2. **Author-Only**: Only comment author or superuser can update/delete comments
3. **Automatic Assignment**: User ID is automatically set from current authenticated user

## Database Schema

```sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX ix_comments_task_id ON comments(task_id);
CREATE INDEX ix_comments_user_id ON comments(user_id);
```

## Files Created/Modified

### New Files
- `app/models/comment.py` - SQLAlchemy Comment model
- `app/schemas/comment.py` - Pydantic schemas (CommentCreate, CommentUpdate, CommentOut)
- `app/crud/comment.py` - CRUD operations (list, create, get, update, delete)
- `app/api/v1/comment.py` - Standalone comment endpoints
- `alembic/versions/81654a2185a4_add_comment_table.py` - Database migration

### Modified Files
- `app/models/__init__.py` - Added Comment import and export
- `app/models/task.py` - Added comments relationship
- `app/models/user.py` - Added comments relationship
- `app/schemas/__init__.py` - Added Comment schemas
- `app/crud/__init__.py` - Added comment CRUD functions
- `app/api/v1/deps.py` - Added ensure_comment_access dependency
- `app/api/v1/task.py` - Added task-scoped comment endpoints
- `app/api/v1/api.py` - Included comment router

## Migration

Run migration to create the comments table:

```bash
alembic upgrade head
```

## Features

- ✅ Complete CRUD operations
- ✅ Proper authorization (task access + author-only for updates/deletes)
- ✅ Automatic timestamp management (created_at, updated_at)
- ✅ Cascade deletes (comment deleted when task or user is deleted)
- ✅ Input validation (non-empty content after strip)
- ✅ Indexed foreign keys for performance
- ✅ Consistent with project patterns (Integer IDs, AsyncSession, HTTPException)
