from django.conf.urls import url
from . import views
from django.core.urlresolvers import reverse

app_name = 'class'

urlpatterns = [
	url(r'^$', views.userhome, name='userhome'),
	url(r'^login$', views.login_, name='login_'),
	url(r'^register$', views.register, name='register'),
	url(r'^logout$', views.logout_, name='logout_'),
	url(r'^(?P<class_code>[A-Za-z0-9]+)/settings', views.inst_settings, name='inst_settings'),
	url(r'^(?P<class_code>[A-Za-z0-9]+)/', views.classhome, name='classhome'),
	url(r'^join_form$', views.join_form, name='join_form'),
	url(r'^create_form$', views.create_form, name='create_form'),
	url(r'^new_post$', views.new_post, name='new_post'),
	url(r'^edit_post$', views.edit_post, name='edit_post'),
	url(r'^delete_post$', views.delete_post, name='delete_post'),
	url(r'^pin_post$', views.pin_post, name='pin_post'),
	url(r'^get_post$', views.get_post, name='get_post'),
	url(r'^new_comment$', views.new_comment, name='new_comment'),
	url(r'^edit_comment$', views.edit_comment, name='edit_comment'),
	url(r'^delete_comment$', views.delete_comment, name='delete_comment'),
]
