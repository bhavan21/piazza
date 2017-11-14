from django.conf.urls import url
from . import views
from django.core.urlresolvers import reverse

app_name = 'class'

urlpatterns = [
<<<<<<< HEAD
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login_, name='login'),
    url(r'^register$', views.register, name='register'),
     url(r'^home',views.user_home,name = 'user_home'),
    url(r'^join_form',views.join_form , name ='join_form'),
    url(r'^create_form',views.create_form , name ='create_form'),
    url(r'^logout$', views.logout_, name='logout'),

=======
	url(r'^$', views.userhome, name='userhome'),
	url(r'^login$', views.login_, name='login_'),
	url(r'^register$', views.register, name='register'),
	url(r'^logout$', views.logout_, name='logout_'),
	url(r'^(?P<class_code>[A-Za-z0-9]+)/', views.classhome, name='classhome'),
	url(r'^join_form$', views.join_form, name='join_form'),
	url(r'^create_form$', views.create_form, name='create_form'),
	url(r'^new_post$', views.new_post, name='new_post'),
	url(r'^get_post$', views.get_post, name='get_post'),
	url(r'^new_comment$', views.new_comment, name='new_comment'),
>>>>>>> a7cd484c9648fcf83b040874bf97632bc24c5391
]
