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
from django.utils import timezone
from core.models import Appliance, Area, Notice
from core.views import build_area_status, schedules_for_area_on
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
                "dashboard"
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


@login_required(login_url="login")
def dashboard(request):

    setup = (
        SavedSetup.objects
        .filter(user=request.user)
        .prefetch_related("items__appliance")
        .first()
    )

    setup_items = []
    total_watt = 0

    if setup:

        setup_items = setup.items.all()

        for item in setup_items:

            watt = (
                item.custom_watt
                or item.appliance.watt
            )

            total_watt += (
                watt *
                item.quantity
            )

    notices = (
        Notice.objects
        .all()
        .order_by("-created_at")[:3]
    )

    saved_areas = (
        SavedArea.objects
        .filter(user=request.user)
        .select_related("area")
        .order_by("-is_primary", "label")
    )

    area_statuses = [
        {
            "saved_area": saved_area,
            **build_area_status(saved_area.area)
        }
        for saved_area in saved_areas
    ]

    upcoming_by_area = []

    for saved_area in saved_areas:
        upcoming_by_area.append({
            "saved_area": saved_area,
            "schedules": schedules_for_area_on(
                saved_area.area_id,
                timezone.localdate()
            )[:3],
        })

    context = {
        "setup": setup,
        "setup_items": setup_items,
        "total_watt": total_watt,
        "capacity_percent": min(
            100,
            round((total_watt / setup.ips_capacity) * 100)
        ) if setup and setup.ips_capacity else 0,
        "notice_count": Notice.objects.count(),
        "notices": notices,
        "saved_areas": saved_areas,
        "area_statuses": area_statuses,
        "upcoming_by_area": upcoming_by_area,
        "areas": Area.objects.all().order_by(
            "district",
            "upazila",
            "area_name"
        ),
    }

    return render(
        request,
        "dashboard.html",
        context
    )


@login_required(login_url="login")
def profile(request):

    user_profile = (
        UserProfile.objects
        .filter(user=request.user)
        .select_related("area")
        .first()
    )

    setup = (
        SavedSetup.objects
        .filter(user=request.user)
        .prefetch_related("items__appliance")
        .first()
    )

    setup_items = (
        setup.items.all()
        if setup
        else []
    )

    context = {
        "user_profile": user_profile,
        "setup": setup,
        "setup_items": setup_items,
        "saved_areas": SavedArea.objects.filter(
            user=request.user
        ).select_related("area"),
        "areas": Area.objects.all().order_by(
            "district",
            "upazila",
            "area_name"
        ),
    }

    return render(
        request,
        "profile.html",
        context
    )

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


@login_required(login_url="login")
def save_area(request):
    if request.method == "POST":
        area_id = request.POST.get("area")
        label = request.POST.get("label", "Home").strip() or "Home"

        if not area_id:
            messages.error(request, "Please choose an area.")
            return redirect("dashboard")

        saved_area, created = SavedArea.objects.get_or_create(
            user=request.user,
            area_id=area_id,
            label=label,
            defaults={
                "email_alerts":
                request.POST.get("email_alerts") == "on",
                "alert_minutes_before":
                int(request.POST.get("alert_minutes_before") or 30),
                "is_primary":
                not SavedArea.objects.filter(
                    user=request.user
                ).exists(),
            }
        )

        if not created:
            saved_area.email_alerts = (
                request.POST.get("email_alerts") == "on"
            )
            saved_area.alert_minutes_before = int(
                request.POST.get("alert_minutes_before") or 30
            )
            saved_area.save()

        profile, _ = UserProfile.objects.get_or_create(
            user=request.user
        )

        if saved_area.is_primary or not profile.area:
            profile.area = saved_area.area
            profile.save()

        messages.success(request, "Area preferences saved.")

    return redirect(request.POST.get("next") or "dashboard")


@login_required(login_url="login")
def delete_area(request, saved_area_id):
    if request.method == "POST":
        SavedArea.objects.filter(
            id=saved_area_id,
            user=request.user
        ).delete()
        messages.success(request, "Saved area removed.")

    return redirect(request.POST.get("next") or "dashboard")
