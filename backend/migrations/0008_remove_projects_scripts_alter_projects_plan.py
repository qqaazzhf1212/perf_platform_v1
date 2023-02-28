# Generated by Django 4.1.2 on 2023-02-24 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0007_tasks_mq_id_tasks_stop_alter_tasks_des_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="projects",
            name="scripts",
        ),
        migrations.AlterField(
            model_name="projects",
            name="plan",
            field=models.CharField(
                blank=True, default="", max_length=1000, null=True, verbose_name="压测计划"
            ),
        ),
    ]
