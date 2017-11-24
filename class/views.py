from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Class,ClassInsRelation,Joins,Topic,Post,ViewRelation,PinRelation,TopicPostRelation,Comment,Poll,Option,OptionStudRelation
import json
from datetime import datetime
from django.utils import timezone
from django.utils.crypto import get_random_string



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
			user_object=User.objects.get(id=user_id)
			polls = Poll.objects.filter(
						time_stamp__lt= timezone.now(),
						class_id__class_code__exact = class_code
					).order_by('-time_stamp')

			context = {
				'posts': [],
				'polls': [],
				'pins': [],
				'drafts': [],
				'error': '',
				'all_tags' : [],
				'class_code': class_code,
				'user_id':user_object			
			}
			all_topic = Topic.objects.filter(class_id__class_code__exact= class_code)
			
			
			for i in all_topic:
				context["all_tags"].append(i.name)

			for i in posts:
				temp = ViewRelation.objects.filter(user_id=user_id, post_id=i.id).count()

				topic_post = TopicPostRelation.objects.filter(post_id = i.id)

				tags = []
				for j in topic_post:
					tags.append(j.topic_id)

				if temp > 0:
					seen = True
				else:
					seen = False

				temp = PinRelation.objects.filter(user_id=user_id, post_id=i.id).count()
				if temp > 0:
					pinned = True
				else:
					pinned = False

				newobj = {
					"post": i,
					"tags" : tags ,
					"seen": seen
				}

				if i.is_draft==0:
					context["posts"].append(newobj)
					if pinned:
						context["pins"].append(newobj)
				if i.is_draft==1 and i.posted_by.id==user_id:
					context["drafts"].append(newobj)

				


			return render(request, 'class/classhome.html', context)
		else:
			context = {
				'posts': [],
				'error': 'This class is not taken by you'
			}
			return render(request, 'class/', context)
	else:
		return redirect(('class:login_'))


@csrf_exempt
@login_required(login_url=loginURL)
def join_form(request):
	class_code = request.POST['codein']
	pass_code = request.POST['codeout']
	class_to_join = Class.objects.filter(class_code=class_code, class_password=pass_code)
	if not class_to_join:
		return HttpResponse("Failed")
	class_ins_check = ClassInsRelation.objects.filter(class_id = class_to_join,ins_id= request.user)
	if class_ins_check:
		return HttpResponse("instructor");
	var = Joins.objects.filter(class_id=class_to_join.first(), stud_id=request.user)
	if not var:
		Joins.objects.create(class_id=class_to_join.first(), stud_id=request.user, time_stamp=timezone.now())
		return HttpResponse("success")
	return HttpResponse("already")


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
	return HttpResponse("success")


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

		if request.POST.get('data') and request.POST.get('time'):
			time_stamp=datetime.strptime(request.POST['date']+request.POST['time'], '%d %B, %Y%I:%M%p')
		else:
			time_stamp=timezone.now()
		if request.POST["is_anonymous"]=="1":
			is_anonymous=True
		else:
			is_anonymous=False

		if request.POST.get("is_draft"):
			is_draft=True
		else:
			is_draft=False

		
		tags_fetch = request.POST['tags_select']
		tags_fetch = tags_fetch.split('&')
		post_object = Post.objects.create(class_id=class_object,posted_by=posted_by,title=title,content=content,time_stamp=time_stamp,is_anonymous=is_anonymous,is_draft=is_draft)
		for tag in tags_fetch:
			id_name , tag = tag.split('=')
			topic_post = Topic.objects.get(name = tag , class_id = class_object)
			TopicPostRelation.objects.create(topic_id = topic_post , post_id = post_object)
		return HttpResponse("success")
	else:
		return HttpResponse("Failed")

@csrf_exempt
@login_required(login_url=loginURL)
def delete_post(request):
	user_id = request.session.get("id")
	class_code = request.POST['class_code']
	post_id = request.POST['post_id']
	post= Post.objects.get(id=post_id)

	is_ins = ClassInsRelation.objects.filter(
		class_id__class_code__exact=class_code,
		ins_id__id__exact=user_id
	)
	is_stud_and_has_access = Post.objects.filter(id=post_id,posted_by__id__exact=user_id);

	if is_ins or is_stud_and_has_access :
		post.delete()
		return HttpResponse("success")
	else:
		return HttpResponse("Failed")

@csrf_exempt
@login_required(login_url=loginURL)
def pin_post(request):
	user_id = request.session.get("id")
	class_code = request.POST['class_code']
	post_id = request.POST['post_id']
	post= Post.objects.get(id=post_id)

	if is_class_taken(user_id,class_code):
		is_already_pinned=PinRelation.objects.filter(user_id=user_id, post_id=post_id)
		if not is_already_pinned:
			user_object=User.objects.get(id=user_id)
			PinRelation.objects.create(user_id=user_object,post_id=post)
		return HttpResponse("success")
	else:
		return HttpResponse("Failed")


@csrf_exempt
@login_required(login_url=loginURL)
def edit_post(request):
	user_id = request.session.get("id")
	class_code = request.POST['class_code']
	post_id = request.POST['post_id']
	post= Post.objects.get(id=post_id)

	is_ins = ClassInsRelation.objects.filter(
		class_id__class_code__exact=class_code,
		ins_id__id__exact=user_id
	)
	is_stud_and_has_access = Post.objects.filter(id=post_id,posted_by__id__exact=user_id);

	if is_ins or is_stud_and_has_access :
		title = request.POST['title']
		content = request.POST['content']
		post.title=title
		post.content=content
		post.save()
		return HttpResponse("success")
	else:
		return HttpResponse("Failed")

@csrf_exempt
@login_required(login_url=loginURL)
def get_post(request):
	print("akh")
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
		if post.is_anonymous:
			data["posted_by"]={"name":"Anonymous User"}
		else:
			data["posted_by"]={"id":post.posted_by.id, 
							"name":post.posted_by.first_name+" "+post.posted_by.last_name}
		data["views"]=post.views
		data["time_stamp"]=post.time_stamp.strftime("%b %d, %I:%M %p")
		is_ins = ClassInsRelation.objects.filter(
			class_id__class_code__exact=class_code,
			ins_id__id__exact=user_id
		)
		if is_ins or post.posted_by.id==user_id:
			data["can_edit_delete"]=1;
		else:
			data["can_edit_delete"]=0;

		data["comments"]=[]
		data["tags"] = []

		topic_post = TopicPostRelation.objects.filter(post_id = post)
		print(post.id)
		for topic in topic_post:
			topic_tag = topic.topic_id.name
			data["tags"].append(topic_tag)
			print(topic_tag)
			print("akh")
		for i in comments:
			comment={}
			comment["id"]=i.id
			comment["content"] = i.content
			if i.is_anonymous:
				comment["posted_by"]={"name":"Anonymous User"}
			else:
				comment["posted_by"] = {"id":i.posted_by.id, 
							"name":i.posted_by.first_name+" "+i.posted_by.last_name}
			comment["time_stamp"]=i.time_stamp.strftime("%b %d, %I:%M %p")
			if is_ins or i.posted_by.id==user_id:
				comment["can_edit_delete"]=1;
			else:
				comment["can_edit_delete"]=0;
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
		if request.POST["is_anonymous"]=="1":
			is_anonymous=True
		else:
			is_anonymous=False
		Comment.objects.create(post_id=post, posted_by=posted_by,content=content,time_stamp=timezone.now(),is_anonymous=is_anonymous )
		return HttpResponse("success")
	else:
		return HttpResponse("Failed")

@csrf_exempt
@login_required(login_url=loginURL)
def edit_comment(request):
	user_id = request.session.get("id")
	class_code = request.POST['class_code']
	comment_id = request.POST['comment_id']
	comment= Comment.objects.get(id=comment_id)

	is_ins = ClassInsRelation.objects.filter(
		class_id__class_code__exact=class_code,
		ins_id__id__exact=user_id
	)
	is_stud_and_has_access = Comment.objects.filter(id=comment_id,posted_by__id__exact=user_id);

	if is_ins or is_stud_and_has_access :
		content = request.POST['content']
		comment.content=content
		comment.save()
		return HttpResponse("success")
	else:
		return HttpResponse("Failed")

@csrf_exempt
@login_required(login_url=loginURL)
def delete_comment(request):
	user_id = request.session.get("id")
	class_code = request.POST['class_code']
	comment_id = request.POST['comment_id']
	comment= Comment.objects.get(id=comment_id)

	is_ins = ClassInsRelation.objects.filter(
		class_id__class_code__exact=class_code,
		ins_id__id__exact=user_id
	)

	is_stud_and_has_access = Comment.objects.filter(id=comment_id,posted_by__id__exact=user_id);

	if is_ins or is_stud_and_has_access :
		comment.delete()
		return HttpResponse("success")
	else:
		return HttpResponse("Failed")

@login_required(login_url=loginURL)
def inst_settings(request,class_code):
	user_id = request.session.get("id")
	is_ins = ClassInsRelation.objects.filter(
		class_id__class_code__exact=class_code,
		ins_id__id__exact=user_id
	)
	if is_ins:
		filtered= Joins.objects.filter(class_id__class_code__exact=class_code)
		context={"stud_list":[]}
		for i in filtered:
			context["stud_list"].append(i.stud_id)
		return render(request, 'class/settings.html', context)
	else:
		return HttpResponse("You aren't instructor for this class")


def logout_(request):
	logout(request)		# logout flushes the session
	return redirect('class:login_')
