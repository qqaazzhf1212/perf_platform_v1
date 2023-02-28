from django.test import TestCase

# Create your tests here.

import threading
import time


def a():
    print('哈哈哈', time.time())
    time.sleep(2)
    print('呵呵呵',time.time())


ts = []

for i in range(10):
    t = threading.Thread(target=a)
    t.setDaemon(True)
    ts.append(t)

for t in ts:
    t.start()

for t in ts:
    t.join()