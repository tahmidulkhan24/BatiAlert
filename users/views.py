from django.shortcuts import (render,redirect)
from django.contrib.auth.models import User
from django.contrib.auth import (
    authenticate,
    login
)
from django.contrib.auth import logout
from django.contrib import messages
from .models import *
from django.contrib.auth.decorators import login_required
from core.models import Appliance
from django.http import JsonResponse


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


@login_required
def save_setup(request):

    if request.method != "POST":

        return redirect(
            "home"
        )

    ips_capacity = request.POST.get(
        "ips_capacity"
    )

    if not ips_capacity:

        messages.error(
            request,
            "Please enter IPS Capacity."
        )

        return redirect(
            "home"
        )

    setup, created = (
        SavedSetup.objects.get_or_create(
            user=request.user,
            defaults={
                "ips_capacity":
                ips_capacity
            }
        )
    )

    setup.ips_capacity = ips_capacity
    setup.save()

    setup.items.all().delete()

    appliances = request.POST.getlist(
        "appliance[]"
    )

    quantities = request.POST.getlist(
        "quantity[]"
    )

    watts = request.POST.getlist(
        "custom_watt[]"
    )

    priorities = request.POST.getlist(
        "priority[]"
    )

    for appliance_id, qty, watt, priority in zip(
        appliances,
        quantities,
        watts,
        priorities
    ):

        if not appliance_id:
            continue

        SetupAppliance.objects.create(

            setup=setup,

            appliance_id=int(
                appliance_id
            ),

            quantity=int(
                qty or 1
            ),

            custom_watt=(
                int(watt)
                if watt
                else None
            ),

            priority=int(
                priority
            )

        )

    messages.success(
        request,
        "Setup saved successfully!"
    )

    return redirect(
        "home"
    )

@login_required
def get_saved_setup(request):

    try:

        setup = SavedSetup.objects.get(
            user=request.user
        )

        appliances = []

        for item in setup.items.all():

            appliances.append({

                "appliance_id":
                item.appliance.id,

                "quantity":
                item.quantity,

                "custom_watt":
                item.custom_watt,

                "priority":
                item.priority

            })

        return JsonResponse({

            "success": True,

            "ips_capacity":
            setup.ips_capacity,

            "appliances":
            appliances

        })

    except SavedSetup.DoesNotExist:

        return JsonResponse({

            "success": False

        })