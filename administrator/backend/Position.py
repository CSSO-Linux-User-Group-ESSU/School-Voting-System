from django.contrib import messages
from django.shortcuts import render
from voting.models import Position
from voting.forms import PositionForm
from django.http import HttpRequest, HttpResponse
from typing import Union

def viewPositions(request : HttpRequest) -> HttpResponse:
    """
    Displays and add positions for an election.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'admin/positions.html' template with position data.

    Raises:
        None

    Usage:
        This view displays and add positions for an election. It retrieves existing positions
        ordered by priority and provides a form for adding new positions. If a valid position is
        submitted via a POST request, it is added to the database, and a success message is displayed.
        If the form has errors, an error message is displayed. The view redirects to the same page after
        processing.
    """

    #Get all the position in the database
    positions : Position = Position.objects.order_by('-priority').all()

    #Forrm for adding a new postion
    form : PositionForm = PositionForm(request.POST or None)
    
    #Context to be used in the frontend when rendering
    context : Union[str, object] = {
        'positions': positions,
        'form1': form,
        'page_title': "Positions"
    }

    if request.method == 'POST':
        #Validate the form is the request method is POST

        if form.is_valid():

            #Save the form without it adding to database
            form = form.save(commit=False)

            #Set the priority of the position to count of all postions plus one
            form.priority = positions.count() + 1

            #Save the form in the database
            form.save()
            messages.success(request, "New Position Created")

        else:
            #Show an error message if the form don't validate
            messages.error(request, "Form errors")
    
    #Render the html file if the request method is GET or after creating a new position
    return render(request, "admin/positions.html", context)
