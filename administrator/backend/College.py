from django.contrib import messages
from django.shortcuts import redirect, reverse
from voting.forms import CollegeForm
from django.http import HttpResponseRedirect, HttpRequest

def colleges(request : HttpRequest) -> HttpResponseRedirect:
    """
    Handles the addition of college information through a form submission.

    Parameters:
        request (HttpRequest): The HTTP request object containing form data.

    Returns:
        HttpResponseRedirect: Redirects to the 'course' page after processing the form.

    Raises:
        None

    Usage:
        This view is responsible for processing the submission of a college form. It expects
        a POST request with college data. If the form is valid, the college information is
        saved, and a success message is displayed. If the form is invalid, an error message
        is displayed. In both cases, the view redirects to the 'course' page.
    """

    #Retrieve the form filled byu the user.
    collegesForm : CollegeForm = CollegeForm(request.POST)

    #Check if the reqest method is POST
    if request.method == "POST":

        #Validate the form
        if collegesForm.is_valid():

            #Save the data in the database if the form is valid
            collegesForm.save()
            messages.success(request, "Added College")  

        else:
            #Show an error if the form didn't pass the validation
            messages.error(request, "Invalid Form or College may already exist.")
    
    #Redirect the user to  the same page
    return redirect(reverse("course"))