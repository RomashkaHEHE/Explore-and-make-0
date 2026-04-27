from django.urls import include, path
from rest_framework.routers import DefaultRouter

from tasks.views import (
    ProjectMemberViewSet,
    ProjectViewSet,
    RegisterView,
    TaskCommentViewSet,
    TaskViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("projects", ProjectViewSet, basename="project")
router.register("project-members", ProjectMemberViewSet, basename="project-member")
router.register("tasks", TaskViewSet, basename="task")
router.register("comments", TaskCommentViewSet, basename="comment")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/", include("rest_framework.urls")),
    path("", include(router.urls)),
]
