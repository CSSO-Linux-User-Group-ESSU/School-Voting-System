from voting.models import Election, Position, Voter, Candidate, Votes, College
from administrator.models import ElectoralCommittee
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest

def dashboard(request : HttpRequest) -> HttpResponse:
    """
    Generates and displays the dashboard for election-related information.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'admin/home.html' template with the dashboard data.

    Raises:
        None

    Usage:
        This view generates and displays the dashboard for election-related information.
        It retrieves data about active elections, user roles, and permissions to customize
        the displayed information. The dashboard includes details on positions, candidates,
        voters, and voting statistics. Additionally, it generates charts with voting data for
        different positions if an active election is present.
    """

    #Get the data of any active election
    active_election : Election = Election.objects.filter(started=True)

    try:
        #Get the electoral committee data if the one logging in is a committee member
        user_data : ElectoralCommittee = ElectoralCommittee.objects.get(fullname_id = request.user.id)
    except Exception:
        #Set the userr data to none if not a memeber of committee
        user_data = None
    
    #Initialize varaiable to be filled later
    context : dict = {}
    chart_data : dict = {}
    search : str = "all"
    show_chart : bool = False

    if not active_election:
        #No active Election

        #Get all the position, candidates, voter and the voters whow voted in the database
        #Set the has_election to false and positions to empty
        positions : Position = Position.objects.all()
        candidates : Candidate = Candidate.objects.all()
        voters : Voter = Voter.objects.all()
        voted_voters : Voter = Voter.objects.filter(voted=1)
        context["has_election"] = False
        context["positions"] = []
        
    else:
        #If there's active election going

        #Get all the distinct positions in the current election from the database order by their priority
        positions : Position = Position.objects.filter(candidate__election_id=active_election[0]).distinct().order_by('priority')

        #Get all the Candidate of the current active election
        candidates : Candidate = Candidate.objects.filter(election=active_election[0])

        if active_election[0].scope == "1":
            #If the election scope is university-wide

            if user_data and user_data.ssc == True or request.user.user_type == "1":
                #If the user is an SSC committee or an admin
                #Get the all the Voters and voters whoe already voted in the database
                voters :  Voter = Voter.objects.all()
                voted_voters : Voter = Voter.objects.filter(voted=1)

                #Set this to true to see the chart
                show_chart : bool = True
            else:
                #Don't show any data if the user is not an SSC member or not an admin
                voters : Voter = Voter.objects.filter(id=0)
                voted_voters : Voter = Voter.objects.filter(id=0)
                show_chart : bool = False
        
        elif active_election[0].scope == "2":
            #If the election scope is college-wide

            if user_data and user_data.scope == active_election[0].college_limit or request.user.user_type == "1":
                #If the comittee is enrolled in the same college as the college scope of the current election or the user is an admin

                #Get all the voters with the same college as the college scope
                voters : Voter = Voter.objects.filter(course__college=active_election[0].college_limit)

                #Get all the voters who voted with the same college as the college scope
                voted_voters : Voter = Voter.objects.filter(course__college=active_election[0].college_limit,voted=1)

                #Set the search to whatever college limit/scope the active election have
                search : str = active_election[0].college_limit

                #Set to show the chart
                show_chart : bool = True

        elif active_election[0].scope == "3":
            #If the election is course-wide

            #Get the college of the course in the active election
            course_college : College = College.objects.get(course=active_election[0].course_limit)

            if user_data and user_data.scope == course_college or request.user.user_type == "1":
                #If the comittee is enrolled in the same college as the college scope of the current election or the user is an admin

                #Get all the voters with the same course and year level as the election limiy
                voters :  Voter = Voter.objects.filter(course=active_election[0].course_limit, year_level=active_election[0].year_level_limit)

                #Get all the voters who already voted with the same course and year level as the election limiy
                voted_voters : Voter = Voter.objects.filter(course=active_election[0].course_limit, year_level=active_election[0].year_level_limit, voted=1)

                #Set the search to the election course and year
                search : str = f"{active_election[0].course_limit}-{active_election[0].year_level_limit}"

                #show the chart
                show_chart : bool = True


        if show_chart:
            #If allowed to show the chart
            for position in positions:
                #Itterate over to all the distinct position
                list_of_candidates : list = []
                votes_count : list = []

                for candidate in Candidate.objects.filter(position=position, election=active_election[0]):
                    #Iterate over the candidates in the active election

                    #Get the candidate name and append it list_of_candidates list variable
                    list_of_candidates.append(str(candidate.fullname))

                    #Get all the votes for that candidate and append to vote_count list variable
                    votes : Votes = Votes.objects.filter(candidate=candidate).count()
                    votes_count.append(votes)

                #Insert all the data in the chart_data for rendering in the frontend chart
                chart_data[position] = {
                    'candidates': list_of_candidates,
                    'votes': votes_count,
                    'pos_id': position.id
                }
        
        #Add the data to context to be used in the frontend with jinja
        context["has_election"] = show_chart
        context["positions"] = positions
        context["election_title"] = str(active_election[0]).title()

    if request.user.user_type == "2":
        #If the user is an electoral committee
        if not user_data.ssc:
            #Check if the user is not an SSC member

            #Get all the voters, candidate and positions with the same college as the user
            voters : Voter = Voter.objects.filter(course__college=user_data.scope)
            candidates : Candidate = Candidate.objects.filter(fullname__course__college=user_data.scope)
            positions : Position = Position.objects.filter(candidate__fullname__course__college=user_data.scope).distinct().order_by('priority')
            
            #Set the search to be the limit scope of the user
            search : str = user_data.scope
    
    
    #Add the data to context to be used in the frontend with jinja
    context["search"] = search
    context["position_count"] = positions.count()  
    context["voters_count"] = voters.count()
    context['candidate_count'] = candidates.count()
    context["voted_voters_count"] = voted_voters.count() 
    context["chart_data"] = chart_data
    context['page_title'] = "Dashboard"

    #Return an HttpResponse to render the dashboard
    return render(request, "admin/home.html", context)