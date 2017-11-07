from django.shortcuts import render,redirect
from django.template import loader
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout



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
			return redirect(index)
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
	logout(request)		#logout flushes the session
	return redirect(login_)

