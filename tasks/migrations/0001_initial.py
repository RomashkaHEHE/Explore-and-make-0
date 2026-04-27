import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_projects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='ProjectMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_members', to='tasks.project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_memberships', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['project', 'user'],
            },
        ),
        migrations.AddField(
            model_name='project',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='projects', through='tasks.ProjectMember', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=160)),
                ('description', models.TextField(blank=True)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=20)),
                ('status', models.CharField(choices=[('todo', 'To do'), ('in_progress', 'In progress'), ('review', 'Review'), ('done', 'Done')], default='todo', max_length=20)),
                ('deadline', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assignee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_tasks', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='tasks.project')),
            ],
            options={
                'ordering': ['deadline', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TaskComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_comments', to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='tasks.task')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='projectmember',
            constraint=models.UniqueConstraint(fields=('project', 'user'), name='unique_project_member'),
        ),
    ]
