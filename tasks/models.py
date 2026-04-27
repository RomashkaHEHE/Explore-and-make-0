from django.conf import settings
from django.db import models


class Project(models.Model):
    """Проект, где команда хранит свои задачи и участников."""

    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="ProjectMember",
        related_name="projects",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        """
        Возвращает название проекта, чтобы в админке было понятно.
        Args:
            None
        Returns:
            str: Project title.
        Raises:
            None
        """
        return self.title


class ProjectMember(models.Model):
    """Связь между проектом и пользователем из команды."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="project_members",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["project", "user"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"],
                name="unique_project_member",
            )
        ]

    def __str__(self):
        """
        Собирает короткую подпись участника проекта.
        Args:
            None
        Returns:
            str: Project and username text.
        Raises:
            None
        """
        return f"{self.project.title}: {self.user.username}"


class Task(models.Model):
    """Задача внутри проекта с автором, исполнителем и дедлайном."""

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class Status(models.TextChoices):
        TODO = "todo", "To do"
        IN_PROGRESS = "in_progress", "In progress"
        REVIEW = "review", "Review"
        DONE = "done", "Done"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
    )
    deadline = models.DateField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tasks",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_tasks",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["deadline", "-created_at"]

    def __str__(self):
        """
        Возвращает заголовок задачи для списков и админки.
        Args:
            None
        Returns:
            str: Task title.
        Raises:
            None
        """
        return self.title


class TaskComment(models.Model):
    """Комментарий к задаче, чтобы обсуждение не терялось в чатах."""

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="task_comments",
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        """
        Делает короткую подпись комментария, чтобы не выводить весь текст.
        Args:
            None
        Returns:
            str: Short comment text.
        Raises:
            None
        """
        return self.text[:40]
