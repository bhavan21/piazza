<<<<<<< HEAD
from django.shortcuts import render,redirect
from django.http import HttpResponse
=======
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
>>>>>>> a7cd484c9648fcf83b040874bf97632bc24c5391
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.shortcuts import render
from django.template import loader
from .models import Joins
from datetime import datetime
from django.utils import timezone
from .models import Class
from .models import ClassInsRelation
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Class,ClassInsRelation,Joins,Topic,Post,ViewRelation,PinRelation,TopicPostRelation,Comment,Poll,Option,OptionStudRelation
import json
from datetime import datetime
from django.utils import timezone
from django.utils.crypto import get_random_string

<<<<<<< HEAD
@login_required(login_url='/class/login')
def index(request):
    return render(request, 'class/index.html', {})

@csrf_exempt
def login_(request):
    print(request.session.get_expire_at_browser_close())
    if request.session.get("email")!=None:
        return redirect(index)
    if request.method == 'POST':
        email=request.POST.get("email")
        password=request.POST.get("password")
        user=authenticate(username=email,password=password)
        if user is not None:
            request.session["name"] = user.first_name+" "+user.last_name
            request.session["email"] = email
            login(request,user)
            return redirect(user_home)
        else:
            return render(request, 'class/login.html', {"error":"Wrong Credentials"})
    return render(request, 'class/login.html', {})

@csrf_exempt
def register(request):
    if request.session.get("email")!=None:
        return redirect(index)
    if request.method == 'POST':
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        email=request.POST.get("email")
        password=request.POST.get("password")
        user, created = User.objects.get_or_create(first_name=first_name, last_name=last_name,username=email, email=email)
        if created:
            user.set_password(password) # This line will hash the password
        user.save()
        request.session["name"] = first_name+" "+last_name
        request.session["email"] = email
        return redirect(index)
    return render(request, 'class/register.html', {})


def logout_(request):
    logout(request)     #logout flushes the session
    return redirect(login_)
def user_home(request):
    if request.user.is_authenticated():
        std_class = Joins.objects.filter(stud_id =  request.user)
        ins_class = ClassInsRelation.objects.filter(ins_id = request.user)
        return render(request,'class/user_home.html',{ 'instructor_class' : ins_class ,
            'student_class' : std_class , 
         'first_name' : request.user.first_name , 'last_name' : request.user.last_name })
        
        return HttpResponse(request.user.email)
    # first_name , last_name , email , username
    return redirect(index)
    return HttpResponse('Go To Login Screen')
@csrf_exempt
def join_form(request):
    if request.user.is_authenticated():
        class_code = request.POST['codein']
        pass_code = request.POST['codeout']
        class_to_join = Class.objects.filter(class_code = class_code , 
            class_password = pass_code)
        if not class_to_join:
            return HttpResponse("No Class Exists")
        some = Joins.objects.create(class_id = class_to_join.first(), 
            stud_id = request.user , time_stamp = timezone.now())
        return redirect(user_home)

    return redirect(index)

@csrf_exempt
def create_form(request):
    print("AKH")
    if request.user.is_authenticated():
        class_code = request.POST['classcode']
        class_name = request.POST['classname']
        semester = request.POST['semester']
        year = request.POST['year']
        some = Class.objects.create(course_name = class_name,
            course_code = class_code,year = year , semester = semester)
        some1 = ClassInsRelation.objects.create(class_id = some, 
            ins_id = request.user , time_stamp = timezone.now())
        return redirect(user_home)

    return redirect(index)
=======


loginURL = '/class/login'


def is_class_taken(user_id,class_code) :
	is_stud = Joins.objects.filter(
		class_id__class_code__exact=class_code,
		stud_id__id__exact=user_id
	)
	is_ins = ClassInsRelation.objects.filter(
		class_id__class_code__exact=class_code,
		ins_id__id__exact=user_id
	)
	if is_ins or is_stud:
		return True
	else:
		return False


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
			if request.POST.get("next") is not None:
				return redirect(request.POST.get("next"))
			else:
				return redirect('class:userhome')
		else:
			return render(request, 'class/login.html', {"error": "Wrong Credentials"})
	if request.GET.get("next") is not None:
		context = {'next': request.GET.get("next")}
	else:
		context={}
	return render(request, 'class/login.html', context)


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
		user_id = request.session.get("id")
		if is_class_taken(user_id,class_code):
			posts = Post.objects.filter(
						time_stamp__lt=timezone.now(),
						class_id__class_code__exact=class_code
					).order_by('-time_stamp')

			context = {
				'posts': [],
				'error': '',
				'class_code': class_code
			}
			for i in posts:
				temp = ViewRelation.objects.filter(user_id=user_id, post_id=i.id).count()

				if temp > 0:
					seen = True
				else:
					seen = False

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
		Joins.objects.create(class_id=class_to_join.first(), stud_id=request.user, time_stamp=timezone.now())
	return redirect('class:userhome')


@csrf_exempt
@login_required(login_url=loginURL)
def create_form(request):
	course_code = request.POST['classcode']
	class_name = request.POST['classname']
	semester = request.POST['semester']
	year = request.POST['year']
	while True:
		class_code=get_random_string(length=6)
		matched = Class.objects.filter(class_code=class_code)
		if not matched:
			break
	some = Class.objects.create(course_name=class_name, course_code=course_code, year=year, semester=semester,class_code=class_code)
	ClassInsRelation.objects.create(class_id=some, ins_id=request.user, time_stamp=timezone.now())
	return redirect('class:userhome')
>>>>>>> a7cd484c9648fcf83b040874bf97632bc24c5391


@csrf_exempt
@login_required(login_url=loginURL)
def new_post(request):
	user_id = request.session.get("id")
	class_code = request.POST['class_code']
	if is_class_taken(user_id,class_code):
		title = request.POST['title']
		content = request.POST['content']
		class_object = Class.objects.get(class_code=class_code)
		posted_by= User.objects.get(id=user_id)
		
		Post.objects.create(class_id=class_object,posted_by=posted_by,title=title,content=content,time_stamp=timezone.now())
		return HttpResponse("success")
	else:
		return HttpResponse("Failed")

@csrf_exempt
@login_required(login_url=loginURL)
def get_post(request):
	user_id = request.session.get("id")
	class_code = request.GET['class_code']
	post_id = request.GET['post_id']
	is_post_in_class= Post.objects.filter(id=post_id,class_id__class_code__exact=class_code)
	if is_class_taken(user_id,class_code) and is_post_in_class:
		post = Post.objects.get(id=post_id)
		comments = Comment.objects.filter(post_id=post).order_by('time_stamp')

		isread=ViewRelation.objects.filter(user_id=user_id, post_id=post_id)
		if not isread:
			user_object=User.objects.get(id=user_id)
			ViewRelation.objects.create(user_id=user_object,post_id=post)
			post.views=post.views+1
			post.save()

		data={}
		data["id"]=post.id
		data["title"]=post.title
		data["content"]=post.content
		data["posted_by"]={"id":post.posted_by.id, 
							"name":post.posted_by.first_name+" "+post.posted_by.last_name}
		data["views"]=post.views
		data["comments"]=[]
		for i in comments:
			comment={}
			comment["content"] = i.content
			comment["posted_by"] = {"id":post.posted_by.id, 
							"name":post.posted_by.first_name+" "+post.posted_by.last_name}
			data["comments"].append(comment)
		return HttpResponse(json.dumps(data))
	else:
		return HttpResponse("Failed")

@csrf_exempt
@login_required(login_url=loginURL)
def new_comment(request):
	user_id = request.session.get("id")
	class_code = request.POST['class_code']
	post_id = request.POST['post_id']
	is_post_in_class= Post.objects.filter(id=post_id,class_id__class_code__exact=class_code)
	if is_class_taken(user_id,class_code) and is_post_in_class:
		content = request.POST['content']
		posted_by= User.objects.get(id=user_id)
		post = Post.objects.get(id=post_id)
		Comment.objects.create(post_id=post, posted_by=posted_by,content=content,time_stamp=timezone.now())
		return HttpResponse("success")
	else:
		return HttpResponse("Failed")


def logout_(request):
	logout(request)		# logout flushes the session
	return redirect('class:login_')
