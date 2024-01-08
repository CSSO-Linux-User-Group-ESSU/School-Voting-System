from django.contrib import messages
from voting.models import Course
from django.shortcuts import redirect, reverse
from django.http import HttpRequest, HttpResponseRedirect

def delete_course(request : HttpRequest) -> HttpResponseRedirect:
    """
    Handles the deletion of a course based on a POST request.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to the 'course' page after processing the request.

    Raises:
        None

    Usage:
        This view is responsible for processing the deletion of a course. It expects a
        POST request with the 'course_delete' parameter containing the ID of the course
        to be deleted. If the request is valid, the specified course is deleted, and a
        success message is displayed. If the request is invalid or unauthorized, an error
        message is displayed. In both cases, the view redirects to the 'course' page.
    """

    #Check if the request method is POST or GET
    if request.method != "POST":

        #Show an error message if the request method GET
        messages.error(request, "Acces To This Resources is Denied!")
    
    else:
        #Start an error handler if the request method is POST
        try:

            #Extract the coure id included in the POST request and retrieve the course data based on that id
            course_id : Course = Course.objects.get(id=request.POST.get("course_delete"))
            
            #Delete the course in the database
            course_id.delete()
            messages.success(request, "Course Deleted!")
        
        except Exception:
            #Show an error message if an error has occured during the deletion
            messages.error(request, "Access To This Resources is Denied!")
    
    #Redirect the user to `course` route
    return redirect(reverse("course"))