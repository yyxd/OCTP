# -*- coding: utf-8 -*
from __future__ import unicode_literals
from django.utils import timezone
from django.db import models
from django import forms
import datetime
from OnlineTeaching.settings import *


# TODO 设置字段默认值

# 课程表
class Courses(models.Model):
    def __unicode__(self):
        return self.Name

    def __str__(self):
        return self.Name

    # TODO 待测试
    def gen_resources_path(self):
        return '/media/course' + str(self.id) + '/resources/'

    Name = models.CharField(max_length=40)
    Department = models.CharField(max_length=40)
    Semester = models.CharField(max_length=40, null=True)
    Weeks = models.IntegerField(null=True)
    StudentCount = models.IntegerField(null=True)
    credit = models.FloatField(default=0.0)
    type = models.IntegerField(default=0)  # type 为0表示个人课程/为1表示团队课程
    teamMaximum = models.IntegerField(default=0)
    teamMinimum = models.IntegerField(default=0)
    teachHour = models.IntegerField(default=0)
    practiceHour = models.IntegerField(default=0)
    beginDate = models.DateField(default='2016-03-01')
    plan = models.TextField(default='')
    resourcesPath = models.CharField(null=True, max_length=1000, auto_created=gen_resources_path)  # 资源存放目录(网站绝对路径）


# 教师表
class Teachers(models.Model):
    TNo = models.IntegerField(primary_key=True)
    Pwd = models.CharField(max_length=200)
    Name = models.CharField(max_length=40)
    Sex = models.CharField(max_length=6, null=True)
    Position = models.CharField(max_length=40, null=True)
    Department = models.CharField(max_length=40)
    Email = models.EmailField(null=True)
    Phone = models.CharField(max_length=20, null=True)
    Courses = models.ManyToManyField(Courses, through='TeachCourse', related_name='jiaoke')
    Token = models.CharField(max_length=200, null=True)  # 教师在线聊天的Token


class Admin(models.Model):
    ANo = models.IntegerField(primary_key=True)
    Pwd = models.CharField(max_length=200)
    Name = models.CharField(max_length=40)
    Sex = models.CharField(max_length=6, null=True)


# 学生表
class Students(models.Model):
    SNo = models.IntegerField(primary_key=True)
    Pwd = models.CharField(max_length=200)
    Name = models.CharField(max_length=40)
    Sex = models.CharField(max_length=6, null=True)
    Department = models.CharField(max_length=40)
    Email = models.CharField(max_length=50, null=True)
    Phone = models.CharField(max_length=20, null=True)
    Courses = models.ManyToManyField(Courses, through='STT', related_name='xuanke')
    Token = models.CharField(max_length=200, null=True)  # 表示学生在线聊天的Token


# 团队表,由学生组成团队
class Teams(models.Model):
    Name = models.CharField(max_length=128, default='')  # 团队名称
    Introduction = models.TextField(default='')  # 团队介绍
    Status = models.IntegerField(default=0)  # 团队状态
    '''status = 0 团队正在创建,此时团队队长可以审批
    status = 1 团队创建成功,提交给教师批准
    status = 2 团队教师审批通过
    status = 3 团队教师审批未通过
    '''
    TeamLeader = models.ForeignKey(Students, on_delete=models.CASCADE)
    StudentCount = models.IntegerField(default=1)  # 团队当前人数
    Course = models.ForeignKey(Courses, on_delete=models.CASCADE)


# 团队学生课程
class STT(models.Model):
    SNo = models.ForeignKey(Students, on_delete=models.CASCADE)
    Course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    Team = models.ForeignKey(Teams, on_delete=models.CASCADE, null=True)


# 教师教课表 教师与课程表多对多关系
class TeachCourse(models.Model):
    TNo = models.ForeignKey(Teachers, on_delete=models.CASCADE)
    Course = models.ForeignKey(Courses, on_delete=models.CASCADE)


# 作业表 与课程多对一关系
class Homeworks(models.Model):
    ASSIGNMENT_TYPE = (
        ('I', '个人'),
        ('T', '团队'),
    )

    def __unicode__(self):
        return self.Heading

    def get_attachment_name(self):
        attachment_name = self.AttachmentUrl
        if attachment_name is not None and attachment_name != '':
            pos = attachment_name.rfind('/')
            attachment_name = attachment_name[pos + 1:]
        return attachment_name

    def get_submission_num(self):
        return self.teamhomeworks_set.count()

    def get_submissions(self):
        return self.teamhomeworks_set.all()

    Heading = models.CharField(max_length=200, verbose_name='标题')
    InsertTime = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    StartTime = models.DateTimeField(null=True, verbose_name='开始时间')
    EndTime = models.DateTimeField(null=True, verbose_name='结束时间')
    Type = models.CharField(max_length=10, choices=ASSIGNMENT_TYPE, default='I', verbose_name='形式')
    Description = models.TextField(null=True, verbose_name='描述')
    AttachmentUrl = models.CharField(max_length=1000, null=True, verbose_name='附件')
    FullMark = models.DecimalField(null=True, max_digits=6, decimal_places=2, verbose_name='满分')
    Course = models.ForeignKey(Courses, null=True, on_delete=models.CASCADE)


# 团队提交作业表,以团队方式提交,如果是个人课程,那么团队仅有一人且是负责人
class TeamHomeworks(models.Model):
    def __str__(self):
        return self.Name

    def get_team_or_student_info(self):
        if self.Team is None:
            return str(self.Student.SNo) + '-' + self.Student.Name
        else:
            return str(self.Team.id) + '-' + self.Team.Name

    SubmitTime = models.DateTimeField()  # 最后提交时间
    Homework = models.ForeignKey(Homeworks, on_delete=models.CASCADE)
    Team = models.ForeignKey(Teams, on_delete=models.CASCADE, null=True)
    Name = models.CharField(max_length=128)  # 上传附件的名称
    Path = models.CharField(max_length=256)  # 上传附件的路径
    Comment = models.TextField(null=True)  # 教师评语
    Score = models.FloatField(null=True)  # 教师评分
    Student = models.ForeignKey(Students, on_delete=models.CASCADE)  # 最后一次提交作业的学生


class CourseFile(models.Model):
    def __unicode__(self):
        return self.filename

    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    uploader = models.ForeignKey(Teachers, on_delete=models.CASCADE, null=True)
    # uploadername = models.CharField(max_length=30)
    filename = models.CharField(max_length=50)
    updateTime = models.DateTimeField(auto_now_add=True)
    # path = models.CharField(max_length=100)


# 团队申请者
# 申请团队时创建,
# Status = 0 刚刚申请,TeamLeader未审批
# Status = 1 TeamLeader 同意本次申请 将该人加入到Team中
# Status = 2 TeamLeader 不同意本次申请
class Applicant(models.Model):
    Student = models.ForeignKey(Students, on_delete=models.CASCADE)
    Team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    Status = models.IntegerField(default=0)


