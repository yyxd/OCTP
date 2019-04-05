from django.conf.urls import url
from Teacher import views

# 以 / 结尾的url请求的为页面，其余为API接口（一般返回json）    by:zycdev
urlpatterns = [
    url(r'^$', views.index, name="tIndex"),  # 教师首页
    url(r'^login$', views.login),  # 教师登录接口
    url(r'^i/$', views.self_info, name="teacher_info"),  # 教师个人中心页面
    # url(r'^addTestData$', views.addTestData),
    # 批量下载接口
    url(r'^batch_download$', views.batch_download, name='batch_download'),
    # 教师在线交流页面
    url(r'^communicate/$', views.communication, name='IM'),
    # 课程在线交流页面
    url(r'^course/(\d+)/communicate/$', views.communication, name='CIM'),
    # 教师课程空间首页 cid
    url(r'^course/(\d+)/$', views.course, name='course'),
    # 课程作业管理页面 cid
    url(r'^course/(\d+)/assignments/$', views.assignments, name='assignments'),
    # 课程新建作业页面 cid
    url(r'^course/(\d+)/assignment/new/$', views.new_assignment, name='new_assignment'),
    # 新建课程作业接口(POST) cid
    url(r'^course/(\d+)/assignment/create$', views.create_assignment, name='create_assignment'),
    # 课程(修改)作业详情页面 cid aid
    url(r'^course/(\d+)/assignment/(\d+)/$', views.assignment, name='assignment'),
    # 课程修改作业接口(POST) cid aid
    url(r'^course/(\d+)/assignment/(\d+)/update$', views.update_assignment, name='update_assignment'),
    # 删除课程作业接口(POST) cid aid
    url(r'^course/(\d+)/assignment/(\d+)/delete$', views.delete_assignment, name='delete_assignment'),
    # 上传课程新建作业附件接口(POST) cid
    url(r'^course/(\d+)/assignment/upload', views.upload_attachments, name='upload_attachments'),
    # 删除作业附件接口（POST）
    url(r'^course/(\d+)/attachments/delete$', views.delete_attachments, name='delete_attachments'),
    # 重新上传课程作业附件接口(POST) cid aid 已弃用！！！
    url(r'^course/(\d+)/assignment/(\d+)/upload', views.reupload_attachments, name='reupload_attachments'),
    # 课程资源管理页面 cid
    url(r'^course/(\d+)/resources/$', views.resources, name='resources'),
    # 上传课程资源接口(POST) cid
    url(r'^course/(\d+)/resources/upload$', views.upload_resources, name='upload_resources'),
    # 删除课程资源接口(POST) cid
    url(r'^course/(\d+)/resources/(\d+)/delete$', views.delete_resources, name='delete_resources'),
    # 课程作业列表页面
    url(r'^course/(\d+)/homework/$', views.homework_list, name='homework_list'),
    # 课程批改作业页面
    url(r'^course/(\d+)/homework/(\d+)/$', views.homework, name='homework_mark'),
    # 教师批改课程作业接口（POST）
    url(r'^course/(\d+)/homework/(\d+)/mark$', views.mark_homework, name='mark_homework'),
    # 教师团队审核页面
    url(r'^course/(\d+)/teamcheck/$',views.team_check,name='team_check'),
    # 教师团队审核接口
    url(r'^course/(\d+)/team_check$',views.teamCheck,name='teamCheck'),
    # ------------- zycdev -------------
    url(r'^course/(\d+)/homework/$', views.resources),  # 要批改的作业列表
    url(r'^course/(\d+)/homework/(\d+)/$', views.resources),  # 批改某次作业
    url(r'^download_hmwkfile$', views.download_hmwkfile),  # 下载学生作业时调用
    url(r'^index/$', views.index),
    url(r'^delete/(?P<courseId>\d+)/(?P<filename>\w+)/$', views.delete_file),
    url(r'^homeworkdownload/$', views.homeworkdownload),
    url(r'^course/(\d+)/settings/save$', views.set_course, name='set_course'),
    url(r'^course/(\d+)/settings/$', views.view_course_info, name='view_course_info'),  #查看课程信息
]
