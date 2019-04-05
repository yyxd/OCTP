from django.shortcuts import render
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from Teacher.models import *
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
import zipfile
import json
import urllib
import shutil
import xlrd


def index(request):
    context = {}
    try:
        context['uid'] = request.session.get('uid')
    finally:
        return render(request, 'Admin/index.html', context)


# 管理员登录接口
def login(request):
    # return HttpResponse("12333")
    if request.method == "GET":
        return HttpResponseRedirect("/login")
    ano = request.POST.get('id', '')
    password = request.POST.get('pwd', '')
    response = {'result': 0}
    try:
        admin = Admin.objects.get(ANo=ano)
        if admin.Pwd == password:
            request.session['uid'] = ano
            request.session['name'] = admin.Name
            request.session['role'] = 0
            response['result'] = 1
    except Exception as e:
        response['result'] = 0
    return JsonResponse(response)


# 管理员学期设置页面
def semestersetting(request):
    context = {}
    try:
        context['uid'] = request.session.get('uid')
    finally:
        return render(request, 'Admin/SemesterSet.html', context)


# 管理员课程设置页面
def coursesetting(request):
    context = {}
    try:
        context['uid'] = request.session.get('uid')
    finally:
        return render(request, 'Admin/CourseSet.html', context)


def studentsetting(request):
    context = {}
    try:
        context['uid'] = request.session.get('uid')
    finally:
        return render(request, 'Admin/StudentSet.html', context)


def teachersetting(request):
    context = {}
    try:
        context['uid'] = request.session.get('uid')
    finally:
        return render(request, 'Admin/TeacherSet.html', context)

def teacherSetting(request):
    context = {}
    return render(request, 'Admin/TeacherSet.html', context)

#上传教师的excel
def uploadTeacherInfo(request):
    if request.method == 'POST':
        context = {}
        context['uid'] = request.session.get('uid')
        file = request.FILES.get('uploadfile', None)
        saveStatus=savefile(file,MEDIA_ROOT+'tmp/')
        path = MEDIA_ROOT + 'tmp/' + file.name;
        try:
            data = xlrd.open_workbook(path)
            table = data.sheets()[0]  # 获取excel表中的第一个sheet
            rows = table.nrows  # 获取excel中的行数
            cols = table.ncols  # 获取excel中的列数
        except Exception as e:
            print(e)
        teacherList = []
        for i in range(1, rows):  # 第一行为title,循环不要读取
            teacher = {}
            for j in range(cols):
                if table.row(0)[j].value == 'ID':
                    teacher['id'] = table.row(i)[j]
                    if type(teacher['id'].value) == type(1):  # 此时teacher[id]为整数
                        Teacher.TNo = teacher['id']
                    elif type(teacher['id'].value) == type("123"):  # 此时teacher[id]为字符串
                        Teacher.TNo = int(teacher['id'])
                    elif type(teacher['id'].value) == type(123.123):
                        try:
                            teacher['id'] = int(teacher['id'].value)
                        except Exception as e:
                            print(e)
                elif table.row(0)[j].value == '姓名':
                    teacher['name'] = table.row(i)[j].value
                elif table.row(0)[j].value == '性别':
                    teacher['sex'] = table.row(i)[j].value
                elif table.row(0)[j].value == '院系':
                    teacher['department'] = table.row(i)[j].value
            teacher['originpwd'] = '000000'

            Teacher = Teachers()
            try:

                Teacher.TNo = teacher['id']
                Teacher.Name = teacher['name']
                Teacher.Sex = teacher['sex']
                Teacher.Department = teacher['department']
                Teacher.Pwd = teacher['originpwd']
                print(type(Teacher.TNo))
                print(type(Teacher.Name))
                print(type(Teacher.Sex))
                print(type(Teacher.Department))
                print(type(Teacher.Pwd))

                Teacher.save()
                teacherList.append(teacher)
            except Exception as e:
                print(e)
        context['teacherList'] = teacherList
        context['status'] = 'success'
        context['info'] = 'the teacher info has been uploaded succefully'
    return JsonResponse(context)


#上传学生的excel
def uploadStudentInfo(request):
    if request.method == 'POST':
        context = {}
        context['uid'] = request.session.get('uid')
        file = request.FILES.get('uploadfile', None)
        data = xlrd.open_workbook(file)
        table = data.sheets()[0]  # 获取excel表中的第一个sheet
        rows = table.nrows  # 获取excel中的行数
        cols = table.ncols  # 获取excel中的列数
        stuList = []
        for i in range(1, rows):  # 第一行为title,循环不要读取
            student = {}
            for j in range(cols):
                if table.row(0)[j].value == 'ID':
                    student['id'] = table.row(i)[j]
                elif table.row(0)[j].value == '姓名':
                    student['name'] = table.row(i)[j]
                elif table.row(0)[j].value == '性别':
                    student['sex'] = table.row(i)[j]
                elif table.row(0)[j].value == '院系':
                    student['department'] = table.row(i)[j]
            student['originpwd'] = '000000'
            Student = Students()
            if type(student['id']) == type(1):  # 此时teacher[id]为整数
                Student.TNo = student['id']
            elif type(student['id']) == type("123"):  # 此时teacher[id]为字符串
                Student.TNo = int(student['id'])
            Student.Name = student['name']
            Student.Sex = student['sex']
            Student.Department = student['department']
            Student.Pwd = student['originpwd']
            Student.save()
            stuList.append(student)
        context['studentList'] = stuList
        context['status'] = 'success'
        context['info'] = 'the student info has been uploaded successfully'
    return JsonResponse(context)



#上传课程的excel
def uploadCourseInfo(request):
    if request.method == 'POST':
        context = {}
        context['uid'] = request.session.get('uid')
        file = request.FILES.get('uploadfile', None)
        data = xlrd.open_workbook(file)
        table = data.sheets()[0]  # 获取excel表中的第一个sheet
        rows = table.nrows  # 获取excel中的行数
        cols = table.ncols  # 获取excel中的列数
        courseList = []
        for i in range(1, rows):  # 第一行为title,循环不要读取
            course = {}
            for j in range(cols):
                if table.row(0)[j].value == '课程名':
                    course['name'] = table.row(i)[j]
                elif table.row(0)[j].value == '任课教师':
                    course['teacher'] = table.row(i)[j]
                elif table.row(0)[j].value == '院系':
                    course['department'] = table.row(i)[j]
                elif table.row(0)[j].value =='课程编号':
                    course['id'] =  table.row(i)[j]
                elif table.row(0)[j].value =='教师编号':
                    course['teacherId'] = table.row(i)[j]
                elif table.row(0)[j].value =='学分':
                    course['credit'] = table.row(i)[j]
                elif table.row(0)[j].value == '讲课学时':
                    course['teachHour'] = table.row(i)[j]
                elif table.row(0)[j].value == '实践学时':
                    course['practiceHour'] = table.row(i)[j]

            Course = Courses()
            if type(course['id']) == type(1):  # 此时teacher[id]为整数
                Course.id = course['id']
            elif type(course['id']) == type("123"):  # 此时teacher[id]为字符串
                Course.id = int(course['id'])
            Course.Name = course['name']
            Course.Department = course['department']
            Course.credit = course['credit']
            Course.teachHour = course['teacherHour']
            Course.practiceHour = course['practiceHour']

            teachCourse = TeachCourse(Course_id= course['id'],TNo_id=course['teacherId'])
            teachCourse.save()
            courseList.append(course)

        context['courseList'] = courseList
        return JsonResponse(context)


# 修改教师信息功能，需要传来教师Id
def teacherInfoModify(request, id):
    if request.method == 'POST':
        context = {}
        try:
            tList = Students.objects.filter(SNo=id)
            if len(tList) == 0:
                teacher = Teachers(SNo=id)
                teacher.Name = request.POST.get('Name')
                teacher.Department = request.POST.get('Department')
                teacher.Email = request.POST.get('Email')
                teacher.Phone = request.POST.get('Phone')
                teacher.save()
            elif len(tList) == 1:
                tList[0].Name = request.POST.get('Name')
                tList[0].Department = request.POST.get('Department')
                tList[0].Email = request.POST.get('Email')
                tList[0].Phone = request.POST.get('Phone')
                tList[0].save()
            else:
                for i in range(len(tList) - 1):
                    tList[i].delete()
                tList[len(tList) - 1] = request.POST.get('Name')
                tList[len(tList) - 1] = request.POST.get('Department')
                tList[len(tList) - 1] = request.POST.get('Email')
                tList[len(tList) - 1] = request.POST.get('Phone')
                tList[len(tList) - 1].save()
                tList['status'] = 'success'
                tList['info'] = 'modify teacher info successfully'
                return JsonResponse(context)
        except Exception as e:
            print(e)
            context['status'] = 'failed'
            context['info'] = 'modify teacher info unsuccessfully'
            return JsonResponse(context)


# 修改学生信息功能,需要传来学生id
def studentInfoModify(request, id):
    if request.method == 'POST':
        context = {}
        try:
            stuList = Students.objects.filter(SNo=id)
            if len(stuList) == 0:
                student = Students(SNo=id)
                student.Name = request.POST.get('Name')
                student.Department = request.POST.get('Department')
                student.Email = request.POST.get('Email')
                student.Phone = request.POST.get('Phone')
                student.save()
            elif len(stuList) == 1:
                stuList[0].Name = request.POST.get('Name')
                stuList[0].Department = request.POST.get('Department')
                stuList[0].Email = request.POST.get('Email')
                stuList[0].Phone = request.POST.get('Phone')
                stuList[0].save()
            else:
                for i in range(len(stuList) - 1):
                    stuList[i].delete()
                stuList[len(stuList) - 1] = request.POST.get('Name')
                stuList[len(stuList) - 1] = request.POST.get('Department')
                stuList[len(stuList) - 1] = request.POST.get('Email')
                stuList[len(stuList) - 1] = request.POST.get('Phone')
                stuList[len(stuList) - 1].save()
                context['status'] = 'success'
                context['info'] = 'modify student info successfully'
                return JsonResponse(context)
        except Exception as e:
            print(e)
            context['status'] = 'failed'
            context['info'] = 'modify student info unsuccessfully'
            return JsonResponse(context)



def savefile(f, filedirpath):
    file_name = ""
    try:
        # 如果课程作业所在的文件夹不存在，生成一个文件夹
        if not os.path.exists(filedirpath):
            os.makedirs(filedirpath)

        file_name = filedirpath + f.name
        destination = open(file_name, 'wb+')
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
    except Exception as e:
        print(e)
        return False
    return True
