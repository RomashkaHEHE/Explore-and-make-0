def user_in_project(user, project):
    """
    Проверяет, что пользователь реально связан с проектом.
    Args:
        user: Django user object.
        project: Project object.
    Returns:
        bool: True if user is project owner or member.
    Raises:
        None
    """
    if not user or not user.is_authenticated:
        return False
    return (
        project.owner_id == user.id
        or project.project_members.filter(user=user).exists()
    )
