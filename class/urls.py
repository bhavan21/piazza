from django.conf.urls import url
from . import views
from django.core.urlresolvers import reverse

app_name = 'class'

urlpatterns = [
	url(r'^$', views.userhome, name='userhome'),
	url(r'^login$', views.login_, name='login_'),
	url(r'^register$', views.register, name='register'),
	url(r'^logout$', views.logout_, name='logout_'),
	url(r'^(?P<class_code>[A-Za-z0-9]+)$', views.classhome, name='classhome'),
	url(r'^join_form', views.join_form, name='join_form'),
	url(r'^create_form', views.create_form, name='create_form'),
]
