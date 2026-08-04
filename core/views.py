from django.shortcuts import render
from .models import Notice
from django.http import JsonResponse
from .models import *
from datetime import date, timedelta, datetime
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from users.models import SavedSetup, SetupAppliance, UserProfile
from django.contrib import messages

def notice_view(request):
    notices = Notice.objects.all().order_by('-created_at')
    return render(request, 'notice.html', {'notices': notices})

def home(request):
    return render(request, 'home.html')
    notices = Notice.objects.all().order_by('-created_at') 
    return render(request, 'notice.html', {'notices': notices})

def schedule(request):

    districts = (
        Area.objects
        .values_list(
            'district',
            flat=True
        )
        .distinct()
    )

    selected_district = request.GET.get(
        'district'
    )

    selected_upazila = request.GET.get(
        'upazila'
    )

    selected_area = request.GET.get(
        'area'
    )

    upazilas = []

    areas = []

    today_schedules = []

    tomorrow_schedules = []

    weekly_rows = []

    next_outage = None

    countdown = None

    today = date.today()

    tomorrow = (
        today +
        timedelta(days=1)
    )
    #aita diye time theke ajker day ber kore
    today_day = (
        today.strftime("%A")
    )

    tomorrow_day = (
        tomorrow.strftime("%A")
    )

    if selected_district:

        upazilas = (
            Area.objects.filter(
                district=selected_district
            )
            .values_list(
                'upazila',
                flat=True
            )
            .distinct()
        )

    if (
        selected_district and
        selected_upazila
    ):

        areas = (
            Area.objects.filter(
                district=selected_district,
                upazila=selected_upazila
            )
        )

    if selected_area:

        # TODAY

        today_schedules = (
            Schedule.objects.filter(
                area_id=selected_area
            ).filter(

                Q(
                    schedule_type='Daily'
                )

                |

                Q(
                    schedule_type='Weekly',
                    day_of_week=today_day
                )

            )
        )

        # TOMORROW

        tomorrow_schedules = (
            Schedule.objects.filter(
                area_id=selected_area
            ).filter(

                Q(
                    schedule_type='Daily'
                )

                |

                Q(
                    schedule_type='Weekly',
                    day_of_week=tomorrow_day
                )

            )
        )

        # WEEKLY CARD

        weekly_schedules = (
            Schedule.objects.filter(
                area_id=selected_area,
                schedule_type='Weekly'
            )
        )

        for schedule in weekly_schedules:

            weekly_rows.append({

                'day':
                schedule.day_of_week,

                'start_time':
                schedule.start_time,

                'end_time':
                schedule.end_time,

            })

        

        now = datetime.now()

        current_time = now.time()

        for schedule in today_schedules:

            if schedule.start_time > current_time:

                next_outage = schedule

                break
        if next_outage:

            outage_datetime = datetime.combine(
                today,
                next_outage.start_time
            )

            diff = (
                outage_datetime - now
            )

            total_seconds = int(
                diff.total_seconds()
            )

            hours = (
                total_seconds // 3600
            )

            minutes = (
                total_seconds % 3600
            ) // 60

            countdown = (
                f"{hours}h {minutes}m"
            )

    context = {

        'districts':
        districts,

        'upazilas':
        upazilas,

        'areas':
        areas,

        'selected_district':
        selected_district,

        'selected_upazila':
        selected_upazila,

        'selected_area':
        selected_area,

        'today_schedules':
        today_schedules,

        'tomorrow_schedules':
        tomorrow_schedules,

        'weekly_rows':
        weekly_rows,

        'next_outage':
        next_outage,

        'countdown':
        countdown,

    }

    return render(
        request,
        'schedule.html',
        context
    )

def get_upazilas(request):

    district = request.GET.get(
        'district'
    )

    upazilas = list(

        Area.objects.filter(
            district=district
        )
        .values_list(
            'upazila',
            flat=True
        )
        .distinct()

    )

    return JsonResponse(
        {
            'upazilas': upazilas
        }
    )


def get_areas(request):

    district = request.GET.get(
        'district'
    )

    upazila = request.GET.get(
        'upazila'
    )

    areas = list(

        Area.objects.filter(
            district=district,
            upazila=upazila
        ).values(
            'id',
            'area_name'
        )

    )

    return JsonResponse(
        {
            'areas': areas
        }
    )
@login_required
def calculator(request):

    # ==========================
    # USER DATA
    # ==========================

    saved_setup = SavedSetup.objects.filter(
        user=request.user
    ).first()

    profile = UserProfile.objects.filter(
        user=request.user
    ).first()

    appliances = []

    if saved_setup:
        appliances = (
            SetupAppliance.objects
            .filter(setup=saved_setup)
            .select_related("appliance")
        )

    districts = (
        Area.objects
        .values_list("district", flat=True)
        .distinct()
        .order_by("district")
    )

    appliances_list = (
        Appliance.objects
        .all()
        .order_by("name")
    )

    result = None

    # ==========================
    # POST
    # ==========================

    if request.method == "POST":

        mode = request.POST.get("mode", "saved")

        total_load = 0
        total_appliance = 0
        recommendations = []
        schedule = None
        battery_percent = 0
        battery_message = ""

        def safe_int(value, default=0):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        if mode == "saved":

            if not saved_setup:
                # no saved setup exists - just skip silently, don't crash
                voltage = 12
                battery_ah = 0
                rows = []
                area = None
            else:

                voltage = safe_int(
                    request.POST.get("battery_voltage"), 12
                )

                battery_ah = safe_int(
                    request.POST.get("battery_capacity"), 0
                )

                rows = (
                    SetupAppliance.objects
                    .filter(setup=saved_setup)
                    .select_related("appliance")
                )

                area = Area.objects.filter(
                    id=request.POST.get("area_saved")
                ).first()

            if not saved_setup:
                messages.error(
                    request,
                    "You don't have a saved IPS setup yet."
                )
                return render(
                    request,
                    "calculator.html",
                    {
                        "saved_setup": saved_setup,
                        "profile": profile,
                        "appliances": appliances,
                        "districts": districts,
                        "appliances_list": appliances_list,
                        "result": None,
                    }
                )

            voltage = safe_int(
                request.POST.get("battery_voltage"), 12
            )

            battery_ah = safe_int(
                request.POST.get("battery_capacity"), 0
            )

            rows = (
                SetupAppliance.objects
                .filter(setup=saved_setup)
                .select_related("appliance")
            )

            # Area now comes from user input (saved section dropdown)
            area = Area.objects.filter(
                id=request.POST.get("area_saved")
            ).first()

        else:

            voltage = safe_int(
                request.POST.get("battery_voltage_temp"), 12
            )

            battery_ah = safe_int(
                request.POST.get("battery_capacity_temp"), 0
            )

            area = Area.objects.filter(
                id=request.POST.get("area")
            ).first()

            rows = []

            appliance_ids = request.POST.getlist("appliance[]")
            quantities = request.POST.getlist("quantity[]")
            priorities = request.POST.getlist("priority[]")

            for appliance_id, quantity, priority in zip(
                appliance_ids, quantities, priorities
            ):
                appliance_obj = Appliance.objects.filter(
                    id=appliance_id
                ).first()

                if not appliance_obj:
                    continue

                rows.append({
                    "appliance": appliance_obj,
                    "quantity": safe_int(quantity, 1),
                    "priority": safe_int(priority, 2),
                })

        # ==========================
        # LOAD
        # ==========================

        for row in rows:

            if mode == "saved":
                appliance = row.appliance
                quantity = row.quantity
                priority = row.priority
            else:
                appliance = row["appliance"]
                quantity = row["quantity"]
                priority = row["priority"]

            total_appliance += quantity
            total_load += appliance.watt * quantity

            if priority == 3:
                recommendations.append(appliance.name)

        usable_power = voltage * battery_ah * 0.85

        if total_load > 0:
            backup_time = round(usable_power / total_load, 2)
        else:
            backup_time = 0

        # ==========================
        # TODAY'S SCHEDULE
        # ==========================

        if area:
            today = date.today()
            today_day = today.strftime("%A")

            schedule = (
                Schedule.objects.filter(area=area)
                .filter(
                    Q(schedule_type="Daily")
                    |
                    Q(schedule_type="Weekly", day_of_week=today_day)
                )
                .order_by("start_time")
                .first()
            )

        # ==========================
        # BATTERY STATUS
        # ==========================

        if backup_time >= 5:
            status = "READY"
            battery_message = "Enough battery for today's scheduled outage."
        elif backup_time >= 3:
            status = "Needs Optimization"
            battery_message = "Battery is enough but optimization is recommended."
        else:
            status = "Backup Not Enough"
            battery_message = "Battery backup is not enough for today's outage."

        battery_percent = min(100, round((backup_time / 8) * 100))

        # ==========================
        # RECOMMENDATION
        # ==========================

        recommendation_text = []

        for appliance_name in recommendations:
            recommendation_text.append(f"Turn OFF {appliance_name}")

        if len(recommendation_text) == 0:
            recommendation_text.append("Your current setup is already optimized.")

        # ==========================
        # DURATION
        # ==========================

        duration = "--"

        if schedule:
            start = datetime.combine(date.today(), schedule.start_time)
            end = datetime.combine(date.today(), schedule.end_time)
            diff = end - start

            total_minutes = diff.seconds // 60
            hours = total_minutes // 60
            minutes = total_minutes % 60

            if hours > 0 and minutes > 0:
                duration = f"{hours}h {minutes}m"
            elif hours > 0:
                duration = f"{hours} Hours"
            else:
                duration = f"{minutes} Minutes"

        # ==========================
        # RESULT
        # ==========================

        result = {
            "schedule": {
                "area": area.area_name if area else "--",
                "start_time": schedule.start_time if schedule else "--",
                "end_time": schedule.end_time if schedule else "--",
                "duration": duration,
            },
            "total_load": total_load,
            "backup_time": backup_time,
            "status": status,
            "battery_percent": battery_percent,
            "battery_message": battery_message,
            "recommendation": recommendation_text,
            "total_appliance": total_appliance,
            "battery_capacity": battery_ah,
        }

    # ==========================
    # CONTEXT
    # ==========================

    context = {
        "saved_setup": saved_setup,
        "profile": profile,
        "appliances": appliances,
        "districts": districts,
        "appliances_list": appliances_list,
        "result": result,
    }

    return render(request, "calculator.html", context)

    # ==========================
    # USER DATA
    # ==========================

    saved_setup = SavedSetup.objects.filter(
        user=request.user
    ).first()

    profile = UserProfile.objects.filter(
        user=request.user
    ).first()

    appliances = []

    if saved_setup:
        appliances = (
            SetupAppliance.objects
            .filter(setup=saved_setup)
            .select_related("appliance")
        )

    districts = (
        Area.objects
        .values_list("district", flat=True)
        .distinct()
        .order_by("district")
    )

    appliances_list = (
        Appliance.objects
        .all()
        .order_by("name")
    )

    result = None

    # ==========================
    # POST
    # ==========================

    if request.method == "POST":

        mode = request.POST.get("mode", "saved")

        total_load = 0
        total_appliance = 0
        recommendations = []
        schedule = None
        battery_percent = 0
        battery_message = ""

        def safe_int(value, default=0):
            try:
                return int(value)
            except (TypeError, ValueError):
                return default

        if mode == "saved":

            voltage = safe_int(
                request.POST.get("battery_voltage"), 12
            )

            battery_ah = safe_int(
                request.POST.get("battery_capacity"), 0
            )

            rows = (
                SetupAppliance.objects
                .filter(setup=saved_setup)
                .select_related("appliance")
            )

            area = profile.area if profile else None

        else:

            voltage = safe_int(
                request.POST.get("battery_voltage_temp"), 12
            )

            battery_ah = safe_int(
                request.POST.get("battery_capacity_temp"), 0
            )

            area = Area.objects.filter(
                id=request.POST.get("area")
            ).first()

            rows = []

            appliance_ids = request.POST.getlist("appliance[]")
            quantities = request.POST.getlist("quantity[]")
            priorities = request.POST.getlist("priority[]")

            for appliance_id, quantity, priority in zip(
                appliance_ids, quantities, priorities
            ):
                appliance_obj = Appliance.objects.filter(
                    id=appliance_id
                ).first()

                if not appliance_obj:
                    continue

                rows.append({
                    "appliance": appliance_obj,
                    "quantity": safe_int(quantity, 1),
                    "priority": safe_int(priority, 2),
                })

        # ==========================
        # LOAD
        # ==========================

        for row in rows:

            if mode == "saved":
                appliance = row.appliance
                quantity = row.quantity
                priority = row.priority
            else:
                appliance = row["appliance"]
                quantity = row["quantity"]
                priority = row["priority"]

            total_appliance += quantity
            total_load += appliance.watt * quantity

            if priority == 3:
                recommendations.append(appliance.name)

        usable_power = voltage * battery_ah * 0.85

        if total_load > 0:
            backup_time = round(usable_power / total_load, 2)
        else:
            backup_time = 0

        # ==========================
        # TODAY'S SCHEDULE
        # ==========================

        if area:
            today = date.today()
            today_day = today.strftime("%A")

            schedule = (
                Schedule.objects.filter(area=area)
                .filter(
                    Q(schedule_type="Daily")
                    |
                    Q(schedule_type="Weekly", day_of_week=today_day)
                )
                .order_by("start_time")
                .first()
            )

        # ==========================
        # BATTERY STATUS
        # ==========================

        if backup_time >= 5:
            status = "READY"
            battery_message = "Enough battery for today's scheduled outage."
        elif backup_time >= 3:
            status = "Needs Optimization"
            battery_message = "Battery is enough but optimization is recommended."
        else:
            status = "Backup Not Enough"
            battery_message = "Battery backup is not enough for today's outage."

        battery_percent = min(100, round((backup_time / 8) * 100))

        # ==========================
        # RECOMMENDATION
        # ==========================

        recommendation_text = []

        for appliance_name in recommendations:
            recommendation_text.append(f"Turn OFF {appliance_name}")

        if len(recommendation_text) == 0:
            recommendation_text.append("Your current setup is already optimized.")

        # ==========================
        # DURATION
        # ==========================

        duration = "--"

        if schedule:
            start = datetime.combine(date.today(), schedule.start_time)
            end = datetime.combine(date.today(), schedule.end_time)
            diff = end - start
            duration = f"{diff.seconds // 3600} Hours"

        # ==========================
        # RESULT
        # ==========================

        result = {
            "schedule": {
                "area": area.area_name if area else "--",
                "start_time": schedule.start_time if schedule else "--",
                "end_time": schedule.end_time if schedule else "--",
                "duration": duration,
            },
            "total_load": total_load,
            "backup_time": backup_time,
            "status": status,
            "battery_percent": battery_percent,
            "battery_message": battery_message,
            "recommendation": recommendation_text,
            "total_appliance": total_appliance,
            "battery_capacity": battery_ah,
        }

    # ==========================
    # CONTEXT
    # ==========================

    context = {
        "saved_setup": saved_setup,
        "profile": profile,
        "appliances": appliances,
        "districts": districts,
        "appliances_list": appliances_list,
        "result": result,
    }

    return render(request, "calculator.html", context)