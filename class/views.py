from django.shortcuts import render,redirect
from django.http import HttpResponse
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
from django.contrib.auth import authenticate,login,logout

@login_required(login_url='/class/login')
def index(request):
    return render(request, 'class/index.html', {})

@csrf_exempt
def login_(request):
	print(request.session.get_expire_at_browser_close())
	if request.session.get("id")!=None:
		return redirect(index)
	if request.method == 'POST':
		email=request.POST.get("email")
		password=request.POST.get("password")
		user=authenticate(username=email,password=password)
		if user is not None:
			request.session["name"] = user.first_name+" "+user.last_name
			request.session["id"] = user.id
			login(request,user)
			return redirect(index)
		else:
			return render(request, 'class/login.html', {"error":"Wrong Credentials"})
	return render(request, 'class/login.html', {})

@csrf_exempt
def register(request):
	if request.session.get("id")!=None:
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
		request.session["id"] = user.id
		login(request,user)
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

