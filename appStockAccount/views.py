from django.http import HttpResponse
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

# Create your views here.
def index(request):
    return HttpResponse("안녕하세요! 회원가입 페이지에 오신것을 환영합니다!")

def index_check(request):

    return render(request, 'appStockAccount/SignUp.html')

# 회원가입
def signup(request):
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            user = User.objects.create_user(
                                            username=request.POST['username'],
                                            password=request.POST['password1'],
                                            email=request.POST['email'],)
            auth.login(request, user)
            return redirect('/')
        return render(request, 'appStockAccount/SignUp.html')
    return render(request, 'appStockAccount/SignUp.html')