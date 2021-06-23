from django.shortcuts import render


def home_view(request):
    return render(request, "site/pages/home_page.html")
