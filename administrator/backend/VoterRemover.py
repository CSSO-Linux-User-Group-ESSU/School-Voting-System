from django.contrib import messages
from django.shortcuts import redirect, reverse
from voting.models import Voter
from django.http import HttpResponseRedirect, HttpRequest

def deleteVoter(request : HttpRequest) -> HttpResponseRedirect:
    """
    Deletes a voter and associated user based on the provided voter ID in a POST request.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to the 'adminViewVoters' page after processing the request.

    Raises:
        None

    Usage:
        This view deletes a voter and associated user based on the provided voter ID in a POST request.
        The voter ID is extracted from the POST parameters, and the corresponding voter and user instances
        are retrieved. If the deletion is successful, a success message is displayed. If an error occurs
        during the deletion or access is denied, an error message is displayed. The view redirects to the
        'adminViewVoters' page after processing.
    """

    if request.method != 'POST':
        #Show an error message if the request method is not POST
        messages.error(request, "Access Denied")
    else:
        try:

            #Retrieve the account and voter data based on the ID given in the request
            admin : Voter = Voter.objects.get(id=request.POST.get('id')).admin
            voter : Voter = Voter.objects.get(id=request.POST.get('id'))
            
            #Delete the account and voter data in the database
            admin.delete()
            voter.delete()

            messages.success(request, "Voter Has Been Deleted")
        
        except:
            #Show an error message if an error has occured upon deleting
            messages.error(request, "Access To This Resource Denied")
    #redirect the user to adminViewVoters route
    return redirect(reverse('adminViewVoters'))