from django.contrib import admin
from backend.models import Projects, Tasks, DB_django_task_mq

# Register your models here.


admin.site.register(Projects)
admin.site.register(Tasks)

admin.site.register(DB_django_task_mq)
