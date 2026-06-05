from django.shortcuts import render
from .models import Notice

def home(request):
    return render(
        request,
        'base.html'
    )

def notice_view(request):
    notices = Notice.objects.all().order_by('-created_at') 
    return render(request, 'notice.html', {'notices': notices})