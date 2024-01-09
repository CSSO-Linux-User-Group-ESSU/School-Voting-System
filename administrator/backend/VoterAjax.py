from django.http import JsonResponse, HttpRequest
from voting.models import Voter
from typing import Union

def view_voter_by_id(request : HttpRequest) -> JsonResponse:
    """
    An API that retrieves voter information by voter ID and returns it as JSON response.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: JSON response containing voter information.

    Raises:
        None

    Usage:
        This view retrieves voter information based on the provided voter ID. The voter ID is
        extracted from the GET parameters in the request. If a voter with the specified ID exists,
        the information is returned as a JSON response with a success code (200). If no voter is
        found, a JSON response with a not found code (404) is returned.
    """

    #Extract the ID from the GET request
    voter_id : int = request.GET.get('id', None)

    #Extract the voter data based on the ID from the request
    voter : Voter = Voter.objects.filter(id=voter_id)

    context : Union[str, int] = {}
    
    if not voter.exists():
        #Only send a code response of 404 if the voter doesn't exist
        context['code'] = 404

    else:
        #Attach the user info if the voter data exist and set the code to 200 for sucessful reterieval
        context['code'] = 200

        #Get the first instance of the returned query
        voter = voter[0]

        #Add the fisrt name to the context
        context['first_name'] = voter.admin.first_name

        #Add the last name to the context
        context['last_name'] = voter.admin.last_name

        #Add the voter ID to the context
        context['id'] = voter.id
    
    #Return the response as a JSON
    return JsonResponse(context)