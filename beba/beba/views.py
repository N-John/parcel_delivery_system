from django.shortcuts import render

def index_view(request):
    return render (request,'public/index.html')

def priceing_view(request):
    return render (request,'public/priceing.html')

def about_view(request):
    return render (request,'public/about.html')

def contact_view(request):
    return render (request,'public/contact.html')

def services_view(request):
    return render (request,'public/services.html')

class oauth():
    def login_customer(request):
        pass
    def logout(request):
        pass
    def login_internal(reruest):
        pass
    def verification(request):
        pass
