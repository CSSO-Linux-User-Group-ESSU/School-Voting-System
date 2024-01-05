from django.contrib import messages
from administrator.models import ElectoralCommittee
from django.shortcuts import redirect, reverse
from voting.models import Election
from django.http import HttpRequest, HttpResponseRedirect

def stoper(request : HttpRequest) -> HttpResponseRedirect:
    """
    Stops an ongoing election based on the user's role and permissions.

    Parameters:
        - request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to the 'viewElections' page after stopping the election.

    Raises:
        None

    Usage:
        Call this function to stop an election. The function checks the user's type and
        permissions before allowing the election to be stopped.
    """

    #Check it the request method is POST not GET
    if request.method != "POST":

        #Show an error when the method is GET
        messages.error(request, "Access To This Resources Denied!")

    else:
        #Get the election data from the database
        e : Election = Election.objects.filter(id=request.POST.get("stop_id"))

        #Check for user's type of permissions
        if request.user.user_type == "1":
            #Admin can stop any election
            e.update(started=False) #Change the election state in the database
            messages.success(request, "You can now start another election.")
        
        elif request.user.user_type == "2":
            #ELectoral committee still need to be verified if they are allowed and have limited access
            cmt : ElectoralCommittee = ElectoralCommittee.objects.get(fullname_id=request.user.id) #Get the electoral committee data

            #Check if the committee and election have the same college of department
            if e[0].course_limit and e[0].course_limit.college == cmt.scope or e[0].college_limit and e[0].college_limit == cmt.scope:
                e.update(started=False) #Change the election state in the database
                messages.success(request, "You can now start another election.")

            #Committee has no power to stop the election
            else:
                 messages.error(request, "Access to that resource is denied!")
        else:
            #Voter have to access in changing the election state
            messages.error(request, "No Access Here!")
    
    #return HttpResponseRedirect
    return redirect(reverse("viewElections"))