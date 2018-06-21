"""
Definition of urls for CustomUser_v2.
"""

from django.conf.urls import include, url
from django.urls import path
from API.urls import router as api_router

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/',include(api_router.urls)),
]