# finalAssessment>myapp>views.py
from django.shortcuts import render, HttpResponse, redirect

 # the index function is called when root is visited
def index(request):
    return render(request, 'index.html')
