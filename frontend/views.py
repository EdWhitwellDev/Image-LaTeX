from django.shortcuts import render

def index(request, *args, **kwargs): # note this is a function, not a class as it is not a REST API
    return render(request, 'frontend/index.html')