from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.urls import reverse
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
	if request.session.get("id") is not None:
		return redirect('class:userhome')
	if request.method == 'POST':
		email = request.POST.get("email")
		password = request.POST.get("password")
		user = authenticate(username=email, password=password)
		if user is not None:
			request.session["name"] = user.first_name + " " + user.last_name
			request.session["id"] = user.id
			login(request, user)
			return redirect('class:userhome')
		else:
			return render(request, 'class/login.html', {"error": "Wrong Credentials"})
	return render(request, 'class/login.html', {})


@csrf_exempt
def register(request):
	if request.session.get("id") is not None:
		return redirect('class:userhome')
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
			return redirect('class:userhome')
		else:
			return render(request, 'class/register.html', {"error": "Error while signing up. Please try again"})
	return render(request, 'class/register.html', {})


@login_required(login_url=loginURL)
def userhome(request):
	std_class = Joins.objects.filter(stud_id=request.user)
	ins_class = ClassInsRelation.objects.filter(ins_id=request.user)
	return render(request, 'class/userhome.html', {
													'instructor_class': ins_class,
													'student_class': std_class,
													'first_name': request.user.first_name,
													'last_name': request.user.last_name
												})


@login_required(login_url=loginURL)
def classhome(request, class_code):
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

			return render(request, 'class/classhome.html', context)
		else:
			context = {
				'posts': [],
				'error': 'This class is not taken by you'
			}
			return render(request, 'class/classhome.html', context)
	else:
		return redirect(('class:login_'))


@csrf_exempt
@login_required(login_url=loginURL)
def join_form(request):
	class_code = request.POST['codein']
	pass_code = request.POST['codeout']
	class_to_join = Class.objects.filter(class_code=class_code, class_password=pass_code)
	if not class_to_join:
		return HttpResponse("No Class Exists")
	var = Joins.objects.filter(class_id=class_to_join.first(), stud_id=request.user)
	if not var:
		Joins.objects.create(class_id=class_to_join.first(), stud_id=request.user, time_stamp=datetime.datetime.now())
	return redirect('class:userhome')


@csrf_exempt
@login_required(login_url=loginURL)
def create_form(request):
	class_code = request.POST['classcode']
	class_name = request.POST['classname']
	semester = request.POST['semester']
	year = request.POST['year']
	some = Class.objects.create(course_name=class_name, course_code=class_code, year=year, semester=semester)
	ClassInsRelation.objects.create(class_id=some, ins_id=request.user, time_stamp=datetime.datetime.now())
	return redirect('class:userhome')


def logout_(request):
	logout(request)		# logout flushes the session
	return redirect('class:login_')
