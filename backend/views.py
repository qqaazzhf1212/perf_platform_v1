import json
import os
import re
import time
import threading
import subprocess
import sys

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.contrib.auth.models import User
from django_task_mq import mq_producer

from backend.models import Projects, Tasks, DB_django_task_mq


def login(request):
    form = json.loads(request.body)
    # print(type(form), form)
    # 用这个用户名和密码去 用户数据库表中找，如果找到的是用户就ok，如果找到的是一个None 那就不ok。
    USER = auth.authenticate(username=form['username'], password=form['password'])
    # print(USER)
    if USER:  # 证明找到用户了
        auth.login(request, USER)
        request.session['username'] = form['username']
        return HttpResponse(json.dumps({"result": 0}))
    else:  # 证明用户名密码错误
        return HttpResponse(json.dumps({"result": 1}))


def register(request):
    form = json.loads(request.body)
    # print(type(form), form)
    # 用户名和密码去 直接注册，注册成功就ok，注册失败就说明用户名已存在
    try:
        user = User.objects.create_user(username=form['username'], password=form['password'])
        user.save()
        return HttpResponse(json.dumps({"result": 0}))
    except:
        return HttpResponse(json.dumps({"result": 1}))


def logout(request):
    auth.logout(request)
    return redirect('/login/')


def get_echarts_data(request):
    res = {
        "legend_data": ['项目1', '项目2', '项目3'],
        "xAxis_data": ['9-15', '9-16', '9-17', '9-18', '9-19', '9-20', '9-21', '9-22', '9-23', '9-24', '9-25', '9-26'],
        "series": [
            {'name': '项目1', "data": [3, 1, 2, 29, 32, 12, 52, 23, 51, 35, 26, 16], 'type': 'line'},
            {'name': '项目2', "data": [33, 12, 24, 2, 3, 2, 5, 13, 21, 25, 26, 26], 'type': 'line'},
            {'name': '项目3', "data": [6, 21, 12, 19, 22, 15, 9, 2, 32, 5, 12, 36], 'type': 'line'}
        ]
    }

    style = {
        'label': {
            'show': True,
            'position': 'bottom',
            'fontSize': 10
        },
        # 'smooth': True,
        # 'step': 'middle',
    }

    for i in range(len(res['series'])):
        res['series'][i].update(style)

    return HttpResponse(json.dumps(res), content_type='application/json')


def get_projects(request):
    projects = list(Projects.objects.all().values())

    # print(type(res), res)
    return HttpResponse(json.dumps(projects))


def add_project(request):
    Projects.objects.create()
    return get_projects(request)


def delete_project(request):
    project_id = request.GET.get('project_id')
    Projects.objects.filter(id=project_id).delete()
    return get_projects(request)


def get_project_detail(request):
    project_id = request.GET.get('project_id')
    project_detail = list(Projects.objects.filter(id=project_id).values())[0]
    project_detail['scripts'] = eval(project_detail['scripts'])
    return HttpResponse(json.dumps(project_detail))


def save_project(request):
    project_detail = json.loads(request.body.decode('utf-8'))
    id = project_detail['id']
    Projects.objects.filter(id=id).update(**project_detail)
    return HttpResponse(json.dumps({"result": 0}))


def upload_script_file(request):
    script_model = request.POST.get('script_model')
    # print(script_name)
    myFile = request.FILES.get("script_file")
    finename = str(myFile)
    # print(type(finename), finename)
    with open('scripts/' + script_model + "/" + finename, 'wb+') as fp:
        for i in myFile.chunks():
            fp.write(i)
    return HttpResponse(json.dumps({"result": 0}))


def get_script_list(request):
    script_list = []
    scripts = []
    base_dir = os.getcwd()
    for path in ['other', 'python', 'go']:
        scripts += [path + '/' + i for i in os.listdir(os.path.join(base_dir, 'scripts', path))]

    for i in scripts:
        if 'init' in i:
            continue
        else:
            script_list.append(i)
    # print(scripts)
    # print(script_list)
    return HttpResponse(json.dumps(script_list))


def get_tasks(request):
    tasks = list(Tasks.objects.all().values())[::-1]
    for i in tasks:
        i['create_time'] = i['create_time'].strftime("%Y-%m-%d %H:%M:%S")

    # print(type(tasks),tasks)
    return HttpResponse(json.dumps(tasks))


def add_task(request):
    des = request.GET.get("des")
    project_id = request.GET.get("project_id")
    new = Tasks.objects.create(des=des, project_id=int(project_id), create_time=time.ctime())
    mq_id = mq_producer(DB_django_task_mq, topic='压测', message={"task_id": new.id})
    new.mq_id = mq_id
    new.save()
    return get_tasks(request)


def play(mq):
    def execute_other(filepath):
        print('other')
        subprocess.call('python3 {} mqid= {} '.format(filepath, mq.id), shell=True)

    def execute_python(filepath):
        print('python')
        subprocess.call('python3 {} mqid= {} '.format(filepath, mq.id), shell=True)

    def execute_go(filepath):
        print('go')
        subprocess.call('python3 {} mqid= {} '.format(filepath, mq.id), shell=True)

    def one_round(filepath, num, script_model):
        ts = []
        target = {"other": execute_other, "python": execute_python, "go": execute_go}[script_model]
        for i in range(int(num)):
            t = threading.Thread(target=target, args=[filepath, ])
            t.setDaemon(True)
            ts.append(t)
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        print('---结束了一轮压测---')

    message = json.loads(mq.message)
    task_id = message['task_id']
    task = Tasks.objects.filter(id=int(task_id))
    task.update(status='压测中')
    # ----

    ## 根据这个任务关联的项目id，去数据库找出这个项目的所有内容。
    project = Projects.objects.filter(id=int(task[0].project_id))[0]
    scripts = eval(project.scripts)
    # print(scripts)
    for step in project.plan.split(','):
        script = scripts[int(step.split('-')[0])].split('/')

        # round = int(step.split('-')[2])
        filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts', script[0],
                                script[1])
        # print(filepath)
        tsr = []
        if '+' in step:  # 无限增压
            round = 100  # 安全阀
        elif '_' in step:  # 瞬时增压
            round = int(step.split('-')[2]) * (step.count('_') + 1)
        else:
            round = int(step.split('-')[2])

        for r in range(round):
            if '/' in step:  # 阶梯增加
                mid = step.split('-')[1]  # 10/90
                num = int(int(mid.split('/')[0]) + (int(mid.split('/')[1]) - int(mid.split('/')[0])) / (round - 1) * r)
            elif '+' in step:  # 无限增压
                mid = step.split('-')[1]  # 1+5
                num = int(int(mid.split('+')[0]) + int(mid.split('+')[1]) * r)
            elif '_' in step:  # 瞬时增压
                mid = step.split('-')[1]  # 10_100_1000   r=0,1,2,3,4=10=0 ,r=5,6,7,8,9=100=1, r=10,11,12,13,14=1000=2
                mid = mid.split('_')  # [10,100,1000]
                num = int(mid[int(r / int(step.split('-')[2]))])
            else:
                num = int(step.split('-')[1])
            print(num)
            tr = threading.Thread(target=one_round, args=[filepath, num, script[0]])
            tr.setDaemon(True)
            tsr.append(tr)
        for t in tsr:
            # 路障
            now_task = Tasks.objects.filter(id=task_id)[0]
            if now_task.stop == True:
                break
            t.start()
            time.sleep(1)
        for t in tsr:
            t.join()
        print('-----------结束了一个阶段压测计划---------')
    print('【整个压测任务结束】')
    # ----
    task.update(status='已结束')


def stop_task(request):
    def s_mac():
        ts = subprocess.check_output('ps -ef |grep mqid=%s |grep -v "grep"' % str(mq_id), shell=True)
        for t in str(ts).split('mqid=' + str(mq_id)):
            s = re.findall(r'\b(\d+?)\b', t)[:3]
            if s:
                pid = max([int(i) for i in s])
                subprocess.call('kill -9 ' + str(pid), shell=True)

    def s_win():
        # ts = subprocess.check_output('wmic process where caption="python.exe" get processid,commandline', shell=True)
        ts = subprocess.check_output('tasklist | findstr "py"', shell=True)
        for t in str(ts).split(r'\n'):
            # print(t)
            if 'python3' in t:
                # pid = re.findall(r'\b(\d+?)\b', t)[-1]
                pid = pid = re.findall(r'\b(\d+?)\b', t)[0]
                # print(pid)
                # print(eval(pid))
                subprocess.call('taskkill /T /F /PID %s' % pid, shell=True)

    task_id = request.GET.get('id')
    task = Tasks.objects.filter(id=int(task_id))[0]
    mq_id = task.mq_id
    if task.status == '队列中':
        DB_django_task_mq.objects.filter(id=int(mq_id)).delete()
        # mq = DB_django_task_mq.objects.filter(id=int(mq_id))
        # mq.update(status=False)
        # mq.save()
        task.status = '队列中时结束'
        task.save()
    if task.status == '压测中':
        task.stop = True
        task.save()
        for j in range(100):
            now_task = Tasks.objects.filter(id=task_id)[0]
            if now_task.status == '压测中':
                try:
                    time.sleep(2)
                    if 'win' in sys.platform:
                        s_win()
                    else:
                        s_mac()
                except:
                    break
                finally:
                    now_task.status = '压测中时结束'
                    now_task.save()
            else:
                break
        return HttpResponse(json.dumps({"errorCode": 300, "data": [], "Message": "任务已结束"}))

    return HttpResponse(json.dumps({"errorCode": 200, "data": [], "Message": "终止成功"}))
