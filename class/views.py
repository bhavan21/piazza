from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Class,ClassInsRelation,Joins,Topic,Post,ViewRelation,PinRelation,TopicPostRelation,Comment,Poll,Option,OptionStudRelation
import json
import datetime
from django.utils import timezone
from django.utils.crypto import get_random_string
from io import TextIOWrapper
from django.db.models import F
import csv


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
			return render(request, 'class/signin-up.html', {"error": "Wrong Credentials"})
	if request.GET.get("next") is not None:
		context = {'next': request.GET.get("next")}
	else:
		context = {}
	return render(request, 'class/signin-up.html', context)


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
			return render(request, 'class/signin-up.html', {"error": "Error while signing up. Please try again"})
	return render(request, 'class/signin-up.html', {})


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
						deadline__gte = timezone.now(),
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

			for i in polls:
				vote = False
				options = Option.objects.filter(poll_id = i)
				for j in options:
					stud_exist = OptionStudRelation.objects.filter(option_id = j ,stud_id = request.user)
					if stud_exist:
						vote = True
						break
				
				newobj = {
					"poll" : i ,
					"vote" : vote
				}
				context["polls"].append(newobj)

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
	passing_code = request.POST['passingcode']
	class_name = request.POST['classname']
	semester = request.POST['semester']
	year = request.POST['year']
	while True:
		class_code=get_random_string(length=6)
		matched = Class.objects.filter(class_code=class_code)
		if not matched:
			break
	some = Class.objects.create(course_name=class_name,class_password= passing_code , course_code=course_code, year=year, semester=semester,class_code=class_code)
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

		post_object = Post.objects.create(class_id=class_object,posted_by=posted_by,title=title,content=content,time_stamp=time_stamp,is_anonymous=is_anonymous,is_draft=is_draft)
		if request.POST.get('tags_select'):
			tags_fetch = request.POST['tags_select']
			tags_fetch = tags_fetch.split('&')
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
@login_required(login_url = loginURL)
def get_poll(request):
	user_id = request.session.get("id")
	class_code = request.GET['class_code']
	poll_id = request.GET['poll_id']
	poll_present = Poll.objects.filter(class_id__class_code__exact = class_code,id =poll_id)
	if is_class_taken(user_id,class_code) and poll_present:
		data = {}
		poll = Poll.objects.get(id = poll_id)
		data["id"] = poll.id
		data["title"] = poll.title
		data["time_stamp"] = poll.time_stamp.strftime("%b %d, %I:%M %p")
		data["deadline"] = poll.deadline.strftime("%b %d, %I:%M %p")
		data["is_multi"] = poll.check_multiple
		data["attempts"] = poll.attempts
		data["is_ins"] = False
		if (poll.posted_by.id == user_id):
			data["is_ins"] = True
		data["options"] = []
		options_list = Option.objects.filter(poll_id = poll)
		for op in options_list:
			opt_buf = {}
			opt_buf["option_name"] = op.content
			opt_buf["option_id"]= op.id
			opt_buf["option_count"] = op.count
			check_option = OptionStudRelation.objects.filter(option_id = op,stud_id = request.user)
			if check_option:
				opt_buf["checked"] = True
			else:
				opt_buf["checked"] = False
			data["options"].append(opt_buf)
		return HttpResponse(json.dumps(data))
	else:
		return HttpResponse("Failed")

@csrf_exempt
@login_required(login_url = loginURL)
def submit_poll(request):
	user_id = request.session.get("id")
	class_code = request.POST['class_code']
	form_data = request.POST['form_data']
	poll_id = request.POST['poll_id']
	ism = request.POST['multiple_option']
	poll_exist = Poll.objects.filter(id = poll_id,class_id__class_code__exact = class_code)
	if is_class_taken(user_id,class_code) and poll_exist:
		
		check_attempt = OptionStudRelation.objects.filter(stud_id = user_id,option_id__poll_id__id = poll_id)
		if not check_attempt:
			poll_obj = Poll.objects.filter(id = poll_id).first()
			poll_obj.attempts = poll_obj.attempts + 1
			poll_obj.save()
		if ism == "true":
			# print(form_data)
			fields = form_data.split('&')
			powerful = OptionStudRelation.objects.filter(stud_id = user_id,option_id__poll_id__id = poll_id)
			for ia in powerful:
				alh = Option.objects.filter(id = ia.option_id.id).first()
				alh.count = alh.count - 1
				alh.save()
			OptionStudRelation.objects.filter(stud_id = user_id,option_id__poll_id__id = poll_id).delete()
			for vari in fields:
				print(vari)
				# varite = vari.split('=')
				# for opt_id , varw in varite:							
				opt_id , varw = vari.split('=')
				option_object = Option.objects.get(id = opt_id)
				som = OptionStudRelation.objects.create(option_id = option_object,stud_id = request.user)
				option_object.count = option_object.count + 1 	
				option_object.save()

		if ism == "false" :
			group , opt_id = form_data.split('=')
			powerful = OptionStudRelation.objects.filter(stud_id = user_id,option_id__poll_id__id = poll_id)
			for ia in powerful:
				alh = Option.objects.filter(id = ia.option_id.id).first()
				alh.count = alh.count - 1 
				alh.save()
			OptionStudRelation.objects.filter(stud_id = user_id,option_id__poll_id__id = poll_id).delete()
			option_object = Option.objects.get(id = opt_id)
			som = OptionStudRelation.objects.create(option_id = option_object ,stud_id = request.user)
			opt_to_update = Option.objects.filter(id = som.option_id.id).first()
			opt_to_update.count = opt_to_update.count + 1 
			opt_to_update.save()
		return HttpResponse("success")
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
		for topic in topic_post:
			topic_tag = topic.topic_id.name
			data["tags"].append(topic_tag)
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
def inst_settings(request, class_code):
	user_id = request.session.get("id")
	is_ins = ClassInsRelation.objects.filter(
		class_id__class_code__exact=class_code,
		ins_id__id__exact=user_id
	)
	if is_ins:
		filtered = Joins.objects.filter(class_id__class_code__exact=class_code)
		polls_for_class = Poll.objects.filter(class_id__class_code__exact=class_code)
		tags = Topic.objects.filter(class_id__class_code__exact=class_code)
		class_is_active = Class.objects.filter(class_code__exact=class_code)
		class_password = class_is_active[0].class_password
		polls = []
		for i in polls_for_class:
			options_for_poll = Option.objects.filter(poll_id=i.id)
			poll_object = {
				'title': i.title,
				'deadline': i.deadline
			}
			options_array = []
			for j in options_for_poll:
				options_array.append(j)
			poll_object['optionsArray'] = options_array
			polls.append(poll_object)

		if class_is_active[0].is_active:
			context = {"stud_list": [], "class_code": class_code, "is_active": 1, "polls": polls, "class_password": class_password, "tags": tags }
		else:
			context = {"stud_list": [], "class_code": class_code, "is_active": 0, "polls": polls, "class_password": class_password, "tags": tags }
		for i in filtered:
			context["stud_list"].append(i.stud_id)
		return render(request, 'class/settings.html', context)
	else:
		return HttpResponse("You aren't instructor for this class")


@csrf_exempt
@login_required(login_url=loginURL)
def delete_stud_from_class(request):
	user_id = request.session.get("id")
	class_code = request.POST['class_code']
	student_id = request.POST['student_id']
	if user_id == student_id:
		is_student_in_class = Joins.objects.filter(stud_id_id__exact=student_id, class_id__class_code__exact=class_code)
		if is_student_in_class:
			is_student_in_class.delete()
			Post.objects.filter(class_id__class_code__exact=class_code, posted_by_id__exact=student_id).delete()
			Comment.objects.filter(posted_by_id__exact=student_id, post_id__class_id__class_code__exact=class_code).delete()
			data = {"status": "200"}
			return HttpResponse(json.dumps(data))
		else:
			data = {"status": 404}
			return HttpResponse(json.dumps(data))
	else:
		is_ins = ClassInsRelation.objects.filter(ins_id_id__exact=user_id, class_id__class_code__exact=class_code)
		if is_ins:
			is_student_in_class = Joins.objects.filter(stud_id_id__exact=student_id, class_id__class_code__exact=class_code)
			if is_student_in_class:
				is_student_in_class.delete()
				Post.objects.filter(class_id__class_code__exact=class_code,posted_by_id__exact=student_id).delete()
				Comment.objects.filter(posted_by_id__exact=student_id,post_id__class_id__class_code__exact=class_code).delete()
				data = {"status": "200"}
				return HttpResponse(json.dumps(data))
		data = {"status": 404}
		return HttpResponse(json.dumps(data))


@csrf_exempt
@login_required(login_url=loginURL)
def change_class_activity(request):
	user_id = request.session.get("id")
	class_code = request.POST['class_code']
	is_ins = ClassInsRelation.objects.filter(ins_id_id__exact=user_id, class_id__class_code__exact=class_code)
	if is_ins:
		class_object = Class.objects.filter(class_code__exact=class_code)[0]
		class_object.is_active = not class_object.is_active
		class_object.save()
		return HttpResponse(json.dumps({"status": "200"}))
	return HttpResponse(json.dumps({"status": "404"}))


@csrf_exempt
@login_required(login_url=loginURL)
def add_students_to_class(request):
	user_id = request.session.get("id")
	class_code = request.POST['class_code']
	is_csv = request.POST['is_csv']
	is_ins = ClassInsRelation.objects.filter(ins_id_id__exact=user_id, class_id__class_code__exact=class_code)
	if is_ins:
		ins = User.objects.get(id=user_id)
		if is_csv == "1":
			able_to_add = []
			unable_to_add = []
			file_read = TextIOWrapper(request.FILES['students_data'].file, encoding=request.encoding, errors='replace')
			data = csv.reader(file_read)
			for line in data:
				is_student_in_class = Joins.objects.filter(stud_id__email__exact=line[0], class_id__class_code__exact=class_code)
				if (not is_student_in_class) and line[0] != ins.email:
					joins = Joins()
					joins.class_id = Class.objects.filter(class_code__exact=class_code)[0]
					joins.stud_id = User.objects.filter(email__exact=line[0])[0]
					joins.time_stamp = timezone.now()
					joins.save()
					able_to_add.append(line[0])
				else:
					unable_to_add.append(line[0])
			# return HttpResponse(json.dumps({"status": "200", "able_to_add": able_to_add, "unable_to_add": unable_to_add}))
			return redirect('/class/' + class_code + '/settings')
		else:
			stud_email = request.POST['stud_email']
			is_student_in_class = Joins.objects.filter(stud_id__email__exact=stud_email, class_id__class_code__exact=class_code)
			if (not is_student_in_class) and stud_email != ins.email:
				joins = Joins()
				joins.class_id = Class.objects.filter(class_code__exact=class_code)[0]
				joins.stud_id = User.objects.filter(email__exact=stud_email)[0]
				joins.time_stamp = timezone.now()
				joins.save()
				return redirect('/class/'+class_code+'/settings')
			else:
				return HttpResponse(json.dumps({"status": "404"}))
	return HttpResponse(json.dumps({"status": "404", "class_code": class_code, "user_id": user_id}))


@csrf_exempt
@login_required(login_url=loginURL)
def add_poll(request):
	user_id = request.session.get("id")
	class_code = request.POST['class_code']
	is_ins = ClassInsRelation.objects.filter(ins_id_id__exact=user_id, class_id__class_code__exact=class_code)
	if is_ins:
		class_object = Class.objects.filter(class_code__exact=class_code)[0]
		user_object = User.objects.filter(id=user_id)[0]
		title = request.POST['poll_title']
		poll_options = request.POST.getlist('pollOptions[]')
		is_multi = request.POST.get('is_multi', None)
		if is_multi is not None:
			is_multi = True
		else:
			is_multi = False
		deadline_date = request.POST['deadline_date']
		deadline_time = request.POST['deadline_time']
		date_array = list(map(int, deadline_date.split('-')))
		time_array = list(map(int, deadline_time.split(':')))
		poll_deadline = datetime.datetime(
			date_array[0],  # year
			date_array[1],  # month
			date_array[2],  # date
			time_array[0],  # hour
			time_array[1],  # minute
			0,              # seconds
			0,              # micro seconds
			tzinfo=timezone.get_current_timezone()  # timezone
		)
		new_poll = Poll()
		new_poll.class_id = class_object
		new_poll.posted_by = user_object
		new_poll.title = title
		new_poll.check_multiple = is_multi
		new_poll.attempts = 0
		new_poll.time_stamp = timezone.now()
		new_poll.deadline = poll_deadline
		new_poll.save()
		for i in poll_options:
			new_option = Option()
			new_option.poll_id = new_poll
			new_option.content = i
			new_option.count = 0
			new_option.save()
		return HttpResponse(
			json.dumps(
				{
					"status": "200",
					"title": title,
					"poll_options": poll_options,
					"is_multi": is_multi,
					"time": str(poll_deadline)[:-6]
				}
			)
		)
	return HttpResponse(json.dumps({"status": "404"}))


@csrf_exempt
@login_required(login_url=loginURL)
def update_account_password(request):
	user_id = request.session.get("id")
	old_password = request.POST['old_password']
	new_password = request.POST['new_password']
	user = User.objects.filter(id=user_id)[0]
	user_exist = authenticate(username=user.username, password=old_password)
	if user_exist:
		user.set_password(new_password)
		user.save()
		logout(request)
		request.session["name"] = user.first_name + " " + user.last_name
		request.session["id"] = user.id
		login(request, user)
		return HttpResponse(json.dumps({"status": "200"}))
	else:
		return HttpResponse(json.dumps({"status": "404"}))


@csrf_exempt
@login_required(login_url=loginURL)
def add_tag(request):
	user_id = request.session.get("id")
	class_code = request.POST['class_code']
	is_ins = ClassInsRelation.objects.filter(ins_id_id__exact=user_id, class_id__class_code__exact=class_code)
	if is_ins:
		new_tag = request.POST['new_tag']
		is_tag_in_class = Topic.objects.filter(class_id__class_code__exact=class_code, name__exact=new_tag)
		if not is_tag_in_class:
			class_object = Class.objects.filter(class_code__exact=class_code)[0]
			topic = Topic()
			topic.name = new_tag
			topic.class_id = class_object
			topic.save()
			return HttpResponse(json.dumps({"status": "200", "tag": new_tag}))
	return HttpResponse(json.dumps({"status": "404"}))


@csrf_exempt
@login_required(login_url=loginURL)
def stud_drop_course(request):
	user_id = request.session.get("id")
	class_code = request.POST['class_code']
	is_in_class = Joins.objects.filter(class_id__class_code__exact=class_code, stud_id_id__exact=user_id)
	if is_in_class:
		Post.objects.filter(class_id__class_code__exact=class_code, posted_by_id__exact=user_id).delete()
		Comment.objects.filter(posted_by_id__exact=user_id, post_id__class_id__class_code__exact=class_code).delete()
		is_in_class.delete()
		return HttpResponse(json.dumps({"status": "200"}))
	return HttpResponse(json.dumps({"status": "404"}))


def logout_(request):
	logout(request)		# logout flushes the session
	return redirect('class:login_')
