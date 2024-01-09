from voting.models import Position
from django.http import JsonResponse, HttpRequest
from typing import Union

def view_position_by_id(request : HttpRequest) -> JsonResponse:
    """
    An API that retrieves position information by position ID and returns it as JSON response.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: JSON response containing position information.

    Raises:
        None

    Usage:
        This view retrieves position information based on the provided position ID. The position ID is
        extracted from the GET parameters in the request. If a position with the specified ID exists,
        the information is returned as a JSON response with a success code (200). If no position is
        found, a JSON response with a not found code (404) is returned.
    """

    #Extract the id in the GET request
    pos_id : int = request.GET.get('id', None)

    #Get the position data based on the ID in the GET request
    pos : Position = Position.objects.filter(id=pos_id)

    context : Union[str, int] = {}

    if not pos.exists():
        #Return an Error code 404 if the postion doesn't exist
        context['code'] = 404

    else:
        #Set the return code to 404 if there's a data about the position
        context['code'] = 200

        #Get the first instance of the query
        pos = pos[0]

        #Retreive the position name, max vote and ID and assign it in the context
        context['name'] = pos.name
        context['max_vote'] = pos.max_vote
        context['id'] = pos.id

    #Return the data as a JSON
    return JsonResponse(context)