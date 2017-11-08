from django.shortcuts import render
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
# Create your views here.
def index(request):
    return HttpResponse('OLE')


def user_home(request):
    if request.user.is_authenticated():
        std_class = Joins.objects.filter(stud_id =  request.user)
        ins_class = ClassInsRelation.objects.filter(ins_id = request.user)
        return render(request,'class/user_home.html',{ 'instructor_class' : ins_class ,
            'student_class' : std_class , 
         'first_name' : request.user.first_name , 'last_name' : request.user.last_name })
        
        return HttpResponse(request.user.email)
    # first_name , last_name , email , username
    return HttpResponse('Go To Login Screen')

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
        return user_home(request)

        return HttpResponse(class_code)