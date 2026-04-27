from django.contrib.auth import get_user_model
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated

from tasks.filters import TaskFilter
from tasks.models import Project, ProjectMember, Task, TaskComment
from tasks.permissions import (
    ProjectMemberPermission,
    ProjectPermission,
    TaskCommentPermission,
    TaskPermission,
)
from tasks.serializers import (
    ProjectMemberSerializer,
    ProjectSerializer,
    TaskCommentSerializer,
    TaskSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Список пользователей, чтобы было кого добавлять в проекты."""

    queryset = User.objects.all().order_by("username")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["username", "email"]


class ProjectViewSet(viewsets.ModelViewSet):
    """API для проектов."""

    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, ProjectPermission]
    lookup_value_regex = r"\d+"
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "created_at", "updated_at"]

    def get_queryset(self):
        """
        Возвращает только проекты, где пользователь владелец или участник.
        Args:
            None
        Returns:
            QuerySet: Projects available for current user.
        Raises:
            None
        """
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return Project.objects.none()

        return (
            Project.objects.filter(Q(owner=user) | Q(members=user))
            .select_related("owner")
            .prefetch_related("members")
            .distinct()
        )

    def perform_create(self, serializer):
        """
        Сохраняет проект и сразу добавляет создателя в участники.
        Args:
            serializer: Project serializer with checked data.
        Returns:
            None
        Raises:
            None
        """
        project = serializer.save(owner=self.request.user)
        ProjectMember.objects.get_or_create(
            project=project,
            user=self.request.user,
        )


class ProjectMemberViewSet(viewsets.ModelViewSet):
    """API для участников проекта."""

    serializer_class = ProjectMemberSerializer
    permission_classes = [IsAuthenticated, ProjectMemberPermission]
    lookup_value_regex = r"\d+"
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["project", "user"]
    ordering_fields = ["joined_at"]

    def get_queryset(self):
        """
        Показывает участников только из доступных пользователю проектов.
        Args:
            None
        Returns:
            QuerySet: Project members from visible projects.
        Raises:
            None
        """
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return ProjectMember.objects.none()

        return (
            ProjectMember.objects.filter(
                Q(project__owner=user) | Q(project__members=user)
            )
            .select_related("project", "user")
            .distinct()
        )

    def perform_destroy(self, instance):
        """
        Удаляет участника, но не дает убрать владельца из его проекта.
        Args:
            instance: ProjectMember object.
        Returns:
            None
        Raises:
            ValidationError: If owner is removed from own project.
        """
        if instance.project.owner_id == instance.user_id:
            raise ValidationError("Project owner cannot be removed.")
        instance.delete()


class TaskViewSet(viewsets.ModelViewSet):
    """API для задач."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, TaskPermission]
    lookup_value_regex = r"\d+"
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["deadline", "created_at", "updated_at", "priority"]

    def get_queryset(self):
        """
        Возвращает задачи только из проектов текущего пользователя.
        Args:
            None
        Returns:
            QuerySet: Tasks from visible projects.
        Raises:
            None
        """
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return Task.objects.none()

        return (
            Task.objects.filter(Q(project__owner=user) | Q(project__members=user))
            .select_related("project", "author", "assignee")
            .distinct()
        )

    def perform_create(self, serializer):
        """
        Сохраняет задачу и ставит текущего пользователя автором.
        Args:
            serializer: Task serializer with checked data.
        Returns:
            None
        Raises:
            None
        """
        serializer.save(author=self.request.user)


class TaskCommentViewSet(viewsets.ModelViewSet):
    """API для комментариев к задачам."""

    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated, TaskCommentPermission]
    lookup_value_regex = r"\d+"
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["task", "author"]
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        """
        Возвращает комментарии только к задачам доступных проектов.
        Args:
            None
        Returns:
            QuerySet: Task comments from visible projects.
        Raises:
            None
        """
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return TaskComment.objects.none()

        return (
            TaskComment.objects.filter(
                Q(task__project__owner=user) | Q(task__project__members=user)
            )
            .select_related("task", "author")
            .distinct()
        )

    def perform_create(self, serializer):
        """
        Сохраняет комментарий от имени текущего пользователя.
        Args:
            serializer: Task comment serializer with checked data.
        Returns:
            None
        Raises:
            None
        """
        serializer.save(author=self.request.user)
