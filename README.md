# Alpha Soft Task Tracker API
# napisal 666!^^!!!

Учебный таск-трекер на Django REST Framework для практики. В проекте есть
регистрация пользователей, проекты, участники проектов, задачи и комментарии.

## Запуск

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

После запуска:

- Swagger: `http://127.0.0.1:8000/api/docs/`
- ReDoc: `http://127.0.0.1:8000/api/redoc/`
- Admin: `http://127.0.0.1:8000/admin/`

## Основные URL

- `POST /api/auth/register/` — регистрация пользователя;
- `/api/auth/login/` — вход через browsable API;
- `/api/users/` — список пользователей;
- `/api/projects/` — проекты;
- `/api/project-members/` — участники проектов;
- `/api/tasks/` — задачи;
- `/api/comments/` — комментарии.

## Фильтрация задач

Примеры:

```text
/api/tasks/?project=1
/api/tasks/?status=in_progress
/api/tasks/?priority=high
/api/tasks/?assignee=2
/api/tasks/?deadline=2026-05-01
/api/tasks/?deadline_from=2026-05-01&deadline_to=2026-05-20
```

Пагинация:

```text
/api/tasks/?page=2
/api/tasks/?page_size=20
```