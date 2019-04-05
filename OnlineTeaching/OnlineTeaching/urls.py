"""OnlineTeaching URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import urls as auth_urls
from . import views
from django.views.static import serve
from OnlineTeaching import settings

# 以 / 结尾的url请求的为页面，其余为API接口（一般返回json）    by:zycdev
urlpatterns = [
    url(r'^$', views.index, name='index'),  # 首页
    url(r'^login/$', views.login, name='login'),  # 统一登录页面
    url(r'^logout', views.logout, name='logout'),  # 登出接口
    url(r'^teacher/', include('Teacher.urls')),
    url(r'^student/', include('Student.urls')),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    # url(r'^templates/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.TEMPLATE_ROOT}),
    url(r'^admin/', include('Admin.urls')),  # 教务
    url(r'^test$', views.test),  # 测试接口
    url(r'^addTest/$', views.addTestData),  # 把数据存入数据库
]
