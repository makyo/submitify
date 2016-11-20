from django.conf.urls import url

from . import views


app_name = 'usermgmt_standalone'
urlpatterns = [
    url('^register/$', views.Register.as_view(), name='register'),
    url(r'~(?P<username>[^/]+)/', views.view_user, name='view_user'),
]
