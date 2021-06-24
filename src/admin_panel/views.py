from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def home_view(request):
    return render(request, 'admin_panel/pages/home.html')
