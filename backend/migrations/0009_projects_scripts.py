# Generated by Django 4.1.2 on 2023-02-24 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0008_remove_projects_scripts_alter_projects_plan"),
    ]

    operations = [
        migrations.AddField(
            model_name="projects",
            name="scripts",
            field=models.CharField(
                default="[]", max_length=500, null=True, verbose_name="压测脚本名称"
            ),
        ),
    ]
