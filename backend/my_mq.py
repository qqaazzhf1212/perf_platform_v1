import os, sys, django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '%s.settings' % 'perf_platform')  # 引号中请输入您的setting父级目录名
django.setup()

from backend.models import DB_django_task_mq
from django_task_mq import mq_consumer, mq_producer
from backend.views import play

mq_consumer(DB_django_task_mq, play, topic='压测')

# 初始化时执行
# import os
# from django_task_mq import mq_init
# mq_init(os.path.dirname(os.path.abspath(__file__)))
