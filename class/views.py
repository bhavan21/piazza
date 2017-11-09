from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Class,ClassInsRelation,Joins,Topic,Post,ViewRelation,PinRelation,TopicPostRelation,Comment,Poll,Option,OptionStudRelation
from django.urls import reverse
import datetime

loginURL = '/class/login/'


def login(request):
	return render(request, 'class/login.html', {})


def register(request):
	return render(request, 'class/register.html', {})


@login_required(login_url=loginURL)
def index(request):
	context = {}
	return render(request, 'class/index.html', context)


@login_required(login_url=loginURL)
def home(request, class_code):
	isclasstaken = Joins.objects.filter(
						class_id__class_code__exact=class_code,
						stud_id_id__exact=request.session['id']
					).count()
	if isclasstaken > 0:
		posts = Post.objects.filter(
					time_stamp__lt=datetime.datetime.now(),
					class_id__class_code__exact=class_code
				).order_by('-time_stamp')
		context = {
			'posts': posts,
			'error': ''
		}
		return render(request, 'class/home.html', context)
	else:
		context = {
			'posts': '',
			'error': 'This is class not taken by you'
		}
		return render(request, 'class/home.html', context)