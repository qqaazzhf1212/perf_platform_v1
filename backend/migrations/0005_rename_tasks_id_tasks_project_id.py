# Generated by Django 4.1.2 on 2023-02-15 06:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0004_tasks"),
    ]

    operations = [
        migrations.RenameField(
            model_name="tasks",
            old_name="tasks_id",
            new_name="project_id",
        ),
    ]
