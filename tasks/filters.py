import django_filters

from tasks.models import Task


class TaskFilter(django_filters.FilterSet):
    """Фильтры для списка задач."""

    deadline_from = django_filters.DateFilter(
        field_name="deadline",
        lookup_expr="gte",
    )
    deadline_to = django_filters.DateFilter(
        field_name="deadline",
        lookup_expr="lte",
    )

    class Meta:
        model = Task
        fields = [
            "project",
            "status",
            "priority",
            "assignee",
            "deadline",
            "deadline_from",
            "deadline_to",
        ]
