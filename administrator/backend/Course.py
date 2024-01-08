from django.contrib import messages
from django.shortcuts import render
from voting.forms import CollegeForm, CourseForm
from voting.models import Course
from django.db.models import Count
from django.http import HttpRequest, HttpResponse

def course(request : HttpRequest) -> HttpResponse:
    """
    Manages courses and colleges, allowing the addition of new courses.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'admin/colleges.html' template with course and college data.

    Raises:
        None

    Usage:
        This view handles the management of courses and colleges. It provides a form for adding new
        courses, and it retrieves a list of colleges with the count of voters for each course. If a
        valid course is submitted via a POST request, it is added to the database, and a success
        message is displayed.
    """
    
    #Get how many voters a certain course have
    colleges : Course = Course.objects.annotate(voter_count=Count('voter'))

    #Form for addding a new course
    courseForm : CourseForm = CourseForm(request.POST or None)

    #Form for addding a new college
    collegeForm : CollegeForm = CollegeForm(request.POST or None)

    #Add everything in a dictionary to be used in the jinja when rendering
    context : dict[object | str] = {
        'course' : courseForm,
        'college' : collegeForm,
        'colleges' : colleges,
        'page_title' : "Courses/college"
    }

    if request.method == "POST":
    ##Check if the the user is using a POST method which means they are addding a new course
        
        if courseForm.is_valid():    
            #Save the course in the database if it validate the django validation
            courseForm.save()
            messages.success(request, "Added Course")
    
    #Render the html when the user is using GET method or done adding a new course
    return render(request, "admin/colleges.html", context)