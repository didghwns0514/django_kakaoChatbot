from django.http import HttpResponse
from django.contrib import auth
from django.contrib.auth import authenticate

from .models import UserManager, User
from django.shortcuts import render, redirect

from datetime import datetime
import logging
logger = logging.getLogger('my')

# Create your views here.
def index(request):
    return HttpResponse("안녕하세요! 회원가입 페이지에 오신것을 환영합니다!")

def index_check(request):

    return render(request, 'appStockAccount/SignUp.html')

# 회원가입
def signup(request):
    if request.method == 'POST':

        #tmpQuery = UserManager.filter(user_id=request.POST['id'])
        tmpQuery = User.objects.filter(name__exact=request.POST['id'])
        print(f"request.POST['password1'] : {request.POST['password1']}")
        print(f"request.POST['password2'] : {request.POST['password2']}")
        if request.POST['password1'] == request.POST['password2']:
            if not tmpQuery.exists():
                userManager = UserManager()
                user = userManager.create_user(
                                        user_id=request.POST['id'],
                                        password=request.POST['password1'],
                                        email=request.POST['email'],

                )
                auth.login(request, user)
                return redirect('/')
            else:
                return redirect('/accounts')
        else:
            if not tmpQuery.exists():
                return render(request, 'appStockAccount/SignUp.html')
            else:
                return render(request, 'appStockAccount/SignIn.html')
    return render(request, 'appStockAccount/SignUp.html')

# 로그인
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, user_id=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('board')
        else:
            return render(request, 'login.html', {'error': 'username or password is incorrect.'})
    else:
        return render(request, 'login.html')


# 로그아웃
def logout(request):
    auth.logout(request)
    return redirect('home')

# home
def home(request):
    return render(request, 'home.html')