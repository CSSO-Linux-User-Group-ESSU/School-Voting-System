from django.contrib import messages
from django.shortcuts import redirect, reverse
from administrator.models import ElectoralCommittee
from voting.models import Election
from django.http import HttpRequest, HttpResponseRedirect


def startElection(request : HttpRequest) -> HttpResponseRedirect:
    """
    Starts an election based on the user's role and permissions.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to the 'viewElections' page after starting the election.

    Raises:
        None

    Usage:
        Call this function to start an election. The function checks the request method,
        ongoing election status, user type, and Electoral Committee membership and scope
        before allowing the election to be started.
    """

    #Check if the request method is POST not GET
    if request.method != "POST":

        #Show an error when the method is GET
        messages.error(request, "Access To This Resources Denied!")

    else:
        #Get the data of any on-going election
        started : Election = Election.objects.filter(started=True)

        #Check if the on-going election is greater than or equal to one
        if started.count() >= 1:
            #Show an error saying that there's an on-going election
            messages.error(request, f"{started[0]} Election is on-going!")

        else:
            #Get the data of the election you want to start
            e : Election = Election.objects.filter(id=request.POST.get("start_id"))

            #Check if the user is admin
            if request.user.user_type == "1":
                #Start the election
                e.update(started=True)
                messages.success(request, f"{e[0].title} Election Started.")

            #Check if Electoral Committe
            elif request.user.user_type == "2":
                #Get the electoral committee data
                cmt : ElectoralCommittee = ElectoralCommittee.objects.get(fullname_id=request.user.id)
                
                #Check if the committee is allowed to start the election
                if e[0].course_limit and e[0].course_limit.college == cmt.scope or e[0].college_limit and e[0].college_limit == cmt.scope:
                    #Start the election if allowed
                    e.update(started=True)
                    messages.success(request, f"{e[0].title} Election Started.")
                
                else:
                    #Show an error message if not allowed
                    messages.error(request, "Access to that resource is denied!")
            else:
                #Show an error message if the user type is Voter
                messages.error(request, "No access here!") 
                

    #Redirect to same page 
    return redirect(reverse("viewElections"))
