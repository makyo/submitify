from django.conf.urls import (
    include,
    url,
)
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^', include('submitify.urls')),
    url(r'^', include('usermgmt_standalone.urls')),
]
