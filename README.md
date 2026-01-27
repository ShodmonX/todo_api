# Todo API

A comprehensive RESTful API for task management built with FastAPI, PostgreSQL, and modern Python async patterns.

## Features

### 🔐 Authentication & Authorization
- User registration with email verification
- JWT-based authentication (access & refresh tokens)
- Role-based access control (Admin/User)
- Password management (change, forgot, reset)
- Profile management with image uploads

### 📝 Task Management
- Full CRUD operations for tasks
- Task status tracking (pending, in-progress, completed)
- Priority levels (low, medium, high)
- Due date management with overdue detection
- Task categorization
- Advanced filtering (by status, priority, date ranges)
- Search functionality
- Bulk operations (create, update, delete)

### 📋 Categories
- Create and manage task categories
- Color-coded categories with hex color validation
- Optional icons for visual organization
- Category statistics

### ✅ Subtasks
- Break down tasks into smaller subtasks
- Track subtask completion with timestamps
- Toggle completion status

### 💬 Comments
- Add comments to tasks
- Edit and delete own comments
- Track comment timestamps (created_at, updated_at)

### 🔔 Reminders
- Set time-based reminders for tasks
- Track sent status with timestamps
- List upcoming reminders
- Automatic reminder management

### 📎 Attachments
- Upload files to tasks
- MIME type validation
- Download attachments
- Delete attachments
- Support for multiple file types (PDFs, images, documents)

### 👥 User Management (Admin)
- List all users
- Ban/unban users
- Update user information
- View user statistics

### 🛠️ Admin Features
- Admin dashboard with system statistics
- Database backup and restore
- System logs access
- Settings management

### 📊 Operational Endpoints
- Health check with database connectivity
- Version information
- System metrics (uptime, database status)
- API documentation (Swagger UI & ReDoc)

### 🔌 WebSocket Support
- Real-time notifications
- Task update broadcasts
- Reminder notifications
- Room-based task updates

## Tech Stack

- **Framework**: FastAPI 0.115.6
- **Database**: PostgreSQL with SQLAlchemy (async)
- **Task Queue**: Celery with RabbitMQ
- **Caching**: Redis
- **Authentication**: JWT (python-jose)
- **Password Hashing**: Passlib with bcrypt
- **Email**: Mailtrap API
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **Deployment**: Docker & Docker Compose

## Project Structure

```
todo_api/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/      # API route handlers
│   │   │   │   ├── auth.py
│   │   │   │   ├── task.py
│   │   │   │   ├── category.py
│   │   │   │   ├── user.py
│   │   │   │   └── attachment.py
│   │   │   └── deps.py         # Dependencies
│   │   └── routers.py          # Router configuration
│   ├── core/
│   │   ├── celery_app.py       # Celery configuration
│   │   └── security.py         # Security utilities
│   ├── crud/                   # Database operations
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── category.py
│   │   └── ...
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── task.py
│   │   └── ...
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── task.py
│   │   └── ...
│   ├── services/
│   │   ├── redis_service.py
│   │   └── ...
│   ├── tasks/                  # Celery tasks
│   │   └── email.py
│   ├── utils/
│   │   └── email.py
│   ├── ws/                     # WebSocket routes
│   │   └── routes.py
│   ├── config.py               # Settings
│   ├── database.py             # Database setup
│   └── main.py                 # Application entry
├── alembic/                    # Database migrations
├── media/                      # File uploads
├── scripts/                    # Utility scripts
├── docker-compose.yml
├── Dockerfile
└── requirements.txt

```

## Installation

### Prerequisites
- Python 3.12+
- PostgreSQL 15+
- Redis 7+
- RabbitMQ 3.12+

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd todo_api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
```env
DEBUG=True
API_TITLE=Todo API
API_VERSION=1.0.0
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/todo_db
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
CELERY_BROKER_URL=amqp://admin:password@localhost:5672//
CELERY_RESULT_BACKEND=redis://localhost:6379/0
MAILTRAP_API_TOKEN=your-mailtrap-token
```

5. **Run database migrations**
```bash
alembic upgrade head
```

6. **Start the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. **Start Celery worker** (in a separate terminal)
```bash
celery -A app.core.celery_app worker --loglevel=info
```

### Docker Deployment

```bash
docker-compose up -d
```

This will start:
- FastAPI application (port 8000)
- PostgreSQL database (port 5432)
- Redis (port 6379)
- RabbitMQ (port 5672, management UI: 15672)
- Celery worker

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/me` - Update profile
- `POST /api/v1/auth/change-password` - Change password

### Tasks
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks` - List tasks
- `GET /api/v1/tasks/{id}` - Get task
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `GET /api/v1/tasks/search` - Search tasks
- `GET /api/v1/tasks/overdue` - Get overdue tasks
- `GET /api/v1/tasks/priority/{level}` - Filter by priority
- `POST /api/v1/tasks/bulk` - Bulk create
- `DELETE /api/v1/tasks/bulk` - Bulk delete

### Categories
- `POST /api/v1/categories` - Create category
- `GET /api/v1/categories` - List categories
- `GET /api/v1/categories/{id}` - Get category
- `PUT /api/v1/categories/{id}` - Update category
- `DELETE /api/v1/categories/{id}` - Delete category

### Subtasks
- `GET /api/v1/subtasks/{id}` - Get subtask
- `PUT /api/v1/subtasks/{id}` - Update subtask
- `DELETE /api/v1/subtasks/{id}` - Delete subtask

### Comments
- `GET /api/v1/comments/{id}` - Get comment
- `PUT /api/v1/comments/{id}` - Update comment
- `DELETE /api/v1/comments/{id}` - Delete comment

### Reminders
- `POST /api/v1/reminders` - Create reminder
- `GET /api/v1/reminders` - List reminders
- `GET /api/v1/reminders/upcoming` - Get upcoming reminders
- `GET /api/v1/reminders/{id}` - Get reminder
- `PUT /api/v1/reminders/{id}` - Update reminder
- `DELETE /api/v1/reminders/{id}` - Delete reminder

### Attachments
- `POST /api/v1/tasks/{task_id}/attachments` - Upload file
- `GET /api/v1/attachments/{id}` - Get attachment info
- `GET /api/v1/attachments/{id}/download` - Download file
- `DELETE /api/v1/attachments/{id}` - Delete attachment

### Admin
- `GET /api/v1/admin/dashboard` - Admin dashboard
- `POST /api/v1/admin/backup` - Create database backup
- `POST /api/v1/admin/restore` - Restore database
- `GET /api/v1/admin/logs` - Get system logs
- `GET /api/v1/admin/settings` - Get settings
- `PUT /api/v1/admin/settings` - Update settings

### Users (Admin)
- `GET /api/v1/users` - List all users
- `GET /api/v1/users/{id}` - Get user
- `POST /api/v1/users/{id}/ban` - Ban user
- `POST /api/v1/users/{id}/unban` - Unban user

### Operational
- `GET /health` - Health check
- `GET /version` - Version information
- `GET /metrics` - System metrics

### WebSocket
- `WS /ws/notifications` - Notification stream
- `WS /ws/reminders` - Reminder stream
- `WS /ws/tasks/{task_id}` - Task-specific updates

## Database Schema

### Users
- User authentication and profile information
- Admin role support
- Profile images

### Tasks
- Core task information
- Status tracking (pending, in-progress, completed)
- Priority levels (low, medium, high)
- Due dates and completion tracking
- Foreign keys to user and category

### Categories
- Task organization
- Color coding (#RRGGBB format)
- Optional icons

### Subtasks
- Task breakdown
- Completion tracking with timestamps

### Comments
- Task discussions
- Author tracking
- Timestamp tracking

### Reminders
- Time-based notifications
- Sent status tracking
- Task associations

### Attachments
- File metadata (filename, size, MIME type)
- File path storage
- Task associations

## Security

- Password hashing with bcrypt
- JWT token-based authentication
- Token refresh mechanism
- Admin role-based authorization
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration
- Input validation (Pydantic)
- File upload validation (MIME types)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please open an issue in the GitHub repository.