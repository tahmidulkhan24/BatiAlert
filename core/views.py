from django.shortcuts import render
from .models import Notice
from django.http import JsonResponse
from .models import *
from datetime import date, timedelta, datetime
from django.db.models import Q


def notice_view(request):
    notices = Notice.objects.all().order_by('-created_at')
    return render(request, 'notice.html', {'notices': notices})

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
