from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include, url
from Admin import views

urlpatterns = [
    url(r'^$',views.index),
    url(r'^login$',views.login),
    url(r'^SemesterSetting/$',views.semestersetting),
    url(r'^CourseSetting/$',views.coursesetting),
    url(r'^StudentSetting/$',views.studentsetting),
    url(r'^TeacherSetting/$',views.teachersetting),
    url(r'^TeacherInfoModify/(\d+)$',views.teacherInfoModify),
    url(r'^StudentInfoModify/(\d+)$',views.studentInfoModify),
    url(r'^uploadStudentInfo$',views.uploadStudentInfo),
    url(r'^uploadTeacherInfo$',views.uploadTeacherInfo),
    url(r'^uploadCourseInfo$',views.uploadCourseInfo),
    url(r'^teacherSetting/$',views.teacherSetting),
]