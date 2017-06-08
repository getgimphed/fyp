"""website URL Configuration

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

# from django.contrib.auth import urls
from django.conf.urls import url, include
from django.contrib import admin
from material.frontend import urls as frontend_urls
# from api.views import ApiEndpoint,home
# from api.views import secret_page
#from django.contrib.auth import views as auth_views
from django.contrib.auth.views import login
from django.contrib.auth import views as auth_views
from api import views
from django.conf import settings
import django
# from rest_framework import routers
# router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

urlpatterns = [
    url(r'', include(frontend_urls)),
    url(r'^accounts/login/$', django.contrib.auth.views.login, {'template_name': 'home.html'}),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/',login,{'template_name':'home.html'}),
    url(r'^auth/',views.Authentication.as_view(),name='auth'),
    url(r'^api/', include('api.urls')),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^$', views.secret_page, name='secret'),
    url(r'^api/hello', views.ApiEndpoint.as_view()),
    url(r'^static/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.STATIC_ROOT}),   
]