from django.contrib import messages
from django.shortcuts import redirect, reverse
from account.forms import CustomUserForm
from voting.forms import VoterForm
from voting.models import Voter
from django.http import HttpRequest, HttpResponseRedirect

def updateVoter(request : HttpRequest) -> HttpResponseRedirect:
    """
    Updates voter information based on the provided data in a POST request.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to the 'adminViewVoters' page after processing the request.

    Raises:
        None

    Usage:
        This view updates voter information based on the data provided in a POST request. The voter ID
        is extracted from the POST parameters, and the corresponding voter instance is retrieved. The
        user and voter forms are populated with the existing data of the voter instance and updated
        with the new data from the request. If the update is successful, a success message is displayed.
        If an error occurs during the update or the access is denied, an error message is displayed.
        The view redirects to the 'adminViewVoters' page after processing.
    """

    if request.method != 'POST':
        #Show an error message if the request method is GET not POST
        messages.error(request, "Access Denied")
        
    else:
        try:

            #Get the voter data based on the ID in the request data
            instance : Voter = Voter.objects.get(id=request.POST.get('id'))

            #Retreive the new information of the user
            user : CustomUserForm = CustomUserForm(request.POST or None, instance=instance.admin)
            voter = VoterForm(request.POST or None, instance=instance)
            
            #Save the changes in the database
            user.save()
            voter.save()
            messages.success(request, "Voter's bio updated")

        except:

            #Shoow an error message if an error occured while updating the user info
            messages.error(request, "Access To This Resource Denied")

    #Redirect the user to the same link
    return redirect(reverse('adminViewVoters'))