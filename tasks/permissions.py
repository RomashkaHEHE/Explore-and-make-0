from rest_framework.permissions import SAFE_METHODS, BasePermission

from tasks.utils import user_in_project


class ProjectPermission(BasePermission):
    """Права для просмотра и изменения проектов."""

    def has_object_permission(self, request, view, obj):
        """
        Решает, что можно делать с конкретным проектом.
        Args:
            self (ProjectPermission): Текущий permission-класс.
            request (Request): DRF request object.
            view (APIView): DRF view object.
            obj (Project): Project object.
        Returns:
            bool: True if action is allowed.
        Raises:
            None
        """
        if request.method in SAFE_METHODS:
            return user_in_project(request.user, obj)
        return obj.owner_id == request.user.id


class ProjectMemberPermission(BasePermission):
    """Права для списка участников проекта."""

    def has_object_permission(self, request, view, obj):
        """
        Проверяет доступ к конкретной записи участника проекта.
        Args:
            self (ProjectMemberPermission): Текущий permission-класс.
            request (Request): DRF request object.
            view (APIView): DRF view object.
            obj (ProjectMember): ProjectMember object.
        Returns:
            bool: True if action is allowed.
        Raises:
            None
        """
        if request.method in SAFE_METHODS:
            return user_in_project(request.user, obj.project)
        return obj.project.owner_id == request.user.id


class TaskPermission(BasePermission):
    """Права для задач с простыми правилами из задания."""

    def has_object_permission(self, request, view, obj):
        """
        Проверяет, какие поля задачи можно менять пользователю.
        Args:
            self (TaskPermission): Текущий permission-класс.
            request (Request): DRF request object.
            view (APIView): DRF view object.
            obj (Task): Task object.
        Returns:
            bool: True if action is allowed.
        Raises:
            None
        """
        if request.method in SAFE_METHODS:
            return user_in_project(request.user, obj.project)

        if obj.project.owner_id == request.user.id:
            return True

        if request.method == "DELETE":
            return obj.author_id == request.user.id

        changed_fields = set(request.data.keys())

        if obj.assignee_id == request.user.id:
            return changed_fields.issubset({"status", "priority"})

        if obj.author_id == request.user.id:
            return changed_fields.issubset({"description"})

        return False


class TaskCommentPermission(BasePermission):
    """Права для комментариев к задачам."""

    def has_object_permission(self, request, view, obj):
        """
        Проверяет доступ к конкретному комментарию.
        Args:
            self (TaskCommentPermission): Текущий permission-класс.
            request (Request): DRF request object.
            view (APIView): DRF view object.
            obj (TaskComment): TaskComment object.
        Returns:
            bool: True if action is allowed.
        Raises:
            None
        """
        if request.method in SAFE_METHODS:
            return user_in_project(request.user, obj.task.project)

        if obj.task.project.owner_id == request.user.id:
            return True

        return obj.author_id == request.user.id
