from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from datetime import datetime, timedelta
from .forms import HomeworkForm
from Teacher.models import *
from OnlineTeaching.settings import *
import shutil
import json
import zipfile
import urllib


# 教师首页
def index(request):
    context = {'cid': -1}
    TNo = request.session.get('uid', -1)
    if TNo != -1:
        try:
            teacher = Teachers.objects.get(TNo=TNo)
            context['courseList'] = Courses.objects.filter(jiaoke=teacher)
        except ObjectDoesNotExist:
            return HttpResponseRedirect('/logout')
    return render(request, 'Teacher/index.html', context)


# 教师登录接口
def login(request):
    if request.method == "GET":
        return HttpResponseRedirect("/login")
    tno = request.POST.get('id', '')
    password = request.POST.get('pwd', '')
    response = {'result': 0}
    try:
        teacher = Teachers.objects.get(TNo=tno)
        if teacher.Pwd == password:
            request.session['uid'] = tno
            request.session['name'] = teacher.Name
            request.session['role'] = 1
            response['result'] = 1
    except ObjectDoesNotExist:
        response['result'] = 0
    return JsonResponse(response)


def self_info(request):
    context = {'cid': -1}
    return render(request, 'Teacher/SelfInfo.html', context)


# 教师课程空间首页
def course(request, cid):
    context = {'cid': cid}
    return render(request, 'Teacher/index.html', context)


# 作业管理页面
def assignments(request, cid):
    try:
        course = Courses.objects.get(id=cid)
        assignments = course.homeworks_set.all()
    except ObjectDoesNotExist:
        return HttpResponseRedirect('/teacher/')
    context = {'cid': cid, 'assignments': assignments}
    return render(request, 'Teacher/Assignments.html', context)


# (修改）作业详情页面
def assignment(request, cid, aid):
    cid = int(cid)
    aid = int(aid)
    errors = []
    try:
        course = Courses.objects.get(id=cid)
        assignment = Homeworks.objects.get(id=aid)
        if int(assignment.Course_id) != cid:
            return HttpResponseRedirect('../../assignments')
    except ObjectDoesNotExist:
        return HttpResponseRedirect('/teacher/')
    context = {'is_publish': False,
               'course_type': course.type,
               'cid': cid,
               'aid': aid,
               'assignment': assignment,
               'errors': errors}
    return render(request, 'Teacher/AssignmentDetail.html', context)


# 新建作业页面
def new_assignment(request, cid):
    cid = int(cid)
    errors = []
    try:
        course = Courses.objects.get(id=cid)
    except ObjectDoesNotExist:
        return HttpResponseRedirect('/teacher/')
    context = {'is_publish': True,
               'course_type': course.type,
               'cid': cid,
               'errors': errors}
    return render(request, 'Teacher/AssignmentDetail.html', context)


# 发布作业接口
def create_assignment(request, cid):
    if request.method == 'GET':
        return HttpResponseRedirect('new/')
    response = {'result': 0}
    # TODO 检查课程是否属于教师
    cid = int(cid)
    response = {'result': 1}
    title = request.POST.get('title', '')
    if title == '':
        response['error'] = 'title required'
    else:
        assignment_type = request.POST.get('type', '个人')
        full_mark = request.POST.get('fullMark', -1)
        description = request.POST.get('description', '')
        start_time = request.POST.get('startTime', None)
        end_time = request.POST.get('endTime', None)
        file_name = request.POST.get('fileName', '')
        response['file_name'] = file_name
        assignment = Homeworks.objects.create(Course_id=cid, Heading=title, Type=assignment_type,
                                              Description=description)
        if file_name != '':
            tmp_path = 'course' + str(cid) + '/tmp/' + request.session.get('uid', '') + '/'
            final_path = 'course' + str(cid) + '/homework' + str(assignment.id) + '/assignment/'
            shutil.move(MEDIA_ROOT + tmp_path, MEDIA_ROOT + final_path)
            assignment.AttachmentUrl = '/media/' + final_path + file_name
        if not (start_time is None or start_time == ''):
            assignment.StartTime = start_time
        if not (end_time is None or end_time == ''):
            assignment.EndTime = end_time
        if full_mark != -1 and full_mark != '':
            assignment.FullMark = full_mark
        assignment.save()
    return JsonResponse(response)


# 修改作业接口
def update_assignment(request, cid, aid):
    if request.method == 'GET':
        return HttpResponseRedirect(".")
    response = {'result': 1}
    # TODO 检查课程是否属于教师
    cid = int(cid)
    aid = int(aid)
    try:
        assignment = Homeworks.objects.get(id=aid)
        if int(assignment.Course_id) != cid:
            response['result'] = 0
            response['error'] = 'permission denied'
        else:
            title = request.POST.get('title', '')
            if title == '':
                response['error'] = 'title required'
            else:
                assignment_type = request.POST.get('type', '')
                full_mark = request.POST.get('fullMark', -1)
                description = request.POST.get('description', '')
                start_time = request.POST.get('startTime', None)
                end_time = request.POST.get('endTime', None)
                file_name = request.POST.get('fileName', '')
                assignment.Heading = title
                assignment.Type = assignment_type
                assignment.Description = description
                if not (start_time is None):
                    if end_time == '':
                        assignment.StartTime = None
                    else:
                        assignment.StartTime = start_time
                if not (end_time is None):
                    if end_time == '':
                        assignment.EndTime = None
                    else:
                        assignment.EndTime = end_time
                if full_mark != -1 and full_mark != '':
                    assignment.FullMark = full_mark
                if file_name != '' and file_name != assignment.get_attachment_name():
                    if not (assignment.AttachmentUrl is None) and assignment.AttachmentUrl != '':
                        path = MEDIA_ROOT + assignment.AttachmentUrl[7:]
                        if os.path.exists(path):
                            os.remove(path)
                    final_path = tmp_path = 'course' + str(cid)
                    tmp_path += '/tmp/' + request.session.get('uid', '') + '/' + file_name
                    final_path += '/homework' + str(assignment.id) + '/assignment/' + file_name
                    shutil.move(MEDIA_ROOT + tmp_path, MEDIA_ROOT + final_path)
                    assignment.AttachmentUrl = MEDIA_URL + final_path
                assignment.save()
    except ObjectDoesNotExist:
        response['result'] = 0
        response['error'] = 'assignment does not exist'
    return JsonResponse(response)


# 删除作业接口
def delete_assignment(request, cid, aid):
    if request.method == 'GET':
        return HttpResponseRedirect("../newassignment/")
    response = {'result': 0}
    cid = int(cid)
    aid = int(aid)
    try:
        course = Courses.objects.get(id=cid)
        assignment = Homeworks.objects.get(id=aid)
        if int(assignment.Course_id) != cid:
            response['error'] = 'permission denied'
        else:
            response['AttachmentUrl'] = assignment.AttachmentUrl
            assignment.delete()
            response['AttachmentUrl'] = assignment.AttachmentUrl
            if not (assignment.AttachmentUrl is None) and assignment.AttachmentUrl != '':
                path = MEDIA_ROOT + 'course' + str(cid) + '/homework' + str(aid) + '/'
                if os.path.exists(path):
                    shutil.rmtree(path)
            response['result'] = 1
    except ObjectDoesNotExist:
        response['error'] = 'assignment does not exist'
    return JsonResponse(response)


# 上传课程新建作业附件接口
def upload_attachments(request, cid):
    if request.method == 'GET':
        return HttpResponseRedirect("../newassignment/")
    # TODO 检查课程是否属于教师
    response = {'result': 1}
    attachment = request.FILES.get('attachment', None)
    relative_path = 'course' + cid + '/tmp/' + request.session.get('uid', '') + '/'
    save_file(attachment, relative_path)
    response['fileUrl'] = '/media/' + relative_path + attachment.__str__()
    response['fileName'] = attachment.__str__()
    return JsonResponse(response)


# 重新上传课程作业附件接口
# 弃用！！！！！
def reupload_attachments(request, cid, aid):
    if request.method == 'GET':
        return HttpResponseRedirect("../newassignment/")
    # TODO 检查课程是否属于教师
    response = {'result': 1}
    attachment = request.FILES.get('attachment', None)
    relative_path = 'course' + cid + '/homework' + aid + '/assignment/'
    save_file(attachment, relative_path)
    cid = int(cid)
    aid = int(aid)
    try:
        assignment = Homeworks.objects.get(id=aid)
        if int(assignment.Course_id) != cid:
            response['result'] = 0
            response['error'] = 'permission denied'
        else:
            # TODO 删除原来附件
            assignment.AttachmentUrl = '/media/' + relative_path + attachment.__str__()
            assignment.save()
            response['fileUrl'] = assignment.AttachmentUrl
            response['fileName'] = attachment.__str__()
    except ObjectDoesNotExist:
        response['result'] = 0
        response['error'] = 'assignment does not exist'
    return JsonResponse(response)


# 删除附件接口
def delete_attachments(request, cid):
    if request.method == 'GET':
        return HttpResponseRedirect("../newassignment/")
    # TODO 检查课程是否属于教师
    response = {'result': 0}
    aid = request.POST.get('aid', -1)
    print('aid:' + aid)
    file_url = request.POST.get('fileUrl', '')
    if file_url != '':
        file_path = MEDIA_ROOT + file_url[7:]
        if os.path.exists(file_path):
            os.remove(file_path)
            response['result'] = 1
            if int(aid) != -1:
                assignment = Homeworks.objects.get(id=int(aid))
                assignment.AttachmentUrl = None
                assignment.save()
        else:
            response['error'] = 'file not exists'
    else:
        response['error'] = 'file url required'
    return JsonResponse(response)


# 课程资源管理页面
def resources(request, cid):
    context = {'cid': cid}
    course = Courses.objects.get(id=int(cid))
    resources = course.coursefile_set.all()
    context['resources'] = resources
    return render(request, 'Teacher/ResManage.html', context)


# 上传课程资源接口
def upload_resources(request, cid):
    if request.method == 'GET':
        return HttpResponseRedirect("./")
    # TODO 检查课程是否属于教师
    response = {'result': 1}
    resource = request.FILES.get('resource', None)
    response['resource'] = resource.__str__()
    relative_path = 'course' + cid + '/resources/'
    save_file(resource, relative_path)
    cid = int(cid)
    (course_file, created) = CourseFile.objects.update_or_create(course_id=cid, filename=resource.__str__())
    teacher = Teachers.objects.get(TNo=request.session.get('uid'))
    course_file.uploader = teacher
    course_file.save()
    course = Courses.objects.get(id=cid)
    if course.resourcesPath is None or course.resourcesPath == '':
        course.resourcesPath = '/media/course' + str(cid) + '/resources/'
        course.save()
    return JsonResponse(response)


# 删除课程资源接口
def delete_resources(request, cid, rid):
    if request.method == 'GET':
        return HttpResponseRedirect("../")
    response = {'result': 0}
    try:
        course_file = CourseFile.objects.get(id=int(rid))
        if course_file.course_id != int(cid):
            response['error'] = 'permission denied'
        else:
            path = MEDIA_ROOT + 'course' + cid + '/resources/' + course_file.filename
            if os.path.exists(path):
                os.remove(path)
            course_file.delete()
            response['result'] = 1
    except ObjectDoesNotExist:
        response['error'] = 'resource does not exist'
    return JsonResponse(response)


# 课程作业(可批改)列表页面
def homework_list(request, cid):
    context = {'cid': cid}
    course = Courses.objects.get(id=int(cid))
    revisable_homework = course.homeworks_set.filter(EndTime__lte=datetime.datetime.now(timezone.utc))
    context['revisable_homework'] = revisable_homework
    return render(request, 'Teacher/HomeworkList.html', context)


# 课程批改作业页面 TODO
def homework(request, cid, hid):
    context = {'cid': cid, 'hid': hid}
    homework = Homeworks.objects.get(id=int(hid))
    submissions = homework.get_submissions()
    context['submissions'] = submissions
    return render(request, 'Teacher/HwCorrect.html', context)


# 教师批改课程作业接口（POST）
def mark_homework(request, cid, hid):
    if request.method == 'GET':
        return HttpResponseRedirect("./")
    response = {'result': 1}
    submissions = request.POST.get('submissions', '[]')
    submissions = json.loads(submissions)
    print(submissions)
    for s in submissions:
        sid = s.get('sid')
        score = s.get('score')
        comment = s.get('comment')
        if sid is not None and sid != "" and score is not None and score != "" and comment is not None:
            try:
                submission = TeamHomeworks.objects.get(id=int(sid))
                submission.Score = float(score)
                submission.Comment = comment
                submission.save()
            except ObjectDoesNotExist:
                response['result'] = 0
                response['error'] = 'submission does not exist'
        else:
            response['result'] = 0
            response['error'] = 'score or comment required'
    return JsonResponse(response)


# 批量下载接口
def batch_download(request):
    if request.method == 'GET':
        return HttpResponseRedirect("/")
    response = {'result': 1}
    file_list = request.POST.get('links', '[]')
    hid = request.POST.get('hid', -1)
    if hid == -1:
        tmp_dir = 'resources/tmp/'
    else:
        tmp_dir = 'homework' + str(hid) + '/tmp/'
    file_list = json.loads(file_list)
    zip_url = pack_files(file_list, tmp_dir)
    response['zipLink'] = zip_url
    return JsonResponse(response)


# args: 文件url列表, 课程目录下的临时文件夹
def pack_files(url_list, tmp_dir):
    if len(url_list) >= 1:
        first_url = url_list[0]
        pos = first_url.find('course')
        pos1 = first_url.find('/', pos + 6, -1)
        course_url = first_url[pos:pos1 + 1]  # 不以‘/’开头，以‘/’结尾
        course_id = first_url[pos + 6:pos1]
        tmp_path = MEDIA_ROOT + course_url + tmp_dir  # .replace('/', '\\')
        all_str = ""
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        for file_url in url_list:
            all_str += file_url
        zip_file_name = str(hash(all_str)) + '.zip'
        zip_file_path = tmp_path + zip_file_name
        try:
            zf = zipfile.ZipFile(zip_file_path, "w", zipfile.zlib.DEFLATED)
        except Exception as e:
            print(e)
        print('zip_file_path: ' + zip_file_path)
        for file_url in url_list:
            pos = file_url.find('course')  # 找到字符串中course的c的下标
            file_or_dir = MEDIA_ROOT + file_url[pos:]  # .replace('/', '\\')
            pos = file_or_dir.rfind('/')  # 从文件路径字符串末尾反向查找/的位置
            if os.path.isfile(file_or_dir):
                file = file_or_dir
                zf.write(file, file[pos + 1:])
            else:
                for root, dirs, files in os.walk(file_or_dir):
                    for name in files:
                        file = os.path.join(file_or_dir, name).replace('\\', '/')
                        zf.write(file, file[pos + 1:])
        zf.close()
        zip_url = MEDIA_URL + course_url + tmp_dir + zip_file_name
        return zip_url
    return ''


# 保存文件在服务器文件系统
def save_file(file, path):
    file_path = ''
    try:
        path = MEDIA_ROOT + path
        if not os.path.exists(path):
            os.makedirs(path)
        file_path = path + file.name
        destination = open(file_path, 'wb+')
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()
    except Exception as e:
        print(e)
    return file_path


# 教师课程内在线交流页面
def communication(request, cid=-1):
    context = {}
    try:
        uid = int(request.session.get('uid'))
        context['userId'] = uid
        cid = int(cid)
        context['courseId'] = cid
        course = Courses.objects.get(id=cid)
        context['cid'] = cid
        context['courseName'] = course.Name
        student_list = []
        sttList = course.stt_set.all()  # STT.objects.filter(Course_id=cid)
        for sttItem in sttList:
            stuObj = {}
            stuId = sttItem.SNo_id
            student = Students.objects.get(SNo=stuId)
            stuObj['userId'] = str(stuId)
            stuObj['userName'] = student.Name
            stuObj['userToken'] = student.Token
            student_list.append(stuObj)
        context['studentList'] = student_list
        teacher_list = []
        teachcourse_list = course.teachcourse_set.all()
        for tc in teachcourse_list:
            teaObj = {}
            teacher = tc.TNo
            teaObj['userId'] = teacher.TNo
            teaObj['userName'] = teacher.Name
            teaObj['userToken'] = teacher.Token
            if uid == teacher.TNo:
                context['userName'] = teacher.Name
                context['userToken'] = teacher.Token
            teacher_list.append(teaObj)
        context['teacherList'] = teacher_list
        # context['type'] = course.type
    finally:
        return render(request, 'Teacher/Communicate.html', context)


# ------------- zycdev -------------

# -----------------------------------------------------------------------------------------------------------------------------------------
# ljx曾经写过的代码

# 教师团队审核界面，需要前端传来cid
def team_check(request, cid):
    context = {}
    try:
        context['uid'] = request.session.get('uid')
        context['cid'] = cid
        context['courseId'] = cid
        teamList = Teams.objects.filter(Status=1)
        tmList = []
        for team in teamList:
            teamInfo = {}
            teamInfo['id'] = team.id
            teamInfo['name'] = team.Name
            teamInfo['introduction'] = team.Introduction
            try:
                student = Students.objects.get(SNo=team.TeamLeader_id)
                stuName = student.Name
                teamInfo['teamLeader'] = stuName
            except Exception as e:
                print(e)
            teamInfo['studentCount'] = team.StudentCount
            tmList.append(teamInfo)
        context['teamList'] = tmList
    except Exception as e:
        tmList = []
    finally:
        return render(request, 'Teacher/TeamAudit.html', context)


def teamCheck(request, cid):
    if request.method == 'POST':
        context = {}
        try:
            context['uid'] = request.session.get('uid')
            context['cid'] = cid
            context['courseId'] = cid
            teamId = request.POST.get('id')
            type = request.POST.get('type')
            team = Teams.objects.get(id=teamId)

            if type == '1':  # 表示老师同意团队创建
                team.Status = 2
                team.save()
                context['type'] = 2
                context['message'] = 'agree the team application'
                return JsonResponse(context)
            else:  # 表示老师拒绝团队创建
                sttList = STT.objects.filter(Course_id=cid, Team_id=team.id)
                for stt in sttList:
                    stt.delete()
                team.delete()
                context['type'] = 3
                context['message'] = 'disagree the team application '
                return JsonResponse(context)
        except Exception as e:
            context['type'] = 4
            context['message'] = 'unknown error'


# 删除文件（课程资源）
def delete_file(request):
    if request.method == 'POST':
        courseId = request.POST('courseId')
        filename = request.POST('filename')
        try:
            path = MEDIA_ROOT + 'Course' + str(courseId) + '/TeachingFiles/'
            if not os.path.exists(path):
                return JsonResponse({'status': 'failed', 'info': 'courseId error'})
            file_name = path + filename
            if not os.path.exists(file_name):
                return JsonResponse({'status': 'failed', 'info': 'file not exist'})
            os.remove(file_name)
            return JsonResponse({'status': 'success', 'info': 'delete success'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'info': 'delete error'})


# 教师点击作业下载学生作业
def download_hmwkfile(request):
    if request.method == 'POST':
        courseId = request.POST('courseId')
        filename = request.POST('filename')

        # 里面调用下载文件的函数，然后返回response

        return


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


def homeworkdownload(request):
    context = {}
    try:
        context['userid'] = request.session['uid']
    finally:
        return render(request, 'Teacher/HwDownload.html', context)


# -------------------------------------------------------------------------------------------------------------------------------------------------

'''
def showPubHw(request):
    context = {}
    try:
        TNo = request.session['TNo']
        Teacher = Teachers.objects.get(TNo=TNo)
        Course = Courses.objects.get(id=course_id)
        context = {}
        context['Teacher_Name'] = Teacher.Name
        context['course_id'] = course_id
        context['startTime'] = request.POST['startTime']
        context['endTime'] = request.POST['endTime']
        context['heading'] = request.POST['heading']
        context['description'] = request.POST['description']
        course_name = Course.Name
        path = course_name + '/' + 'homework'
        homework = Homeworks(Course=course_id, StartTime=startTime, EndTime=endTime, heading=heading,
                             description=description, path=path)
        homework.save()
        if homework.id == None or homework.id == '':
            return HttpResponse('保存失败')
        else:
            return HttpResponse(homework.id)
    finally:
        return render(request, 'Teacher/AssignmentDetail.html', context)'''


########黄丹#########
def checkLogin(request):
    if 'uid' not in request.session or request.session['uid']:
        return HttpResponseRedirect("/login/")


@csrf_exempt
def set_course(request, id):
    checkLogin(request)
    if request.method == "POST":
        course_id = int(request.POST['course_id'])
        course = Courses.objects.get(id=course_id)
        '''
            type:0不是团队/1是团队课程
            teamMaximum:Interger团队人数上限
            teamMinimum:Interger团队人数下限
            credit:Float学分
            teachHour:Interger教学课时
            practiceHour:Integer实践课时
            plan:text 教学计划
        '''
        context = {'cid': course_id}
        course.type = int(request.POST.get('type', '0'))
        course.teamMaximum = int(request.POST.get('teamMaximum', '1'))
        course.teamMinimum = int(request.POST.get('teamMinimum', '1'))
        course.credit = float(request.POST.get('credit', '0.0'))
        course.teachHour = int(request.POST.get('teachHour', ''))
        course.practiceHour = int(request.POST.get('practiceHour'))
        course.plan = request.POST.get('plan', '')
        result = True
        try:
            course.save()
        except Exception as e:
            result = False
        finally:
            course = Courses.objects.get(id=course_id)
            can_be_alter = True
            if course.beginDate < datetime.date.today():
                can_be_alter = False
            context['course'] = course
            context['can_be_alter'] = can_be_alter
            return render(request, 'Teacher/CourseSet.html', context)
    else:
        return HttpResponseRedirect('../settings')


def view_course_info(request, course_id):
    checkLogin(request)
    course = Courses.objects.get(id=course_id)
    context = {'cid': course_id}
    can_be_alter = True
    if course.beginDate < datetime.date.today():
        can_be_alter = False
    if request.method == 'GET':
        context['course'] = course
        context['can_be_alter'] = can_be_alter
    return render(request, 'Teacher/CourseSet.html', context)
    # return HttpResponse(can_be_alter)

########黄丹#########
