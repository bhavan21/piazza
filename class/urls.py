from django.conf.urls import url
from . import views

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
	url(r'^get_poll$',views.get_poll , name = 'get_poll'),
	url(r'^submit_poll$',views.submit_poll , name = 'submit_poll'),
	url(r'^new_comment$', views.new_comment, name='new_comment'),
	url(r'^delete_stud$', views.delete_stud_from_class, name='delete_stud_from_class'),
	url(r'^change_class_activity$', views.change_class_activity, name='change_class_activity'),
	url(r'^add_students_to_class$', views.add_students_to_class, name='add_students_to_class'),
	url(r'^add_poll$', views.add_poll, name='add_poll'),
	url(r'^update_account_password$', views.update_account_password, name='update_account_password'),
	url(r'^add_tag$', views.add_tag, name='add_tag'),
	url(r'^stud_drop_course$', views.stud_drop_course, name='stud_drop_course'),
	url(r'^edit_comment$', views.edit_comment, name='edit_comment'),
	url(r'^delete_comment$', views.delete_comment, name='delete_comment'),
]
