from django.contrib.auth import get_user_model
from rest_framework import serializers

from tasks.models import Project, ProjectMember, Task, TaskComment
from tasks.utils import user_in_project

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Короткая информация о пользователе для ответов API."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для обычной регистрации сотрудника."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        """
        Создает пользователя и нормально сохраняет пароль через Django.
        Args:
            self (UserRegistrationSerializer): Текущий сериализатор.
            validated_data (dict): Проверенные данные пользователя.
        Returns:
            User: Created user object.
        Raises:
            None
        """
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProjectSerializer(serializers.ModelSerializer):
    """Сериализатор проекта с владельцем и списком участников."""

    owner = UserSerializer(read_only=True)
    members = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "owner",
            "members",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "members", "created_at", "updated_at"]


class ProjectMemberSerializer(serializers.ModelSerializer):
    """Сериализатор участника проекта."""

    class Meta:
        model = ProjectMember
        fields = ["id", "project", "user", "joined_at"]
        read_only_fields = ["id", "joined_at"]

    def validate(self, attrs):
        """
        Проверяет, что участников меняет только владелец проекта.
        Args:
            self (ProjectMemberSerializer): Текущий сериализатор.
            attrs (dict): Данные участника проекта.
        Returns:
            dict: Validated member data.
        Raises:
            ValidationError: If user cannot manage this project.
        """
        request = self.context.get("request")
        project = attrs.get("project") or self.instance.project
        user = attrs.get("user") or self.instance.user

        if project.owner_id != request.user.id:
            raise serializers.ValidationError(
                "Only project owner can manage members."
            )

        same_members = ProjectMember.objects.filter(project=project, user=user)
        if self.instance:
            same_members = same_members.exclude(pk=self.instance.pk)

        if same_members.exists():
            raise serializers.ValidationError(
                "This user is already in the project."
            )

        return attrs


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор задачи с проверкой проекта и исполнителя."""

    author = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "title",
            "description",
            "priority",
            "status",
            "deadline",
            "author",
            "assignee",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author", "created_at", "updated_at"]

    def validate(self, attrs):
        """
        Проверяет, что задача не выходит за пределы своего проекта.
        Args:
            self (TaskSerializer): Текущий сериализатор.
            attrs (dict): Данные задачи.
        Returns:
            dict: Validated task data.
        Raises:
            ValidationError: If user or assignee is not in project.
        """
        request = self.context.get("request")
        project = attrs.get("project") or self.instance.project
        assignee = attrs.get("assignee") or self.instance.assignee

        if not user_in_project(request.user, project):
            raise serializers.ValidationError(
                "Only project members can create or edit tasks."
            )

        if not user_in_project(assignee, project):
            raise serializers.ValidationError(
                "Assignee must be a project member."
            )

        return attrs


class TaskCommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария к задаче."""

    author = UserSerializer(read_only=True)

    class Meta:
        model = TaskComment
        fields = [
            "id",
            "task",
            "author",
            "text",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author", "created_at", "updated_at"]

    def validate(self, attrs):
        """
        Проверяет, что комментарий пишет участник нужного проекта.
        Args:
            self (TaskCommentSerializer): Текущий сериализатор.
            attrs (dict): Данные комментария.
        Returns:
            dict: Validated comment data.
        Raises:
            ValidationError: If user is not in task project.
        """
        request = self.context.get("request")
        task = attrs.get("task") or self.instance.task

        if not user_in_project(request.user, task.project):
            raise serializers.ValidationError(
                "Only project members can comment task."
            )

        return attrs
