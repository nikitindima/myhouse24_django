from django.shortcuts import render


def home_view(request):
    return render(request, "site/pages/home.html")


def about_view(request):
    return render(request, "site/pages/about.html")


def services_view(request):
    return render(request, "site/pages/services.html")


def contacts_view(request):
    return render(request, "site/pages/contacts.html")
