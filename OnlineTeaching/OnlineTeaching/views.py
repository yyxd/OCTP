from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from Teacher.models import *


# 系统首页
def index(request):
    context = {'username': request.session.get('name', '')}
    return render(request, 'index.html', context)


# 统一登录页面
def login(request):
    # TODO 已登录自动跳转首页
    context = {'username': request.session.get('name', '')}
    return render(request, 'login.html', context)


# 登出接口
def logout(request):
    try:
        del request.session['uid']
        del request.session['name']
        del request.session['role']
    except KeyError:
        pass
    return HttpResponseRedirect('/')  # 直接跳转到首页


# 测试接口
def test(request):
    return JsonResponse(request.session.__str__())
###############黄丹#################

# 添加基本数据,运行一次即可
def addTestData(request):
    course1 = Courses(Name='软件工程过程', Department='软件学院',type=1, Semester='一', Weeks=7, StudentCount=139, credit=5)
    course1.save()
    course2 = Courses(Name='数据结构', Department='软件学院', Semester='一', Weeks=7, StudentCount=139, credit=5)
    course2.save()
    course3 = Courses(Name='算法导论', Department='软件学院', Semester='一', Weeks=7, StudentCount=139, credit=5)
    course3.save()
    course4 = Courses(Name='编译原理', Department='软件学院', Semester='一', Weeks=7, StudentCount=139, credit=5)
    course4.save()
    course5 = Courses(Name='计算机网络', Department='软件学院', Semester='一', Weeks=7, StudentCount=139, credit=5)
    course5.save()

    teacher1 = Teachers(TNo=11, Name="谭火彬", Department='软件学院', Sex='男', Pwd='123456')
    teacher2 = Teachers(TNo=21, Name="贾经冬", Department='软件学院', Sex='女', Pwd='123456')
    teacher3 = Teachers(TNo=31, Name="三傻", Department='软件学院', Sex='女', Pwd='123456')
    teacher4 = Teachers(TNo=41, Name="瑞肯", Department='软件学院', Sex='男', Pwd='123456')
    teacher5 = Teachers(TNo=51, Name="奈德", Department='软件学院', Sex='男', Pwd='123456')
    teacher6 = Teachers(TNo=61, Name="小玫瑰", Department='软件学院', Sex='女', Pwd='123456')
    teacher7 = Teachers(TNo=71, Name="林广艳", Department='软件学院', Sex='女', Pwd='123456')
    teacher1.save()
    teacher2.save()
    teacher3.save()
    teacher4.save()
    teacher5.save()
    teacher6.save()
    teacher7.save()

    student1 = Students(SNo=13211030, Name="黄丹", Department='软件学院', Sex='女', Pwd='123456')
    student2 = Students(SNo=13211017, Name="朱运昌", Department='软件学院', Sex='男', Pwd='123456')
    student3 = Students(SNo=13211027, Name="陈煜", Department='软件学院', Sex='男', Pwd='123456')
    student4 = Students(SNo=13211003, Name="顾瑾", Department='软件学院', Sex='女', Pwd='123456')
    student5 = Students(SNo=13211026, Name="刘京欣", Department='软件学院', Sex='男', Pwd='123456')
    student6 = Students(SNo=11211016, Name="刘阳光", Department='软件学院', Sex='男', Pwd='123456')
    student7 = Students(SNo=13211037, Name="董舒印", Department='软件学院', Sex='男', Pwd='123456')

    student1.save()
    student2.save()
    student3.save()
    student4.save()
    student5.save()
    student6.save()
    student7.save()

    stt1 = STT(Course=course1, SNo=student1)
    stt2 = STT(Course=course1, SNo=student2)
    stt3 = STT(Course=course1, SNo=student3)
    stt4 = STT(Course=course1, SNo=student4)
    stt5 = STT(Course=course1, SNo=student5)
    stt6 = STT(Course=course1, SNo=student6)
    stt7 = STT(Course=course1, SNo=student7)

    stt8 = STT(Course=course2, SNo=student1)
    stt9 = STT(Course=course2, SNo=student2)
    stt10 = STT(Course=course2, SNo=student3)
    stt11= STT(Course=course2, SNo=student4)
    stt12 = STT(Course=course2, SNo=student5)
    stt13 = STT(Course=course2, SNo=student6)
    stt14= STT(Course=course2, SNo=student7)

    stt15 = STT(Course=course3, SNo=student1)
    stt16 = STT(Course=course5, SNo=student1)
    stt17= STT(Course=course4, SNo=student2)
    stt18= STT(Course=course3, SNo=student3)
    stt19= STT(Course=course4, SNo=student3)
    stt20 = STT(Course=course3, SNo=student4)
    stt21 = STT(Course=course4, SNo=student4)
    stt22 = STT(Course=course5, SNo=student4)
    stt23 = STT(Course=course5, SNo=student5)


    stt1.save()
    stt2.save()
    stt3.save()
    stt4.save()
    stt5.save()
    stt6.save()
    stt7.save()
    stt8.save()
    stt9.save()
    stt10.save()
    stt11.save()
    stt12.save()
    stt13.save()
    stt14.save()
    stt15.save()
    stt16.save()
    stt17.save()
    stt18.save()
    stt19.save()
    stt20.save()
    stt21.save()
    stt22.save()
    stt23.save()

    tc1 = TeachCourse(TNo=teacher1, Course=course1)
    tc2 = TeachCourse(TNo=teacher2, Course=course1)
    tc3 = TeachCourse(TNo=teacher7, Course=course2)
    tc4 = TeachCourse(TNo=teacher7, Course=course1)
    tc5 = TeachCourse(TNo=teacher2, Course=course2)
    tc6 = TeachCourse(TNo=teacher3, Course=course3)
    tc7 = TeachCourse(TNo=teacher4, Course=course4)
    tc8 = TeachCourse(TNo=teacher5, Course=course5)



    tc1.save()
    tc2.save()
    tc3.save()
    tc4.save()
    tc5.save()
    tc6.save()
    tc7.save()
    tc8.save()
    return HttpResponse('Hello')

###############黄丹#################
