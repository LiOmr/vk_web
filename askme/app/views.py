from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect

from app.models import *
from app import forms
import json

PER_PAGE = 20
PER_PAGE_ANSWERS = 5

# Create your views here.


def pagination(request, data, per_page, answerId=None):
    paginator = Paginator(data, per_page)
    page_num = request.GET.get('page', 1)
    if answerId is not None:
        ans = Answer.objects.get(id=answerId)
        print("here")
        for i in paginator.page_range:
            if ans in paginator.page(i).object_list:
                page_num = i
                print(page_num)
                break
    page_obj = paginator.get_page(page_num)
    return page_obj


def index(request):
    best_users = User.objects.all()[:5]
    popular_tags = Tag.objects.get_hot_tags()
    page_obj = pagination(request, Question.objects.get_new_questions(), PER_PAGE)
    return render(request, "index.html", {'questions': page_obj, 'popular_tags': popular_tags, 'members': best_users})


def hot(request):
    best_users = User.objects.all()[:5]
    popular_tags = Tag.objects.get_hot_tags()
    page_obj = pagination(request, Question.objects.get_hot_questions(), PER_PAGE)
    return render(request, "hot.html", {'questions': page_obj, 'popular_tags': popular_tags, 'members': best_users})


def question(request, question_id):
    best_users = User.objects.all()[:5]
    popular_tags = Tag.objects.get_hot_tags()
    item = get_object_or_404(Question, pk=question_id)

    if request.method == 'POST':
        form = forms.AnswerForm(request.user, item, request.POST)
        if form.is_valid():
            answer = form.save()
            page_num = request.GET.get('page', 1)
            return HttpResponseRedirect(f"/questions/{question_id}/?page={page_num}#{answer.id}")

    page_obj = pagination(request, item.answer_set.get_hot_answers(), PER_PAGE_ANSWERS)
    return render(request, "question.html", {'question': item, 'answers': page_obj, 'popular_tags': popular_tags, 'members': best_users})


def tag(request, tag_name):
    best_users = User.objects.all()[:5]
    tag = get_object_or_404(Tag, name=tag_name)
    popular_tags = Tag.objects.get_hot_tags()
    page_obj = pagination(request, Question.objects.get_questions_by_tag(tag_name), PER_PAGE)
    return render(request, "tag.html", {'questions': page_obj, 'tag_name': tag_name, 'popular_tags': popular_tags, 'members': best_users})


@require_http_methods(['GET', 'POST'])
def log_in(request):
    form = forms.LoginForm()
    if request.method == 'POST':
        form = forms.LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(request, **form.cleaned_data)
            if user:
                login(request, user)
                return redirect('index')
            else:
                form.add_error(field=None, error='Invalid username or password')
    return render(request, "login.html", {"form": form})


def log_out(request):
    logout(request)
    return redirect('index')


@require_http_methods(['GET', 'POST'])
def settings(request):
    form = forms.SettingsForm(request.user)
    if request.method == 'POST':
        form = forms.SettingsForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            print("valid")
            user = form.save()
            if not user:
                form.add_error(field=None, error='Some problems with saving')
        else:
            print("not valid")
    return render(request, "settings.html", {"form": form})


@require_http_methods(['GET', 'POST'])
def signup(request):
    print(request.POST)
    form = forms.RegistrationForm()
    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST, request.FILES)
        print(form.non_field_errors())
        if form.is_valid():
            print("im here")
            user = form.save()
            if user:
                print("im here2")
                login(request, user)
                return redirect('index')
            else:
                form.add_error(field=None, error='Some problems with saving')
    return render(request, "signup.html", {"form": form})


def ask(request):
    best_users = User.objects.all()[:5]
    popular_tags = Tag.objects.get_hot_tags()
    form = forms.AskForm(request.user)
    print(request.POST)
    if request.method == 'POST':
        print("POST")
        form = forms.AskForm(request.user, request.POST)
        print(form.errors)
        if form.is_valid():
            print("Valid")
            question = form.save()
            if question:
                print("Hey")
                return redirect('question', question_id=question.id)
    return render(request, "ask.html", {"form": form, 'popular_tags': popular_tags, 'members': best_users})


@require_http_methods(['POST'])
def vote(request):
    body = json.loads(request.body)
    print(body)
    form = forms.VoteForm(request.user, body)
    if form.is_valid():
        rating = form.save()
        body['rating'] = rating
        return JsonResponse(body)
    print(form.errors)
    return JsonResponse({'errors': form.errors}, status=422)


@require_http_methods(['POST'])
def correct(request):
    body = json.loads(request.body)
    print(request)
    form = forms.CorrectForm(request.user, body)
    if form.is_valid():
        print("valid")
        correct = form.save()
        body['is_correct'] = correct
        return JsonResponse(body)
    print(form.errors)
    return JsonResponse({'errors': form.errors}, status=422)


def page_404(request, *args, **argv):
    return render(request, "404.html", status=404)
