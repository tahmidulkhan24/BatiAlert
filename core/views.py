from django.shortcuts import render


def home(request):
    return render(
        request,
        'base.html'
    )
def schedule(request):
    return render(
        request,
        'schedule.html'
    )