from django.shortcuts import (render,redirect)
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate,
    login
)
from django.contrib.auth import logout
from django.contrib import messages
from .models import *

def signup(request):
    if request.method=="POST":
        full_name=request.POST.get("full_name")
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        confirm_password = request.POST.get(
            "confirm_password"
        )
        #validation

        if password!=confirm_password:
            messages.error(
                request,"Passwords do not match."
            )
            return redirect ("signup")
        if User.objects.filter(
            username=username
        ).exists():
            messages.error(
                request,"Username already exists."
            )
            return redirect("signup")
        if User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                "Email already exists."
            )

            return redirect(
                "signup"
            )
        #db te obj create
        user=User.objects.create_user(
            username=username,
            email=email,
            password=password
          )
        user.first_name = full_name
        user.save()

        UserProfile.objects.create(user=user)
        messages.success(
            request,
            "Account created successfully!"
        )

        return redirect(
            "login"
        )
    
    return render(
        request,
        'signup.html'
    )


def login_view(request):
    if request.method=='POST':
        username=request.POST.get("username")
        password=request.POST.get("password")
        user=authenticate(
            request,
            username=username,
            password=password
        )
        if user is not None:
            login(
                request,user
            )
            messages.success(
                request,
                "Login successful!"
            )

            return redirect(
                "home"
            )
        else:

            messages.error(
                request,
                "Invalid username or password."
            )

            return redirect(
                "login"
            )

    return render(
        request,
        "login.html")

def logout_view(request):

    logout(request)

    messages.success(
        request,
        "Logged out successfully."
    )

    return redirect(
        "login"
    )