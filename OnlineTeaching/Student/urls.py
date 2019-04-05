from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include, url
from Student import views

# 以 / 结尾的url请求的为页面，其余为API接口（一般返回json）    by:zycdev
urlpatterns = [
    url(r'^$', views.index, name='sIndex'),  # 学生首页
    url(r'^login$', views.login),  # 学生登录接口
    url(r'^infoModify/$', views.infoModify,name = 'view_infoModify'),  # 学生信息修改页面
    url(r'^saveModifyInfo$', views.saveModifyInfo),  # 学生信息修改保存接口，只能改邮箱和手机号
    url(r'^homeworks/$', views.view_homeworks, name='view_homeworks'),  # 浏览课程作业列表
    url(r'^homework/(\d+)/(\d+)/$', views.view_homework, name='view_homework'),  # 浏览作业详情
    url(r'^communicate/$',views.course_communicate,name='communicate'),  #学生在线交流页面,可以显示多门课程的聊天消息
    url(r'^course/(\d+)/communicate/$',views.course_communicate,name='course_communicate'), #学生课程内的在线交流页面，只显示本门课程的聊天消息
    #url(r'^resources/courses/$', views.show_courses, name='showcourses'),  # 显示学生已选课程列表
    url(r'^resources/teachfiles/$',views.show_teachingfile,name='showteachingfile'),  #显示学生选择的某门课程的资源接口
    url(r'^course/(?P<cid>\d+)/view_resources/$', views.view_resources,name="view_resources"),  # 显示学生选择的某门课程的课程资源
    #在用?P<cid>写法时需要保证前端的cid名字和这里一致
    url(r'^course/(\d+)/view_course_homeworks/$', views.view_course_homeworks,name='view_course_homeworks'),  # 学生某门课程作业列表
    url(r'^course/(\d+)/delete_homework$', views.delete_homework,name='delete_homework'),  # 学生删除作业
    url(r'^resources/$', views.download_coursefile, name="download_resources"),
    url(r'^upload_homeworks/(\d+)$', views.upload_homeworks,name="uploadhomeworkfile"),  # 上传学生作业
    url(r'^commit_homeworks$',views.commit_howorks),  #提交学生作业
    url(r'^download/(?P<courseId>\d+)/(?P<filename>\w+)$', views.download_coursefile),  # 学生下载资源接口
    url(r'^download_many',views.download_manyfiles) , #学生批量下载多个课程资源接口
    url(r'^course/(\d+)/team/create/$', views.create_team, name='create_team'),  # 创建团队
    url(r'^course/(\d+)/team/check/$', views.check_team, name='check_team'),  # 创建团队
    url(r'^course/(\d+)/team/apply/$', views.apply_team, name='apply_team'),  # 申请团队
    url(r'^course/(\d+)/team/view/$', views.view_teams, name='view_teams'),  # 查看课程团队
    url(r'^course/(\d+)/team/submit/$', views.submit_team, name='submit_to_teacher'),  # 查看课程团队
    url(r'^course/(\d+)/view/$', views.view_course, name='view_course'),  # 提交团队至教师审核
    # url(r'^course/team/view/(\d+)$', views.view_team, name='view_team'),  # 查看我的团队

    url(r'^course/(\d+)/$',views.courseIndex,name='course_index'),
]
