from django.shortcuts import render
from .models import Notice

def notice_view(request):
    notices = Notice.objects.all().order_by('-created_at')
    return render(request, 'notice.html', {'notices': notices})

def home(request):
    return render(request, 'home.html')