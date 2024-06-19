from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count
import time


class TagManager(models.Manager):
    def get_hot_tags(self):
        return self.annotate(num_questions=Count('question')).order_by('-num_questions')[:10]


class Tag(models.Model):
    name = models.CharField(max_length=255)
    rating = models.IntegerField(default=0)
    objects = TagManager()

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def get_hot_questions(self):
        return self.order_by('-rating')

    def get_new_questions(self):
        return self.order_by('-pub_date')

    def get_questions_by_tag(self, tag):
        return self.filter(tags__name=tag)


class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, limit_choices_to={'tags__lt': 4})
    rating = models.IntegerField(default=0)
    objects = QuestionManager()

    def __str__(self):
        return self.title

    def get_rating(self):
        likes = self.objects.questionlike_set
        result = 0
        for like in likes:
            if like.value == 'l':
                result += 1
            else:
                result -= 1
        return result


class AnswerManager(models.Manager):
    def get_hot_answers(self):
        return self.order_by('-is_correct', '-rating')

    def get_new_answers(self):
        return self.order_by('-pub_date')

    def get_answers_by_question_id(self, question_id):
        return self.filter(question_id=question_id).order_by('-pub_date')


class Answer(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    objects = AnswerManager()

    def __str__(self):
        return f"{self.author} {self.question}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    avatar = models.ImageField(null=True, blank=True, upload_to='', default='static/img/avatar.png')
    objects = models.Manager()

    def __str__(self):
        return self.user


class QuestionLike(models.Model):
    VALUE_CHOICES = [("l", "Like"), ("d", "Dislike")]
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.CharField(choices=VALUE_CHOICES, max_length=10)
    objects = models.Manager()

    class Meta:
        unique_together = [('question', 'user')]

    def __str__(self):
        return self.question.__str__()


class AnswerLike(models.Model):
    VALUE_CHOICES = [("l", "Like"), ("d", "Dislike")]
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.CharField(choices=VALUE_CHOICES, max_length=10)
    objects = models.Manager()

    class Meta:
        unique_together = [('answer', 'user')]

    def __str__(self):
        return self.answer.__str__()


