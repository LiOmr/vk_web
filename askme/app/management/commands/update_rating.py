from django.core.management.base import BaseCommand
from app.models import *


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        questionLikes = QuestionLike.objects.all()
        for ql in questionLikes:
            if ql.value == 'l':
                ql.question.rating += 1
            else:
                ql.question.rating -= 1
            ql.question.save()
            print(ql.question)
            print(ql.question.rating)
        answerLikes = AnswerLike.objects.all()
        for al in answerLikes:
            if al.value == 'l':
                al.answer.rating += 1
            else:
                al.answer.rating -= 1
            al.answer.save()
