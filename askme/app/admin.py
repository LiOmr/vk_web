from django.contrib import admin
from app.models import *

admin.site.register(Profile)
admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(QuestionLike)
admin.site.register(AnswerLike)

# Register your models here.
