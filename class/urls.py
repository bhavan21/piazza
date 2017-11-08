from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login_, name='login'),
    url(r'^register$', views.register, name='register'),
     url(r'^/home',views.user_home,name = 'user_home'),
    url(r'^/join_form',views.join_form , name ='join_form'),
    url(r'^logout$', views.logout_, name='logout'),
]
