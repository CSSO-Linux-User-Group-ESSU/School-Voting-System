from django.shortcuts import redirect, reverse
from django.contrib import messages
from voting.models import College
from django.http import HttpResponseRedirect, HttpRequest

def remove_college(request : HttpRequest) -> HttpResponseRedirect:
    """
    Handles the removal of a college based on a POST request.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to the 'course' page after processing the request.

    Raises:
        None

    Usage:
        This view is responsible for processing the removal of a college. It expects a
        POST request with the 'college' parameter containing the ID of the college to be deleted.
        If the request is valid, the specified college is deleted, and a success message is displayed.
        If the request is invalid or unauthorized, an error message is displayed. In both cases,
        the view redirects to the 'course' page.
    """

    #Check if the request method is POST
    if request.method == "POST":

        #Get the college data based on the ID given
        college_to_delete = College.objects.get(id=request.POST.get("college"))

        #Delete the college in the database
        college_to_delete.delete()
        messages.success(request, "Deleted")

    else:
        #Show an error if the request method is GET or not POST
        messages.error(request, "Access To this Resources is Denied!")
    
    #Redirect the user to the course url
    return redirect(reverse("course"))
