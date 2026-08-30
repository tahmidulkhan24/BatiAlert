import csv
from io import TextIOWrapper
from datetime import date, timedelta, datetime
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import *
from users.models import *


WEEK_DAYS = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday',
]


def schedule_applies_on(schedule_obj, target_date):
    if schedule_obj.start_date and target_date < schedule_obj.start_date:
        return False

    if schedule_obj.end_date and target_date > schedule_obj.end_date:
        return False

    if schedule_obj.schedule_type == 'Daily':
        return True

    return schedule_obj.day_of_week == target_date.strftime('%A')


def schedules_for_area_on(area_id, target_date):
    return (
        Schedule.objects
        .filter(area_id=area_id)
        .filter(
            Q(end_date__isnull=True) |
            Q(end_date__gte=target_date)
        )
        .filter(start_date__lte=target_date)
        .filter(
            Q(schedule_type='Daily') |
            Q(
                schedule_type='Weekly',
                day_of_week=target_date.strftime('%A')
            )
        )
        .select_related('area')
        .order_by('start_time')
    )


def build_area_status(area_obj, target_date=None):
    target_date = target_date or timezone.localdate()
    now = timezone.localtime()
    current_time = now.time()
    today_schedules = list(
        schedules_for_area_on(area_obj.id, target_date)
    )

    current_outage = None
    next_outage = None

    for schedule_obj in today_schedules:
        if (
            schedule_obj.start_time <= current_time and
            current_time < schedule_obj.end_time
        ):
            current_outage = schedule_obj
            break

        if (
            not next_outage and
            schedule_obj.start_time > current_time
        ):
            next_outage = schedule_obj

    return {
        'area': area_obj,
        'is_power_off': current_outage is not None,
        'current_outage': current_outage,
        'next_outage': next_outage,
        'today_schedules': today_schedules,
    }


def schedules_overlap(
    area,
    start_time,
    end_time,
    start_date,
    end_date,
    schedule_type,
    day_of_week,
    exclude_id=None
):
    query = Schedule.objects.filter(area=area)

    if exclude_id:
        query = query.exclude(id=exclude_id)

    query = query.filter(
        start_date__lte=end_date or start_date
    ).filter(
        Q(end_date__isnull=True) |
        Q(end_date__gte=start_date)
    ).filter(
        start_time__lt=end_time,
        end_time__gt=start_time
    )

    if schedule_type == 'Weekly':
        query = query.filter(
            Q(schedule_type='Daily') |
            Q(day_of_week=day_of_week)
        )

    return query.exists()


def notice_view(request):
    notices = (
        Notice.objects
        .select_related('area')
        .all()
    )

    query = request.GET.get('q', '').strip()
    notice_type = request.GET.get('type', '').strip()
    area_id = request.GET.get('area', '').strip()

    if query:
        notices = notices.filter(
            Q(title__icontains=query) |
            Q(message__icontains=query)
        )

    if notice_type:
        notices = notices.filter(
            notice_type=notice_type
        )

    if area_id:
        notices = notices.filter(
            area_id=area_id
        )

    notices = notices.order_by('-is_pinned', '-created_at')
    notice_list = list(notices)
    unread_ids = set()

    if request.user.is_authenticated:
        read_ids = set(
            NoticeRead.objects
            .filter(
                user=request.user,
                notice__in=notice_list
            )
            .values_list('notice_id', flat=True)
        )
        unread_ids = {
            notice.id
            for notice in notice_list
            if notice.id not in read_ids
        }

        NoticeRead.objects.bulk_create(
            [
                NoticeRead(
                    user=request.user,
                    notice=notice
                )
                for notice in notice_list
                if notice.id in unread_ids
            ],
            ignore_conflicts=True
        )

    return render(
        request,
        'notice.html',
        {
            'notices': notice_list,
            'unread_ids': unread_ids,
            'notice_types': Notice.NOTICE_TYPES,
            'areas': Area.objects.all().order_by(
                'district',
                'upazila',
                'area_name'
            ),
            'query': query,
            'selected_type': notice_type,
            'selected_area': area_id,
        }
    )

def home(request):
    priority_appliance = None
    total_watt = 0

    if request.user.is_authenticated:
        from users.models import SavedSetup

        setup = (
            SavedSetup.objects
            .filter(user=request.user)
            .prefetch_related("items__appliance")
            .first()
        )

        if setup:
            setup_items = setup.items.all()

            priority_appliance = (
                setup_items
                .order_by("priority", "id")
                .first()
            )

            for item in setup_items:
                watt = (
                    item.custom_watt
                    or item.appliance.watt
                )

                total_watt += (
                    watt *
                    item.quantity
                )

    return render(
        request,
        'home.html',
        {
            "priority_appliance":
            priority_appliance,

            "total_watt":
            total_watt,
        }
    )

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

    today = timezone.localdate()

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

        today_schedules = schedules_for_area_on(
            selected_area,
            today
        )

        # TOMORROW

        tomorrow_schedules = schedules_for_area_on(
            selected_area,
            tomorrow
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

        

        now = timezone.localtime()

        current_time = now.time()

        for schedule in today_schedules:

            if schedule.start_time > current_time:

                next_outage = schedule

                break
        if next_outage:

            outage_datetime = timezone.make_aware(
                datetime.combine(
                    today,
                    next_outage.start_time
                ),
                timezone.get_current_timezone()
            )

            diff = outage_datetime - now

            total_seconds = max(
                0,
                int(diff.total_seconds())
            )

            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60

            if hours > 0:
                countdown = f"{hours}h {minutes}m"
            else:
                countdown = f"{minutes}m"

    weekly_calendar = []

    if selected_area:
        for offset in range(7):
            day = today + timedelta(days=offset)
            weekly_calendar.append({
                'date': day,
                'day': day.strftime('%A'),
                'schedules': schedules_for_area_on(
                    selected_area,
                    day
                ),
            })

    selected_area_obj = None
    power_status = None

    if selected_area:
        selected_area_obj = Area.objects.filter(
            id=selected_area
        ).first()

    if selected_area_obj:
        power_status = build_area_status(
            selected_area_obj,
            today
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

        'weekly_calendar':
        weekly_calendar,

        'power_status':
        power_status,

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

 


@login_required(login_url="login")
def feedback_create(request):
    if request.method == "POST":
        area_id = request.POST.get("area") or None
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()
        feedback_type = request.POST.get(
            "feedback_type",
            "Schedule Issue"
        )

        if not subject or not message:
            messages.error(
                request,
                "Please add a subject and message."
            )
            return redirect("dashboard")

        FeedbackReport.objects.create(
            user=request.user,
            area_id=area_id,
            subject=subject,
            message=message,
            feedback_type=feedback_type
        )
        messages.success(
            request,
            "Thanks. Your report has been sent to the team."
        )

    return redirect("dashboard")


@staff_member_required
def management_dashboard(request):
    context = {
        "user_count": User.objects.count(),
        "schedule_count": Schedule.objects.count(),
        "notice_count": Notice.objects.count(),
        "pending_feedback_count": FeedbackReport.objects.filter(
            status="Pending"
        ).count(),
        "recent_feedback": FeedbackReport.objects.select_related(
            "user",
            "area"
        ).order_by("-created_at")[:5],
        "upcoming_schedules": Schedule.objects.select_related(
            "area"
        ).order_by("start_date", "start_time")[:6],
    }
    return render(
        request,
        "management/dashboard.html",
        context
    )


@staff_member_required
def management_schedules(request):
    schedules = (
        Schedule.objects
        .select_related("area")
        .all()
        .order_by("-start_date", "start_time")
    )
    area_id = request.GET.get("area")

    if area_id:
        schedules = schedules.filter(area_id=area_id)

    context = {
        "schedules": schedules[:200],
        "areas": Area.objects.all().order_by(
            "district",
            "upazila",
            "area_name"
        ),
        "week_days": WEEK_DAYS,
        "selected_area": area_id,
    }
    return render(
        request,
        "management/schedules.html",
        context
    )


@staff_member_required
def management_schedule_save(request, schedule_id=None):
    schedule_obj = (
        get_object_or_404(Schedule, id=schedule_id)
        if schedule_id
        else None
    )

    if request.method == "POST":
        area = get_object_or_404(
            Area,
            id=request.POST.get("area")
        )
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date") or None
        schedule_type = request.POST.get(
            "schedule_type",
            "Daily"
        )
        reason = request.POST.get("reason", "").strip()
        days = request.POST.getlist("day_of_week")

        parsed_start = datetime.strptime(
            start_time,
            "%H:%M"
        ).time()
        parsed_end = datetime.strptime(
            end_time,
            "%H:%M"
        ).time()
        parsed_start_date = datetime.strptime(
            start_date,
            "%Y-%m-%d"
        ).date()
        parsed_end_date = (
            datetime.strptime(end_date, "%Y-%m-%d").date()
            if end_date
            else None
        )

        if parsed_end <= parsed_start:
            messages.error(
                request,
                "End time must be after start time."
            )
            return redirect("management_schedules")

        if schedule_type == "Daily":
            days = [""]
        elif not days:
            messages.error(
                request,
                "Choose at least one recurring day."
            )
            return redirect("management_schedules")

        overlaps = []

        for day_name in days:
            if schedules_overlap(
                area,
                parsed_start,
                parsed_end,
                parsed_start_date,
                parsed_end_date,
                schedule_type,
                day_name,
                exclude_id=schedule_id
            ):
                overlaps.append(day_name or "Daily")

        if overlaps:
            messages.error(
                request,
                "Schedule overlaps existing entries: "
                + ", ".join(overlaps)
            )
            return redirect("management_schedules")

        if schedule_obj:
            schedule_obj.area = area
            schedule_obj.start_time = parsed_start
            schedule_obj.end_time = parsed_end
            schedule_obj.start_date = parsed_start_date
            schedule_obj.end_date = parsed_end_date
            schedule_obj.schedule_type = schedule_type
            schedule_obj.day_of_week = (
                days[0] if schedule_type == "Weekly" else None
            )
            schedule_obj.reason = reason
            schedule_obj.updated_at = timezone.now()
            schedule_obj.save()
            messages.success(request, "Schedule updated.")
        else:
            for day_name in days:
                Schedule.objects.create(
                    area=area,
                    start_time=parsed_start,
                    end_time=parsed_end,
                    start_date=parsed_start_date,
                    end_date=parsed_end_date,
                    schedule_type=schedule_type,
                    day_of_week=(
                        day_name
                        if schedule_type == "Weekly"
                        else None
                    ),
                    reason=reason
                )
            messages.success(request, "Schedule created.")

    return redirect("management_schedules")


@staff_member_required
def management_schedule_delete(request, schedule_id):
    if request.method == "POST":
        get_object_or_404(Schedule, id=schedule_id).delete()
        messages.success(request, "Schedule deleted.")

    return redirect("management_schedules")


@staff_member_required
def management_schedule_export(request):
    response = HttpResponse(content_type="text/csv")
    response[
        "Content-Disposition"
    ] = 'attachment; filename="batialert-schedules.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "district",
        "upazila",
        "area_name",
        "start_time",
        "end_time",
        "schedule_type",
        "day_of_week",
        "start_date",
        "end_date",
        "reason",
    ])

    for schedule_obj in Schedule.objects.select_related("area"):
        writer.writerow([
            schedule_obj.area.district,
            schedule_obj.area.upazila,
            schedule_obj.area.area_name,
            schedule_obj.start_time.strftime("%H:%M"),
            schedule_obj.end_time.strftime("%H:%M"),
            schedule_obj.schedule_type,
            schedule_obj.day_of_week or "",
            schedule_obj.start_date.isoformat(),
            schedule_obj.end_date.isoformat()
            if schedule_obj.end_date
            else "",
            schedule_obj.reason or "",
        ])

    return response


@staff_member_required
def management_schedule_import(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = TextIOWrapper(
            request.FILES["csv_file"].file,
            encoding="utf-8"
        )
        reader = csv.DictReader(csv_file)
        created = 0
        skipped = 0

        for row in reader:
            area = Area.objects.filter(
                district=row.get("district", "").strip(),
                upazila=row.get("upazila", "").strip(),
                area_name=row.get("area_name", "").strip()
            ).first()

            if not area:
                skipped += 1
                continue

            start_time = datetime.strptime(
                row["start_time"],
                "%H:%M"
            ).time()
            end_time = datetime.strptime(
                row["end_time"],
                "%H:%M"
            ).time()
            start_date = datetime.strptime(
                row["start_date"],
                "%Y-%m-%d"
            ).date()
            end_date = (
                datetime.strptime(row["end_date"], "%Y-%m-%d").date()
                if row.get("end_date")
                else None
            )

            if schedules_overlap(
                area,
                start_time,
                end_time,
                start_date,
                end_date,
                row.get("schedule_type", "Daily"),
                row.get("day_of_week", "")
            ):
                skipped += 1
                continue

            Schedule.objects.create(
                area=area,
                start_time=start_time,
                end_time=end_time,
                schedule_type=row.get("schedule_type", "Daily"),
                day_of_week=row.get("day_of_week") or None,
                start_date=start_date,
                end_date=end_date,
                reason=row.get("reason", "")
            )
            created += 1

        messages.success(
            request,
            f"Imported {created} schedules. Skipped {skipped} rows."
        )

    return redirect("management_schedules")


@staff_member_required
def management_notices(request):
    notices = Notice.objects.select_related("area").order_by(
        "-is_pinned",
        "-created_at"
    )
    notice_type = request.GET.get("type")

    if notice_type:
        notices = notices.filter(notice_type=notice_type)

    return render(
        request,
        "management/notices.html",
        {
            "notices": notices,
            "areas": Area.objects.all().order_by("area_name"),
            "notice_types": Notice.NOTICE_TYPES,
            "selected_type": notice_type,
        }
    )


@staff_member_required
def management_notice_save(request, notice_id=None):
    notice_obj = (
        get_object_or_404(Notice, id=notice_id)
        if notice_id
        else None
    )

    if request.method == "POST":
        data = {
            "area_id": request.POST.get("area") or None,
            "title": request.POST.get("title", "").strip(),
            "message": request.POST.get("message", "").strip(),
            "notice_type": request.POST.get(
                "notice_type",
                "General"
            ),
            "is_pinned": request.POST.get("is_pinned") == "on",
        }

        if notice_obj:
            for key, value in data.items():
                setattr(notice_obj, key, value)
            notice_obj.save()
            messages.success(request, "Notice updated.")
        else:
            Notice.objects.create(**data)
            messages.success(request, "Notice published.")

    return redirect("management_notices")


@staff_member_required
def management_feedback(request):
    reports = FeedbackReport.objects.select_related(
        "user",
        "area"
    ).order_by("-created_at")
    status = request.GET.get("status")

    if status:
        reports = reports.filter(status=status)

    return render(
        request,
        "management/feedback.html",
        {
            "reports": reports,
            "statuses": FeedbackReport.STATUS_CHOICES,
            "selected_status": status,
        }
    )


@staff_member_required
def management_feedback_update(request, report_id):
    report = get_object_or_404(
        FeedbackReport,
        id=report_id
    )

    if request.method == "POST":
        report.status = request.POST.get(
            "status",
            report.status
        )
        report.staff_note = request.POST.get(
            "staff_note",
            ""
        )
        report.save()
        messages.success(request, "Feedback updated.")

    return redirect("management_feedback")
