from django.shortcuts import render

# Create your views here.

#Rendering the members.html
def members(request):
    return render(request, "members.html")