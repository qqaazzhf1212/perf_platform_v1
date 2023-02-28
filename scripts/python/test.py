import subprocess
import time

# print("我是脚本11111，我正在被执行", time.time())
# time.sleep(3)
# print("我执行完了", time.time())

b=subprocess.check_output('tasklist | findstr "py"', shell=True)

for t in str(b).split(r'\n'):
    print(t)

a = "python3.exe                  17704 Console                    1     37,408 K\r"

import re

# pid = re.findall(r'[1-9]{5}', a)
pid = re.findall(r'\b(\d+?)\b', a)[0]
print(pid)


import sys
print(sys.platform)