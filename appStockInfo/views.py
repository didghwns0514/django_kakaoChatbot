from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse # kkotalk api
from django.views.decorators.csrf import csrf_exempt # block CSRF attacks
from django.views.decorators.csrf import ensure_csrf_cookie # https://stackoverflow.com/questions/19598993/csrf-cookie-not-set-django-verification-failed
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

import json

# Create your views here.
def index(request):
    return HttpResponse('Hello! welcome!')