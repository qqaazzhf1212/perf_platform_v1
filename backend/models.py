from django.db import models


# Create your models here.
class Projects(models.Model):
    name = models.CharField(max_length=30, null=True, blank=True, default='new project', verbose_name='压测名称')
    scripts = models.CharField(max_length=500, null=True, default='[]', verbose_name='压测脚本名称')  # 关联的脚本名字，按顺序。
    plan = models.CharField(max_length=1000, null=True, blank=True, default='',
                            verbose_name='压测计划')  # 压测计划，专用的关键字语法。（可保存成模版）

    def __str__(self):
        return self.name


class Tasks(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='任务创建时间')
    des = models.CharField(max_length=500, null=True, blank=True, default='', verbose_name='任务描述')
    project_id = models.IntegerField(default=0, verbose_name='项目id')
    status = models.CharField(max_length=10, null=True, blank=True, default='队列中',
                              verbose_name='正常状态')  # 队列中 ， 压测中，已结束
    mq_id = models.IntegerField(default=0, verbose_name='mq的id')
    stop = models.BooleanField(default=False, verbose_name='异常终止')  # 终止状态

    def __str__(self):
        return self.des


class DB_django_task_mq(models.Model):
    topic = models.CharField(max_length=100, null=True, blank=True, default="")
    message = models.TextField(default="{}")
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.topic
