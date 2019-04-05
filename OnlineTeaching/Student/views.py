from django.shortcuts import render, render_to_response, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.messages import constants as messages
from django.core.urlresolvers import reverse
from Teacher.models import *
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
import zipfile
import json
import urllib
import shutil
import time


def checkLogin(request):
    if 'uid' not in request.session or request.session['uid']:
        return HttpResponseRedirect("/login/")
    else:
        return HttpResponse("你已经登录啦!")


# 学生首页
def index(request):
    context = {'cid': -1}
    checkLogin(request)
    sno = request.session.get('uid', -1)
    if sno != -1:
        try:
            student = Students.objects.get(SNo=sno)
            context['courseList'] = Courses.objects.filter(xuanke=student)
        except ObjectDoesNotExist:
            return HttpResponseRedirect('/logout')
    return render(request, 'Student/index.html', context)


# 学生登录接口
def login(request):
    if request.method == "GET":
        return HttpResponseRedirect("/login")
    SNo = request.POST.get('id', '')
    password = request.POST.get('pwd', '')
    response = {'result': 0}
    try:
        student = Students.objects.get(SNo=SNo)
        if student.Pwd == password:
            request.session['uid'] = SNo
            request.session['name'] = student.Name
            request.session['role'] = 2
            response['result'] = 1
            response['userid'] = SNo
    except ObjectDoesNotExist:
        response['result'] = 0
    return JsonResponse(response)


# ------------- zycdev -------------

# --------------------------------------------------------------------------------------------------------------------------------------------
# 下面是ljx的代码块，其他人不要乱改

def test(request):
    return HttpResponse(request.session['name'])


# 修改学生信息，只能修改邮箱和手机
def infoModify(request):
    context = {}
    studentInfo = {}
    try:
        userid = request.session.get('uid')
        student = Students.objects.get(SNo=userid)
        studentInfo['SNO'] = student.SNo
        studentInfo['name'] = student.Name
        studentInfo['sex'] = student.Sex
        studentInfo['department'] = student.Department
        studentInfo['email'] = student.Email
        studentInfo['phone'] = student.Phone
        context['userid'] = userid
        context['student'] = studentInfo
    finally:
        return render(request, 'Student/InfoModify.html', context)


# 修改学生信息页面中保存修改信息
def saveModifyInfo(request):
    context = {}
    if request.method == 'POST':
        try:
            email = request.POST.get("Email")
            phone = request.POST.get("Phone")
            userid = request.session.get("uid")
            student = Students.objects.get(SNo=userid)
            student.Email = email
            student.Phone = phone
            student.save()
            context['status'] = 'success'
            context['uid'] = userid
            return JsonResponse(context)

        except Exception as e:
            context['status'] = 'failed'
            context['uid'] = userid
            return JsonResponse(context)


# 上传学生作业接口
# 需要前端传来上传的作业附件
# 使用
def upload_homeworks(request, hmwkId):
    context = {}
    if request.method == 'POST':
        hmwkfile = request.FILES.get('hmwkfile', None)
        if hmwkfile == None or hmwkId == None:
            context['status'] = 'failed'
            context['info'] = 'server get the upload file with some mistakes'
            return JsonResponse(context)
        homeworkObj = Homeworks.objects.get(id=hmwkId)
        homeworkType = homeworkObj.Type  # 表示作业类型为团队作业还是个人作业
        # type为'I'表示个人作业，'T'表示团队作业，默认为个人作业
        courseId = homeworkObj.Course_id

        userId = request.session.get('uid')
        filedirpath = MEDIA_ROOT + 'course' + str(courseId) + '/homework' + str(hmwkId) + '/tmp/';
        filedirUrl = MEDIA_URL + 'course' + str(courseId) + '/homework' + str(hmwkId) + '/tmp/';
        if homeworkType == '团队':
            sttList = STT.objects.filter(Course_id=courseId, SNo_id=userId)
            if len(sttList) == 0:  # 这次作业是团队作业，但是这个人没有加入团队
                context['status'] = 'failed'
                context['info'] = 'the homework is team homework, but the student does not in any team'
                return JsonResponse(context)
            elif len(sttList) > 1:  # 这次作业是团队作业，但这个人属于多个团队
                for i in range(len(sttList) - 1):
                    sttList[i].delete()
                # 为这个人保留一条记录，让它属于列表中最后一个记录中的团队
                context['status'] = 'failed'
                context['info'] = 'the student belongs to many teams,please upload again'
                return JsonResponse(context)
            else:
                if sttList[0].Team_id == None:
                    # 团队作业对应课程，但是这个人没有team
                    context['status'] = 'failed'
                    context['info'] = 'the student does not belong to many team'
                    return JsonResponse(context)
                teamId = sttList[0].Team_id
                filedirpath += 'team' + str(teamId) + '/'
                filedirUrl += 'team' + str(teamId) + '/'
        else:  # 个人作业
            if userId != None:
                sttList = STT.objects.filter(Course_id=courseId, SNo_id=userId)
                if len(sttList) == 0:  # 这次作业是个人作业，选课表中必须有这个人的选课记录
                    context['status'] = 'failed'
                    context['info'] = 'the homework is identical homework, but the student does not choose this course'
                    return JsonResponse(context)
                elif len(sttList) > 1:  # 这次作业是个人作业，但这个人有多次本门课选课记录
                    for i in range(len(sttList) - 1):
                        sttList[i].delete()
                    # 为这个人保留一条选课记录
                    course = Courses.objects.filter(id=courseId)
                    if len(course) != 1:
                        context['status'] = 'failed'
                        context['info'] = 'the course does not exist'
                        return JsonResponse(context)
                    else:  # 数据课程表这门课程唯一
                        courseType = course.type  # type为0表示个人课程，type为1表示团队课程
                        if courseType == 0 and sttList[len(sttList) - 1].Team_id != None:  # 个人课程却存在teamId，记录非法
                            context['status'] = 'failed'
                            context['info'] = 'the homework is identical homework, the student should not have team'
                            sttList[len(sttList) - 1].Team_id = None
                            sttList[len(sttList) - 1].save()
                        if courseType == 1 and sttList[len(sttList) - 1].Team_id == None:  # 团队课程，但这个人却没有加入团队
                            context['status'] = 'failed'
                            context['info'] = 'the student does not belong to any team, upload file error'
                            return JsonResponse(context)
                        filedirpath += str(userId) + '/'
                        filedirUrl += str(userId) + '/'
                        teamId = None

                else:  # 这次是个人作业，选课信息完整
                    filedirpath += str(userId) + '/'
                    filedirUrl += str(userId) + '/'
                    teamId = None

            else:
                context['status'] = 'failed'
                context['info'] = 'the userid is none when server get data from session'
                return JsonResponse(context)
        saveStatus = savefile(hmwkfile, filedirpath)
        # 如果作业在本地文件夹中保存成功，则在数据库中保存该作业的相应信息
        try:
            if saveStatus == True:
                # 上传的时候应该先检查是否已经有人上传了，必须保证一次作业，一个小组的记录在数据库的teamhomework中只有一条记录
                if homeworkType == '团队':  # 那么必然为团队课程
                    tmhmwkList = TeamHomeworks.objects.filter(Team_id=teamId, Homework_id=hmwkId)
                else:
                    tmhmwkList = TeamHomeworks.objects.filter(Student_id=userId, Homework_id=hmwkId)
                # 当数据库中有一条记录时，应当保留最近的一条记录，删除其他所有记录，并且告知用户重新上传
                if len(tmhmwkList) > 1:
                    if homeworkObj.Type == '团队':  # 团队作业，必然为团队课程
                        # 由于之前有团队Id了，这里teamId不可能为None
                        team = Teams.objects.filter(id=teamId)  # teamId为主键，加上stt表中有外键约束，所以team必然返回一个对象
                        if str(team.TeamLeader_id) == userId:  # userId为str类型，teamleaderId为int
                            # 表示整个人就是团队队长
                            for homework in tmhmwkList:
                                homework.delete()
                        else:
                            # 表示不是团队队长，这时删除多余记录，只保留一条
                            for i in range(len(tmhmwkList) - 1):
                                tmhmwkList[i].delete()
                            context['status'] = 'failed'
                            context['info'] = 'the homework has been uploaded'
                            return JsonResponse(context)

                    else:  # 个人作业，得区分课程为团队课程还是个人课程
                        # 个人作业有多条记录，全部删除
                        # 不涉及权限问题
                        for tmhmwk in tmhmwkList:
                            tmhmwk.delete()

                elif len(tmhmwkList) == 1:
                    if homeworkObj.Type == '团队':  # 如果是团队作业
                        # 由于之前有团队Id了，这里teamId不可能为None
                        team = Teams.objects.filter(id=teamId)  # teamId为主键，加上stt表中有外键约束，所以team必然返回一个对象
                        if str(team[0].TeamLeader_id) == userId:  # userId为str类型，teamleaderId为int
                            # 表示整个人就是团队队长
                            for homework in tmhmwkList:
                                homework.delete()
                        else:  # 非队长不能上传作业
                            context['status'] = 'failed'
                            context['info'] = 'the homework has been uploaded'
                            return JsonResponse(context)
                    else:  # 个人作业随意上传覆盖
                        for tmhmwk in tmhmwkList:
                            tmhmwk.delete()

                teamhomework = TeamHomeworks(Homework_id=hmwkId)
                teamhomework.SubmitTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                print(teamhomework.SubmitTime)
                teamhomework.Name = hmwkfile.name
                teamhomework.Student_id = userId
                teamhomework.Team_id = teamId
                teamhomework.save()
                context['status'] = 'success'
                context['info'] = 'student upload homework successfully'
                context['fileName'] = teamhomework.Name
                context['fileUrl'] = filedirUrl + teamhomework.Name
                return JsonResponse(context)
            else:
                context['status'] = 'failed'
                context['info'] = 'student upload homework unsuccessfully'
                return JsonResponse(context)
        except Exception as e:
            print(e)
    else:
        context['status'] = 'failed'
        context['info'] = 'unknown upload error'
        return JsonResponse(context)


# 学生提交作业，需要前端传过来的参数为homeworkId和filename
# 将学生作业移动到学生文件夹中，并返回相应状态
def commit_howorks(request):
    context = {}
    if request.method == "POST":
        hmwkId = request.POST.get('hId')
        filename = request.POST.get('name')
        if hmwkId == None:
            context['status'] = 'failed'
            context['info'] = 'server get the upload file with some mistakes'
            return JsonResponse(context)
        homeworkObj = Homeworks.objects.get(id=hmwkId)
        homeworkType = homeworkObj.Type  # 表示作业类型为团队作业还是个人作业
        # type为'I'表示个人作业，'T'表示团队作业，默认为个人作业
        courseId = homeworkObj.Course_id

        userId = request.session.get('uid')
        try:
            tmpdirpath = MEDIA_ROOT + 'course' + str(courseId) + '/homework' + str(hmwkId) + '/tmp/';
            filedirpath = MEDIA_ROOT + 'course' + str(courseId) + '/homework' + str(hmwkId) + '/';
        except Exception as e:
            print(e)
        if homeworkType == '团队':
            try:
                stt = STT.objects.get(Course_id=courseId, SNo_id=userId)
                teamId = stt.Team_id
                tmhmwkList = TeamHomeworks.objects.filter(Team_id=teamId, Homework_id=hmwkId)
                tmpdirpath += 'team' + str(teamId) + '/'
                filedirpath += 'team' + str(teamId) + '/'
            except Exception as e:
                context['status'] = 'failed'
                context['info'] = 'the student has more than one team in the course'
                return JsonResponse(context)

            if len(tmhmwkList) > 1:
                # 由于之前有团队Id了，这里teamId不可能为None
                team = Teams.objects.filter(id=teamId)  # teamId为主键，加上stt表中有外键约束，所以team必然返回一个对象
                if str(team.TeamLeader_id) == userId:  # userId为str类型，teamleaderId为int
                    # 表示整个人就是团队队长
                    pass
                else:
                    # 表示不是团队队长，这时删除多余记录，只保留一条
                    for i in range(len(tmhmwkList) - 1):
                        tmhmwkList[i].delete()
                    context['status'] = 'failed'
                    context['info'] = 'the homework has been uploaded'
                    return JsonResponse(context)

            elif len(tmhmwkList) == 1:
                # 由于之前有团队Id了，这里teamId不可能为None
                try:
                    team = Teams.objects.filter(id=teamId)  # teamId为主键，加上stt表中有外键约束，所以team必然返回一个对象
                    if (len(team) == 1):
                        if str(team[0].TeamLeader_id) == userId:  # userId为str类型，teamleaderId为int
                            # 表示整个人就是团队队长
                            pass
                        else:  # 非队长不能上传作业
                            if tmhmwkList[0].Path == None or tmhmwkList[0].Path == '':  # 如果Path为空说明是它自己上传了，但是没有提交
                                pass
                            else:
                                context['status'] = 'failed'
                                context['info'] = 'the homework has been uploaded'
                                return JsonResponse(context)
                except Exception as e:
                    print(e)
        else:
            if userId != None:
                tmpdirpath += str(userId) + '/'
                filedirpath += str(userId) + '/'
            else:
                context['status'] = 'failed'
                context['info'] = 'the userid is none when server get data from session'
                return JsonResponse(context)

        tmpfilepath = tmpdirpath + filename
        filepath = filedirpath + filename

        if os.path.exists(tmpfilepath) or os.path.exists(tmpfilepath.replace('/', '\\')):
            try:
                if not os.path.exists(filedirpath):
                    os.makedirs(filedirpath)
                shutil.move(tmpfilepath, filepath)
                shutil.rmtree(tmpdirpath)  # 删除tmp文件夹下面的团队或个人缓存文件夹
                teamhomework = TeamHomeworks.objects.get(Student_id=userId, Homework_id=hmwkId)  # 如果数据库中有多条记录，这里会会出现异常
                pos = filepath.find('/media')
                pos1 = filepath.rfind('/' + filename)
                teamhomework.Path = filepath[pos:pos1 + 1]
                teamhomework.save()
            except Exception as e:
                context['status'] = 'failed'
                context['info'] = 'it occurs an error when commit homework'
                return JsonResponse(context)
            context['status'] = 'success'
            context['info'] = 'the homework commit successfully'
            return JsonResponse(context)
        else:
            context['status'] = 'failed'
            context['info'] = 'the homework commit unsuccessfully'
            return JsonResponse(context)


def delete_homework(request, cid):
    context = {}
    if request.method == "POST":
        fileUrl = request.POST.get('fileUrl')
        pos = fileUrl.rfind('/')  # 找到文件名前面的/
        fileDir = fileUrl[:pos + 1]  # 学生上传作业所在的文件夹的相对路径
        fileName = fileUrl[pos + 1:]  # 学生上传作业的名称
        pos1 = fileDir.find('/homework')  # 找到字符串中/homework的斜杠位置
        fileDirr = fileDir[pos1 + 9:]
        pos2 = fileDirr.find('/')  # 找到/stuId或/teamid的斜杠位置
        try:
            hmwkId = int(fileDirr[:pos2])  # 将课程Id取出来
            userId = request.session.get('uid')
        except Exception as e:
            print(e)
        if userId == None:
            print('暂时不处理')
        else:
            strr = fileDirr[pos2 + 1:-1]
            print(strr)
            pos3 = strr.rfind('/')  # 反向找到/teamId或/stuId的斜杠位置
            try:
                if strr[pos3 + 1] == 't':
                    teamId = int(strr[pos3 + 5:])  # 将团队Id取出来
                else:
                    teamId = None
            except Exception as e:
                print(e)

            if teamId != None:
                tmhmwkList = TeamHomeworks.objects.filter(Team_id=teamId, Homework_id=hmwkId)
                try:
                    homework = Homeworks.objects.get(id=hmwkId)
                    if homework.Type == '团队':  # 团队作业
                        team = Teams.objects.filter(id=teamId)  # teamId为主键，加上stt表中有外键约束，所以team必然返回一个对象
                        if str(team[0].TeamLeader_id) == userId:  # userId为str类型，teamleaderId为int
                            # 表示整个人就是团队队长
                            for homework in tmhmwkList:
                                homework.delete()
                        else:
                            # 表示不是团队队长，这时删除多余记录，只保留一条
                            for i in range(len(tmhmwkList) - 1):
                                tmhmwkList[i].delete()
                            context['status'] = 'failed'
                            context['info'] = '请联系团队队长删除此文件'
                            return JsonResponse(context)
                    else:  # 个人作业
                        pass  # 个人作业相当于可以随意删除
                except Exception as e:
                    print(e)
            else:  # 表示个人作业
                pass  # 个人作业，不论是团队课程还是个人课程，都不涉及权限问题

            path = BASE_DIR + fileUrl
            print(path)
            if os.path.exists(path) or os.path.exists(path.replace('/', '\\')):
                try:
                    if os.path.isfile(path):
                        teachhomework = TeamHomeworks.objects.get(Path=fileDir, Name=fileName)
                        os.remove(path)
                        shutil.rmtree(BASE_DIR + fileDir)
                    else:
                        shutil.rmtree(path)  # 删除提交的作业
                        context['status'] = 'failed'
                        context['info'] = 'the homework file not found'
                        return JsonResponse(context)

                except Exception as e:  # 如果这个记录在数据库中已经被删了，那么这里会出现异常
                    # 另一种异常的情况是在上传完作业以后，未提交作业的情况下，点击删除也会因为path不存在而异常
                    # 因为当前用户为提交者，一个团队在一次作业下数据库中应该有一条记录才对，否则是错误的
                    list = TeamHomeworks.objects.filter(Student_id=userId, Name=fileName)
                    if len(list) == 1:
                        teachhomework = list[0]
                        teachhomework.delete()
                        teachhomework = None
                        print(path)
                        os.remove(path)
                        print(BASE_DIR + fileDir)
                        shutil.rmtree(BASE_DIR + fileDir)
                        print(e)
                    elif len(list) > 1:
                        # 如果数据库中有多条非法记录，就把它们删掉
                        for homework in list:
                            homework.delete()
                        teachhomework = None
                        context['status'] = 'failed'
                        context['info'] = 'there are many same homewrokfile records in database'
                        return JsonResponse(context)

                if teachhomework != None:
                    teachhomework.delete()
                context['status'] = 'success'
                context['info'] = 'the homework delete successfully'
                return JsonResponse(context)
            else:
                context['status'] = 'failed'
                context['info'] = 'the upload homework not exisit in server path'
                return JsonResponse(context)

        context['status'] = 'failed'
        context['info'] = 'unknown error'
        return JsonResponse(context)


# 保存文件到本地路径
# 需要传递courseId和homeworkId两个参数
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


# 多文件压缩，参数为需要下载的文件的url列表
# 返回压缩好的zip的url，便于前端下载
def download_manyfiles(request):
    if request.method == 'POST':
        coursefileList = request.POST.get('Links', '')
        coursefileList = json.loads(coursefileList)
        print(coursefileList)
        zipurl = zip_manyfiles(coursefileList)
        return JsonResponse({'ziplink': zipurl})


# 通用的多文件下载接口，参数filelist为path路径的list，每一个path可能为文件夹路径，也可能为文件路径
# 返回压缩好的zip的path
def zip_manyfiles(pathlist):
    if len(pathlist) >= 1:
        firstpath = pathlist[0]
        pos = firstpath.find('/course')  # 找到字符串中/course的这个斜杠的下标
        pos1 = firstpath.find('/', pos + 6, -1)  # 找到/coursexxx/后面的courseId后面的这个斜杠的下标
        coursedirpath = firstpath[pos:pos1 + 1]
        courseIdStr = firstpath[pos + 7:pos1]  # 获取couseId的字符串
        tmpdirpath = coursedirpath + 'resources/tmp/'

    filelist = []
    allstr = ""
    print(MEDIA_ROOT)
    tmppath = MEDIA_ROOT + (tmpdirpath.replace('/', '\\'))
    if not os.path.exists(tmppath):
        os.makedirs(tmppath)
    for filepath in pathlist:
        print(filepath)
        decodepath = urllib.parse.unquote(
            filepath)  # url解析前台传过来的unicode编码的url   从media下的course开始，例如：/course1/resources/xxx.docx
        pos = decodepath.find('/course')  # 找到字符串中/course的这个斜杠的下标
        allstr += filepath

        path = MEDIA_ROOT + (decodepath[pos:].replace('/', '\\'))
        print(path)
        if os.path.isfile(path):
            filelist.append(path)
        else:
            for root, dirs, files in os.walk(path):
                for name in files:
                    filelist.append(os.path.join(path, name))

    zipfilename = str(hash(allstr)) + '.zip'  # 表示zip压缩包的文件名
    zipfilepath = tmppath + zipfilename  # 表示zip的url路径，该路径前面加上MEDIA_ROOT就是本地路径
    # print(zipfilename)
    # print(tmpdirpath)
    try:
        zf = zipfile.ZipFile(zipfilepath, "w", zipfile.zlib.DEFLATED)
    except Exception as e:
        print(e)
    print(filelist)
    try:
        for file in filelist:
            # print arcname
            pos = file.rfind('\\')  # 从文件路径字符串末尾反向查找\的位置
            zf.write(file, file[pos + 1:])
        zf.close()
    except Exception as e:
        print(e)
    zipurl = MEDIA_URL + tmpdirpath + zipfilename
    return zipurl


def download_resources(request):
    return render(request, 'Student/ResDownload.html')


# 学生下载课程资源页面,显示所有的课程
def show_courses(request):
    context = {}
    try:
        userid = request.session.get('uid')
        student = Students.objects.get(SNo=userid)
        courselist = []
        courseslist = Courses.objects.filter(xuanke=student)

        response_courselist = []
        for course in courseslist:
            courseInfo = {}
            courseInfo['id'] = course.id
            courseInfo['name'] = course.Name
            courseInfo['department'] = course.Department
            courseInfo['semester'] = course.Semester
            courseInfo['weeks'] = course.Weeks
            courseInfo['credit'] = course.credit
            response_courselist.append(courseInfo)
        context['userid'] = userid
        context['courseList'] = response_courselist
    finally:
        return render(request, 'Student/CourseResDownload.html', context)


def show_teachingfile(request):
    if request.method == "POST":
        cid = request.POST.get("cid")
        context = {'cid': cid}
        try:
            course = Courses.objects.get(id=cid)
            coursefileList = CourseFile.objects.filter(course_id=cid)
            response_coursefilelist = []
            for coursefile in coursefileList:
                coursefileInfo = {}
                coursefileInfo['id'] = coursefile.id
                coursefileInfo['filename'] = coursefile.filename
                coursefileInfo['uploadername'] = coursefile.uploader.Name
                coursefileInfo['updatetime'] = coursefile.updateTime
                # coursefileInfo['path'] = coursefile.path
                coursefileInfo['path'] = coursefile.course.resourcesPath + coursefile.filename
                response_coursefilelist.append(coursefileInfo)
            # context['userid'] = request.session.get('userid','')
            context['resList'] = response_coursefilelist
        except Exception as e:
            print(e)
        finally:
            return JsonResponse(context)


# 显示该课程对应的所有课程资源
def view_resources(request, cid):
    context = {}
    context['cid'] = cid
    try:
        course = Courses.objects.get(id=cid)
        coursefileList = CourseFile.objects.filter(course_id=cid)
        response_coursefilelist = []
        for coursefile in coursefileList:
            coursefileInfo = {}
            coursefileInfo['id'] = coursefile.id
            coursefileInfo['filename'] = coursefile.filename
            coursefileInfo['uploadername'] = coursefile.uploader.Name
            coursefileInfo['updatetime'] = coursefile.updateTime
            # coursefileInfo['path'] = coursefile.path
            coursefileInfo['path'] = coursefile.course.resourcesPath + coursefile.filename
            response_coursefilelist.append(coursefileInfo)
        # context['userid'] = request.session.get('userid','')
        context['resList'] = response_coursefilelist
        context['type'] = course.type
    except Exception as e:
        print(e)
    finally:
        return render(request, 'Student/CourseResDownload.html', context)


# 学生点进某门课程以后显示本门课程的在线交流页面
def course_communicate(request, cid):
    context = {}
    try:
        context['userId'] = request.session.get('uid')
        course = Courses.objects.get(id=cid)
        context['courseId'] = cid
        context['cid'] = cid
        context['courseName'] = course.Name

        sttList = STT.objects.filter(Course_id=cid)
        studentList = []
        for sttItem in sttList:
            stuObj = {}
            stuId = sttItem.SNo_id
            student = Students.objects.get(SNo=stuId)
            stuName = student.Name
            stuToken = student.Token
            stuObj['userId'] = str(stuId)
            stuObj['userName'] = stuName
            stuObj['userToken'] = stuToken
            if context['userId'] == str(stuId):
                context['userName'] = stuName
                context['userToken'] = stuToken
            studentList.append(stuObj)
        context['studentList'] = studentList
        teacher_list = []
        teachcourse_list = course.teachcourse_set.all()
        for tc in teachcourse_list:
            teaObj = {}
            teacher = tc.TNo
            teaObj['userId'] = teacher.TNo
            teaObj['userName'] = teacher.Name
            teaObj['userToken'] = teacher.Token
            teacher_list.append(teaObj)
        context['teacherList'] = teacher_list
        context['type'] = course.type
    finally:
        return render(request, 'Student/Communicate.html', context)


# 学生点击查看课程资源时调用该函数，只需post courseId
def download_coursefile(request):
    if request.method == 'POST':
        courseId = request.POST('courseId')

        # 里面调用下载文件的函数，然后返回response
    response = []
    return response


# 抄的网上的下载文件，这个得改一些
def download_file():
    def readFile(fn, buf_size=262144):
        f = open(fn, "rb")
        while True:
            c = f.read(buf_size)
            if c:
                yield c
            else:
                break
        f.close()

    file_name = 'big file data'
    response = HttpResponse(readFile(file_name))

    return response


# --------------------------------------------------------------------------------------------------------------------------------------------


# TODO #############黄丹####################

# 查看studentHome,,,学生登录后将学号存储在session中
def view_homeworks(request):
    checkLogin(request)
    id = request.session['uid']
    Student = Students.objects.get(SNo=id)
    courses = Courses.objects.filter(xuanke=Student)
    allHomeworks = []
    i = -1
    for course in courses:
        homeworks = course.homeworks_set.all()
        if homeworks.count() > 0:
            for homework in homeworks:
                i = i + 1
                if (homework.StartTime > datetime.datetime.now(timezone.utc)):
                    homework.type = 1  # 还未开始
                elif (homework.EndTime > datetime.datetime.now(timezone.utc)):
                    if (homework.Type == 'I' or homework.Type == '个人'):  # 个人作业
                        teamHomeworks = TeamHomeworks.objects.filter(Homework=homework, Student=Student)
                        if len(teamHomeworks) == 0:  # 个人作业未提交
                            homework.type = 3
                        else:
                            if teamHomeworks.get().Path == None or teamHomeworks.get().Path == '':  # 个人作业提交过但删除了
                                homework.type = 3
                            homework.type = 2  # 个人作业已提交
                    else:
                        team = Student.stt_set.filter(Course=homework.Course).get()
                        if (team != None):  # 判断是否在团队中
                            team_id = team.Team_id
                            teamHomeworks = TeamHomeworks.objects.filter(Homework=homework, Team_id=team_id)
                            if len(teamHomeworks) == 0:  # 团队作业未提交
                                homework.type = 3
                            else:
                                if teamHomeworks.get().Path == None or teamHomeworks.get().Path == '':  # 团队作业提交过但删除了
                                    homework.type = 3
                                homework.type = 2
                        else:
                            homework.type = 3
                    homework.Status = 1  # 还未到截止时间
                else:
                    if (homework.Type == 'I' or homework.Type == '个人'):  # 个人作业
                        teamHomeworks = TeamHomeworks.objects.filter(Homework=homework, Student=Student)
                        if len(teamHomeworks) == 0:  # 个人作业未提交
                            homework.type = 4
                        else:
                            if teamHomeworks.get().Path == None or teamHomeworks.get().Path == '':  # 个人作业提交过但删除了
                                homework.type = 4
                            homework.type = 5  # 个人作业已提交
                    else:
                        team = Student.stt_set.filter(Course=homework.Course).get()
                        if (team != None):  # 判断是否在团队中
                            team_id = team.Team_id
                            teamHomeworks = TeamHomeworks.objects.filter(Homework=homework, Team_id=team_id)
                            if len(teamHomeworks) == 0:  # 团队作业未提交
                                homework.type = 4
                            else:
                                if teamHomeworks.get().Path == None or teamHomeworks.get().Path == '':  # 团队作业提交过但删除了
                                    homework.type = 4
                                homework.type = 5
                        else:
                            homework.type = 3
                    homework.Status = 2  # 已到截止时间
                homework.courseName = course.Name
                allHomeworks.append(homework)
    context = {}
    context['allHomeworks'] = allHomeworks

    return render(request, 'Student/HomeWorkList.html', context)


# 学生页面查看某个作业详情,用url传递homework_id
def view_homework(request, id, type):
    userid = request.session.get('uid')
    if userid is None:
        print('暂时无处理')
    else:
        context = {}
        homework = Homeworks.objects.get(id=id)
        path = homework.AttachmentUrl
        context['have_attachment'] = False
        if (path != None):
            pos = path.rfind('/')  # bug是因为数据库中没有attachment的文件名，所以字符串查找必须保证教师上传的作业附件文件名中不能有/符号
            context['assignment'] = {'AttachmentUrl': path, 'name': path[pos + 1:]}
            context['have_attachment'] = True
        Student = Students.objects.get(SNo=userid)
        courseid = homework.Course_id
        context['cid'] = courseid

        context['type'] = homework.Course.type
        stt = STT.objects.get(Course_id=courseid, SNo_id=userid)
        teamid = stt.Team_id
        # 判断学生是否提交作业的状态
        homework.type = None
        context['commitPath'] = None
        context['commitName'] = None
        if (homework.StartTime > datetime.datetime.now(timezone.utc)):
            homework.type = 1  # 作业还未开始
            homework.Status = 0
        elif (homework.EndTime > datetime.datetime.now(timezone.utc)):  # 作业可以提交
            if (homework.Type == 'I' or homework.Type == '个人'):  # 个人作业
                teamHomeworks = TeamHomeworks.objects.filter(Homework=homework, Student=Student)
                if len(teamHomeworks) == 0:  # 个人作业未提交
                    homework.type = 3
                else:
                    if teamHomeworks[0].Path == None or teamHomeworks[0].Path == '':  # 个人作业提交过但删除了
                        homework.type = 3
                    context['commitPath'] = teamHomeworks[0].Path + teamHomeworks[0].Name
                    context['commitName'] = teamHomeworks[0].Name
                    homework.type = 2  # 个人作业已提交
            else:
                team = Student.stt_set.filter(Course=homework.Course).get()
                if (team != None):  # 判断是否在团队中
                    team_id = team.Team_id
                    teamHomeworks = TeamHomeworks.objects.filter(Homework=homework, Team_id=team_id)
                    if len(teamHomeworks) == 0:  # 团队作业未提交
                        homework.type = 3
                    else:
                        if teamHomeworks.get().Path == None or teamHomeworks.get().Path == '':  # 团队作业提交过但删除了
                            homework.type = 3
                        context['commitPath'] = teamHomeworks[0].Path + teamHomeworks[0].Name
                        context['commitName'] = teamHomeworks[0].Name
                        homework.type = 2
                else:
                    homework.type = 3
            homework.Status = 1  # 还未到截止时间
        else:
            if (homework.Type == 'I' or homework.Type == '个人'):  # 个人作业
                teamHomeworks = TeamHomeworks.objects.filter(Homework=homework, Student=Student)
                if len(teamHomeworks) == 0:  # 个人作业未提交
                    homework.type = 4
                else:
                    if teamHomeworks.get().Path == None or teamHomeworks.get().Path == '':  # 个人作业提交过但删除了
                        homework.type = 4
                    context['score'] = teamHomeworks[0].Score
                    context['comment'] = teamHomeworks[0].Comment
                    context['commitPath'] = teamHomeworks[0].Path + teamHomeworks[0].Name
                    context['commitName'] = teamHomeworks[0].Name
                    homework.type = 5  # 个人作业已提交
            else:
                team = Student.stt_set.filter(Course=homework.Course).get()
                if (team != None):  # 判断是否在团队中
                    team_id = team.Team_id
                    teamHomeworks = TeamHomeworks.objects.filter(Homework=homework, Team_id=team_id)
                    if len(teamHomeworks) == 0:  # 团队作业未提交
                        homework.type = 4
                    else:
                        if teamHomeworks.get().Path == None or teamHomeworks.get().Path == '':  # 团队作业提交过但删除了
                            homework.type = 4
                        context['commitPath'] = teamHomeworks[0].Path + teamHomeworks[0].Name
                        context['commitName'] = teamHomeworks[0].Name
                        homework.type = 5
                else:
                    homework.type = 4
            homework.Status = 2  # 已到截止时间
        if type == '0':
            context['homework'] = homework
            return render(request, 'Student/HomeworkDetail.html', context)
        else:
            context['homework'] = homework
            return render(request, 'Student/CourseHomeworkDetail.html', context)


# 查看某门课程所有作业
def view_course_homeworks(request, cid):
    checkLogin(request)
    id = request.session['uid']
    Student = Students.objects.get(SNo=id)
    course = Courses.objects.get(id=cid)
    allHomeworks = []
    i = -1
    homeworks = course.homeworks_set.all()
    if homeworks.count() > 0:
        for homework in homeworks:
            i = i + 1
            if homework.StartTime != None and homework.StartTime > datetime.datetime.now(timezone.utc):
                homework.type = 0  # 还未开始
            elif homework.EndTime != None and homework.EndTime > datetime.datetime.now(timezone.utc):
                if (homework.Type == 'I' or homework.Type == '个人'):  # 个人作业
                    teamHomeworks = TeamHomeworks.objects.filter(Homework=homework, Student=Student)
                    if len(teamHomeworks) == 0:  # 个人作业未提交
                        homework.type = 3
                    else:
                        if teamHomeworks.get().Path == None or teamHomeworks.get().Path == '':  # 个人作业提交过但删除了
                            homework.type = 3
                        homework.type = 2  # 个人作业已提交
                else:
                    team = Student.stt_set.filter(Course=homework.Course).get()
                    if (team != None):  # 判断是否在团队中
                        team_id = team.Team_id
                        teamHomeworks = TeamHomeworks.objects.filter(Homework=homework, Team_id=team_id)
                        if len(teamHomeworks) == 0:  # 团队作业未提交
                            homework.type = 3
                        else:
                            if teamHomeworks.get().Path == None or teamHomeworks.get().Path == '':  # 团队作业提交过但删除了
                                homework.type = 3
                            homework.type = 2
                    else:
                        homework.type = 3
                homework.Status = 1  # 还未到截止时间
            else:
                if (homework.Type == 'I' or homework.Type == '个人'):  # 个人作业
                    teamHomeworks = TeamHomeworks.objects.filter(Homework=homework, Student=Student)
                    if len(teamHomeworks) == 0:  # 个人作业未提交
                        homework.type = 4
                    else:
                        if teamHomeworks.get().Path == None or teamHomeworks.get().Path == '':  # 个人作业提交过但删除了
                            homework.type = 4
                        homework.type = 5  # 个人作业已提交
                else:
                    team = Student.stt_set.filter(Course=homework.Course).get()
                    if (team != None):  # 判断是否在团队中
                        team_id = team.Team_id
                        teamHomeworks = TeamHomeworks.objects.filter(Homework=homework, Team_id=team_id)
                        if len(teamHomeworks) == 0:  # 团队作业未提交
                            homework.type = 4
                        else:
                            if teamHomeworks.get().Path == None or teamHomeworks.get().Path == '':  # 团队作业提交过但删除了
                                homework.type = 4
                            homework.type = 5
                    else:
                        homework.type = 3
                homework.Status = 2  # 已到截止时间
            homework.courseName = course.Name
            allHomeworks.append(homework)

    context = {}
    context['cid'] = cid
    context['type'] = course.type
    context['allHomeworks'] = allHomeworks

    return render(request, 'Student/CourseHomeworkList.html', context)


# 查看某一课程所有的团队+判断是否为TeamLeader
# TODO 团队状态设置 根据团队状态禁用button
def view_teams(request, course_id):
    checkLogin(request)
    id = request.session['uid']
    course = Courses.objects.get(id=course_id)
    context = {'cid': course_id}
    context['type'] = course.type
    # if 'applyMessage' in request.session and request.session['applyMessage']:
    #     context['applyMessage'] = request.session['applyMessage']
    #     request.session['applyMessage'] = None
    if (course.type == 1):
        student = Students.objects.get(SNo=id)
        in_team = student.stt_set.filter(Course=course).get()
        is_in_team = False
        is_team_leader = False
        if in_team.Team_id is not None:
            is_in_team = True
            my_team = Teams.objects.get(id=in_team.Team_id)
            applicants = my_team.applicant_set.all()
            chengyuans = my_team.stt_set.all()
            members = []
            for chengyuan in chengyuans:
                members.append(chengyuan.SNo)
            context['members'] = members
            context['my_team'] = my_team
            context['applicants'] = applicants  # 传入申请者的信息
            if int(id) == int(my_team.TeamLeader_id):
                is_team_leader = True
        teams = course.teams_set.all()
        is_apply_team = False
        teams.length = len(teams)
        for team in teams:
            team.disable = False
            team.TeamLeaderName = team.TeamLeader.Name
            # TODO 检查是否每个团队没有审批通过该同学,如果都没有审批通过,就可以创建团队
            allTeamDecline = True
            for applicant in team.applicant_set.all():
                if int(id) == int(applicant.Student_id):
                    is_apply_team = True
                    if applicant.Status != 2:
                        allTeamDecline = False
            if (team.Status != 0):
                team.disable = True
            if (allTeamDecline):
                is_apply_team = False
        context['can_create_team'] = True
        if (is_in_team or is_apply_team):
            context['can_create_team'] = False  # 是否属于某个团队,如果不属于,可以创建一个新的团队
        context['is_in_team'] = is_in_team  # 是否属于某个团队,如果不属于,可以创建一个新的团队
        context['is_team_leader'] = is_team_leader  # 是否是某个团队的TeamLeader
        context['teams'] = teams  # 该课程的所有团队
        # return HttpResponse(teams)
        return render(request, 'Student/TeamManage.html', context)
    else:
        return HttpResponse("该门课不是团队课程")  # 查看个人所有课程


# 查看课程首页
def courseIndex(request, cid):
    context = {'cid': cid}
    course = Courses.objects.get(id=cid)
    context['type'] = course.type
    return render(request, 'Student/CourseIndex.html', context)


# 申请团队
@csrf_exempt
def apply_team(request, cid):
    if request.method == 'POST':
        response = {'message': ''}
        team_id = request.POST['team_id']
        response['team_id'] = team_id
        sid = request.session['uid']
        course = Courses.objects.get(id=cid)
        student = Students.objects.get(SNo=sid)
        team = Teams.objects.get(id=team_id)
        in_team = student.stt_set.filter(Course=course).get()
        response = {'message': ''}
        if in_team.Team_id is not None:
            my_team = Teams.objects.get(id=in_team.Team_id)
            response['message'] = '你已经加入' + my_team.Name + '团队了'
            return JsonResponse(response)
        myApply = student.applicant_set.filter(Team=team)
        for apply in myApply:
            if apply.Status == 0:
                response['message'] = '你已经申请过该团队了,团队还未审核,请等待审批'
                return JsonResponse(response)
        applicant = Applicant(Student=student, Team=team, Status=0)
        try:
            applicant.save()
            response['message'] = '申请成功'
            return JsonResponse(response)
        except Exception as e:
            response['message'] = '服务器发生错误,申请失败'
            return JsonResponse(response)
    return HttpResponseRedirect(reverse('view_teams', args=(cid)))


# 批准加入团队
@csrf_exempt
def check_team(request, cid):
    response = {}
    if (request.method == 'POST'):
        # response = {'message', ''}
        # response['message'] = '非法操作'
        # return JsonResponse(response)
        # return HttpResponse('Hello!!!!!!')
        status = int(request.POST.get('status', ''))
        applicant_id = int(request.POST.get('applicant_id', -1))
        course = Courses.objects.get(id=cid)
        if applicant_id == -1:
            response['message'] = '非法操作'
            return JsonResponse(response)
        applicant = Applicant.objects.get(id=applicant_id)
        if status == 1:
            try:
                team = applicant.Team
                applicant.Status = 1
                if (team.StudentCount >= team.Course.teamMaximum):
                    team.StudentCount = team.StudentCount + 1
                    team.save()
                    student = applicant.Student
                    stt = student.stt_set.filter(Course=course).get()
                    stt.Team = team
                    applicant.save()
                    stt.save()
                    response['message'] = '已添加入团队'
                    response['type'] = 1
                else:
                    response['message'] = '团队人数已达上限,不能添加新队员'
                    response['type'] = 4
            except Exception as e:
                response['message'] = '服务器发生错误'
                response['type'] = 3
            finally:
                return JsonResponse(response)
        else:
            try:
                applicant.Status = 2
                applicant.save()
                response['message'] = '已拒绝加入团队'
                response['type'] = 2
            except Exception as e:
                response['type'] = 3
                response['message'] = '服务器发生错误'
            finally:
                return JsonResponse(response)
    else:
        return HttpResponseRedirect(reverse('view_teams', args=(cid)))

def submit_team(request,cid):
    if request.method =='POST':
        response = {}
        team_id = request.POST.get('team_id','')
        team = Teams.objects.get(id = int(team_id))
        if team.StudentCount < team.Course.teamMinimum:
            response['status'] = 1
            response['message'] = "团队人数太少,不能申请"
        else:
            try:
                team.Status = 1
                team.save()
                response['status'] = 0
                response['message'] = "申请成功"
            except Exception:
                response['status'] = 2
                response['message'] = "服务器发生错误,请重新提交"
        return JsonResponse(response)
    return HttpResponseRedirect(reverse('view_teams', args=(cid)))

def submit_team(request, cid):
    if request.method == 'POST':
        response = {}
        team_id = request.POST.get('team_id', '')
        team = Teams.objects.get(id=int(team_id))
        if team.StudentCount < team.Course.teamMinimum:
            response['status'] = 1
            response['message'] = "团队人数太少,不能申请"
        else:
            try:
                team.Status = 1
                team.save()
                response['status'] = 0
                response['message'] = "申请成功"
            except Exception:
                response['status'] = 2
                response['message'] = "服务器发生错误,请重新提交"
        return JsonResponse(response)
    return HttpResponseRedirect(reverse('view_teams', args=(cid)))


def view_course(request, cid):
    context = {'cid': cid}
    course = Courses.objects.get(id=cid)
    context['type'] = course.type
    context['course'] = course
    return render(request, 'Student/ViewCourseInfo.html', context)


# TODO #############黄丹####################



# --------------------------------------------------------------------------------------------------------------------------------------------


# LuxakyLuee
# 创建团队接口
@csrf_exempt
def create_team(request, cid):
    checkLogin(request)
    id = request.session['uid']
    course = Courses.objects.get(id=cid)
    student = Students.objects.get(SNo=id)
    if request.method == 'POST':
        response = {}
        if course.type == 0:
            response['result'] = 0
        # 如果该课程不是团队课程返回0
        else:
            cid = int(cid)
            sid = request.session['uid']
            sid = int(sid)
            # sid为学生id
            name = request.POST.get('teamName', '')
            introduction = request.POST.get('teamIntroduction', '')
            response['result'] = 1
            # return JsonResponse(introduction)
            status = 0
            team = Teams(Course=course, TeamLeader=student, Name=name
                         , Introduction=introduction, Status=status)
            team.save()
            stt = student.stt_set.filter(Course=course).get()
            stt.Team_id = team.id
            stt.save()
        return JsonResponse(response)
    else:
        return HttpResponseRedirect('../view')

        # LuxakyLuee
