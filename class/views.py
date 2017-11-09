from django.shortcuts import render, redirect
from django.template import loader
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Class,ClassInsRelation,Joins,Topic,Post,ViewRelation,PinRelation,TopicPostRelation,Comment,Poll,Option,OptionStudRelation
import datetime,json


loginURL = '/class/login'


@csrf_exempt
def login_(request):
	# print(request.session.get_expire_at_browser_close())
	if request.session.get("id") is not None:
		return redirect(index)
	if request.method == 'POST':
		email = request.POST.get("email")
		password = request.POST.get("password")
		user = authenticate(username=email, password=password)
		if user is not None:
			request.session["name"] = user.first_name + " " + user.last_name
			request.session["id"] = user.id
			login(request, user)
			return redirect(index)
		else:
			return render(request, 'class/login.html', {"error": "Wrong Credentials"})
	return render(request, 'class/login.html', {})


@csrf_exempt
def register(request):
	if request.session.get("id") is not None:
		return redirect(index)
	if request.method == 'POST':
		first_name = request.POST.get("first_name")
		last_name = request.POST.get("last_name")
		email = request.POST.get("email")
		password = request.POST.get("password")
		user, created = User.objects.get_or_create(first_name=first_name, last_name=last_name, username=email, email=email)
		if created:
			user.set_password(password)  # This line will hash the password
			user.save()
			request.session["name"] = first_name + " " + last_name
			request.session["id"] = user.id
			login(request, user)
			return redirect(index)
		else:
			return render(request, 'class/register.html', {"error": "Error while signing up. Please try again"})
	return render(request, 'class/register.html', {})


@login_required(login_url=loginURL)
def index(request):
	context = {}
	return render(request, 'class/index.html', context)


@login_required(login_url=loginURL)
def home(request, class_code):
	if request.session.get("id") is not None:
		sessionid = request.session.get("id")

		isclasstaken = Joins.objects.filter(
							class_id__class_code__exact=class_code,
							stud_id_id__exact=sessionid
						).count()

		if isclasstaken > 0:
			posts = Post.objects.filter(
						time_stamp__lt=datetime.datetime.now(),
						class_id__class_code__exact=class_code
					).order_by('-time_stamp')

			context = {
				'posts': [],
				'error': ''
			}

			for i in posts:
				temp = ViewRelation.objects.filter(user_id=sessionid, post_id=i.id).count()

				if temp > 0:
					seen = 1
				else:
					seen = 0

				newobj = {
					"post": i,
					"seen": seen
				}
				context["posts"].append(newobj)

			return render(request, 'class/home.html', context)
		else:
			context = {
				'posts': [],
				'error': 'This class is not taken by you'
			}
			return render(request, 'class/home.html', context)
	else:
		return render(request, 'class/login.html', {"error": "You are not logged in! Please login "})


def logout_(request):
	logout(request)		# logout flushes the session
	return redirect(login_)
