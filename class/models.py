from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Class(models.Model):
	course_name = models.CharField(max_length=100)
	course_code = models.CharField(max_length=10)
	year = models.CharField(max_length=4)
	semester = models.CharField(max_length=10)
	class_code = models.CharField(max_length=6, unique=True)
	class_password = models.CharField(max_length=50)
	is_active = models.BooleanField(default=1)


class ClassInsRelation(models.Model):
	class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
	ins_id = models.ForeignKey(User, on_delete=models.CASCADE)
	time_stamp = models.DateTimeField()


# students
class Joins(models.Model):
	class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
	stud_id = models.ForeignKey(User, on_delete=models.CASCADE)
	time_stamp = models.DateTimeField()


class Topic(models.Model):
	name = models.CharField(max_length=50)
	class_id = models.ForeignKey(Class, on_delete=models.CASCADE)

	class Meta:
		unique_together = ('name', 'class_id',)


class Post(models.Model):
	class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
	posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=50)
	content = models.TextField()
	is_draft = models.BooleanField(default=True)
	is_anonymous=models.BooleanField(default=False)
	views = models.IntegerField(default=0)
	sched_time = models.DateTimeField(null=True)
	time_stamp = models.DateTimeField()


class ViewRelation(models.Model):
	user_id = models.ForeignKey(User, on_delete=models.CASCADE)
	post_id = models.ForeignKey(Post, on_delete=models.CASCADE)


class PinRelation(models.Model):
	user_id = models.ForeignKey(User, on_delete=models.CASCADE)
	post_id = models.ForeignKey(Post, on_delete=models.CASCADE)


class TopicPostRelation(models.Model):
	topic_id = models.ForeignKey(Topic, on_delete=models.CASCADE)
	post_id = models.ForeignKey(Post, on_delete=models.CASCADE)


class Comment(models.Model):
	post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
	posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
	content = models.TextField()
	time_stamp = models.DateTimeField()
	is_anonymous=models.BooleanField(default=False)

class Poll(models.Model):
	class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
	posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.TextField()
	check_multiple = models.BooleanField()
	attempts = models.IntegerField(default=0)
	deadline = models.DateTimeField()
	time_stamp = models.DateTimeField()


class Option(models.Model):
	poll_id = models.ForeignKey(Poll, on_delete=models.CASCADE)
	content = models.CharField(max_length=200)
	count = models.IntegerField(default=0)


class OptionStudRelation(models.Model):
	option_id =  models.ForeignKey(Option, on_delete=models.CASCADE)
	stud_id = models.ForeignKey(User, on_delete=models.CASCADE)
