from django.conf.urls import url
from . import views
from django.core.urlresolvers import reverse

app_name = 'class'

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^login$', views.login_, name='login'),
	url(r'^register$', views.register, name='register'),
	url(r'^logout$', views.logout_, name='logout'),
	url(r'^(?P<class_code>[A-Za-z0-9]+)$', views.home, name='home'),
]
