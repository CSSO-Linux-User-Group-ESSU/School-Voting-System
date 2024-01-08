from django.contrib import messages
from django.shortcuts import render
from voting.models import Voter
from voting.forms import VoterForm, FileUploadForm
from account.forms import CustomUserForm
from django.http import HttpRequest, HttpResponse


def voters(request : HttpRequest) -> HttpResponse:
    """
    Manages the creation and display of voters.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'admin/voters.html' template with voter data.

    Raises:
        None

    Usage:
        This view handles the creation and display of voters. It provides forms for adding new
        voters, including a custom user form and a voter form. The view also displays the list
        of existing voters ordered by course, year level, and admin. If a valid voter is submitted
        via a POST request, a new voter is created, and a success message is displayed.
    """
    #Ordering of the data when querying
    ordering = ["course", "year_level", "admin"]

    #Get all the voters based on the ordering
    voters = Voter.objects.all().order_by(*ordering)

    #Get the user creation form, voter creation form and Bulk user upload. 
    #The request.POST or None means that a user can create or validate a form
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)
    fileupload = FileUploadForm()

    #Add everything in a dictionary to be used in the jinja when rendering
    context = {
        'form1': userForm,
        'form2': voterForm,
        'voters': voters,
        'page_title': 'Voters List',
        'userupload' : fileupload
    }

    #Check for request method
    if request.method == 'POST':

        #Valid the User Creation and Voter form is the request method is post
        if userForm.is_valid() and voterForm.is_valid():

            #Save the data that the user has filled without commiting it to the database for linking
            user = userForm.save(commit=False)
            voter = voterForm.save(commit=False)

            #Link the voter data to user data, Effectively creating a user and be able to sign in
            voter.admin = user

            #Save the data to the database
            user.save()
            voter.save()
            messages.success(request, "New voter created")

        else:
            #Display an error message if the request method is GET
            messages.error(request, "Form validation failed")
    
    #Render the HTML after eeach request
    return render(request, "admin/voters.html", context)