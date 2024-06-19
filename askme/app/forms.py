from django import forms
from django.contrib.auth.models import User
from app.models import Profile
from app.models import Answer
from app.models import Question
from app.models import QuestionLike
from app.models import AnswerLike
from app.models import Tag
import re


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


class SettingsForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    avatar = forms.ImageField(required=False)
    current_user = User()

    def __init__(self, user, *args, **kwargs):
        self.current_user = user
        super(SettingsForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        self.current_user.username = self.cleaned_data['username']
        self.current_user.email = self.cleaned_data['email']
        self.avatar = self.cleaned_data.get('avatar')
        if self.avatar:
            if self.current_user.profile.avatar != self.cleaned_data['avatar']:
                self.current_user.profile.avatar = self.cleaned_data['avatar']
        user = self.current_user
        user.profile.save()
        user.save()
        print(user.profile.avatar)
        return user

    def clean(self):
        cleaned_data = super().clean()
        profiles = User.objects.filter(username=cleaned_data['username'])
        if profiles and profiles[0].username != self.current_user.username:
            self.add_error(field=None, error="This username is already taken")
        profiles = User.objects.filter(email=cleaned_data['email'])
        if profiles and profiles[0].email != self.current_user.email:
            self.add_error(field=None, error="This email is already taken")


class AskForm(forms.ModelForm):
    tags = forms.CharField(required=False)

    class Meta:
        model = Question
        fields = ['title', 'content']

    def __init__(self, user, *args, **kwargs):
        self.current_user = user
        super(AskForm, self).__init__(*args, **kwargs)

    def clean(self):
        tags = self.cleaned_data.get('tags')
        #pattern = r'^[a-zA-Z]+$'
        #if not re.match(pattern, tags):
        #    self.add_error(field=None, error="In tags you can you only letters")
        tags = tags.split()
        if len(tags) > 3:
            self.add_error(field=None, error="You can't write more than 3 tags")

    def save(self, commit=True):
        tags = self.cleaned_data.get('tags')
        tags = tags.split()
        question = super().save(commit=False)
        question.author = self.current_user
        question.save()
        tags = set(tags)
        for tag in tags:
            tag, created = Tag.objects.get_or_create(name=tag)
            question.tags.add(tag)
        question.save()
        self.current_user.profile.save()
        return question


class RegistrationForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField()
    confirm_password = forms.CharField()
    avatar = forms.ImageField()
    profile = Profile()

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'avatar']

    def clean(self):
        cleaned_data = super().clean()
        profiles = User.objects.filter(username=cleaned_data['username'])
        if profiles:
            self.add_error(field=None, error="This username is already taken")
        profiles = User.objects.filter(email=cleaned_data['email'])
        if profiles:
            self.add_error(field=None, error="This email is already taken")
        if cleaned_data['password'] != cleaned_data['confirm_password']:
            self.add_error(field=None, error="Password don't match!")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        profile = Profile(user=user)
        profile.avatar = self.cleaned_data['avatar'];
        user.save()
        profile.save()
        return user


class AnswerForm(forms.ModelForm):
    content = forms.CharField()
    user = User()
    question = Question()

    class Meta:
        model = Answer
        fields = ['content']

    def __init__(self, user, question, *args, **kwargs):
        self.user = user
        self.question = question
        super(AnswerForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        answer = super().save(commit=False)
        answer.author = self.user
        answer.question = self.question
        answer.save()
        return answer


class CorrectForm(forms.Form):
    answer_id = forms.IntegerField()

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(CorrectForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        answer = Answer.objects.filter(id=cleaned_data['answer_id'])
        if not answer:
            self.add_error(field=None, error="Answer is not found")
        if answer[0].question.author != self.user:
            self.add_error(field=None, error="You do not have permission to do it")

    def save(self, commit=True):
        answer = Answer.objects.get(id=self.cleaned_data['answer_id'])
        answer.is_correct = not answer.is_correct
        answer.save()
        return answer.is_correct


class VoteForm(forms.Form):
    ACTIONS = (
        ('Like', 'l'),
        ('Dislike', 'd'),
    )

    TYPE = (
        ('question', 'question'),
        ('answer', 'answer'),
    )

    action = forms.ChoiceField(choices=ACTIONS)
    type = forms.ChoiceField(choices=TYPE)
    itemId = forms.IntegerField()

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        action = self.cleaned_data['action']
        type = self.cleaned_data['type']
        itemId = self.cleaned_data['itemId']

        if type == 'question':
            question = Question.objects.get(id=itemId)
            vote = QuestionLike.objects.filter(user=self.user, question_id=itemId).first()
            if vote:
                if vote.value == action[0].lower():
                    vote.delete()
                else:
                    vote.value = action[0].lower()
                    vote.save()
            else:
                vote = QuestionLike(
                    user=self.user,
                    question_id=itemId,
                    value=action[0].lower()
                )
                vote.save()
            likes = QuestionLike.objects.filter(question__id=itemId, value='l').count()
            dislikes = QuestionLike.objects.filter(question_id=itemId, value='d').count()
            rating = likes - dislikes
            question.rating = rating
            question.save()
            return rating
        else:
            answer = Answer.objects.get(id=itemId)
            vote = AnswerLike.objects.filter(user=self.user, answer_id=itemId).first()
            if vote:
                if vote.value == action[0].lower():
                    vote.delete()
                else:
                    vote.value = action[0].lower()
                    vote.save()
            else:
                vote = AnswerLike(
                    user=self.user,
                    answer_id=itemId,
                    value=action[0].lower()
                )
                vote.save()
            likes = AnswerLike.objects.filter(answer_id=itemId, value='l').count()
            dislikes = AnswerLike.objects.filter(answer_id=itemId, value='d').count()
            rating = likes - dislikes
            answer.rating = rating
            answer.save()
            return rating

