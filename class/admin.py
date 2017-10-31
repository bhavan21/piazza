from django.contrib import admin

# UserName : admin
# Password : fordis1234

from .models import Class
from .models import ClassInsRelation
from .models import Joins
from .models import Topic
from .models import Post
from .models import ViewRelation
from .models import PinRelation
from .models import TopicPostRelation
from .models import Comment
from .models import Poll
from .models import Option
from .models import OptionStudRelation

admin.site.register(Class)
admin.site.register(ClassInsRelation)
admin.site.register(Joins)
admin.site.register(Topic)
admin.site.register(Post)
admin.site.register(ViewRelation)
admin.site.register(PinRelation)
admin.site.register(TopicPostRelation)
admin.site.register(Comment)
admin.site.register(Poll)
admin.site.register(Option)
admin.site.register(OptionStudRelation)