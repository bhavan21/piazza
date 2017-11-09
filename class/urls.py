from django.conf.urls import url
from . import views
from django.core.urlresolvers import reverse

app_name = 'class'

urlpatterns = [
	url(r'^login/$', views.login, name='login'),
	url(r'^register/$', views.register, name='register'),
	url(r'^$', views.index, name='index'),
	url(r'^(?P<class_code>[A-Za-z0-9]+)/$', views.home, name='home'),
]