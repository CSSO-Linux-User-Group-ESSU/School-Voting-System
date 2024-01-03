from django.shortcuts import render, reverse, redirect
from voting.models import Voter, Position, Candidate, Votes, Election
from administrator.forms import CommitteeForms
from administrator.models import ElectoralCommittee
from account.models import CustomUser
from account.forms import CustomUserForm
from voting.forms import *
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
import json  # Not used
from django_renderpdf.views import PDFView
from django.db.models import Count, Q
from administrator.voter_upload import upload_voters
import os
from administrator.backend.ElectionStop import stoper

def find_n_winners(data, n):
    """Read More
    https://www.geeksforgeeks.org/python-program-to-find-n-largest-elements-from-a-list/
    """
    final_list = []
    candidate_data = data[:]
    # print("Candidate = ", str(candidate_data))
    for i in range(0, n):
        max1 = 0
        if len(candidate_data) == 0:
            continue
        this_winner = max(candidate_data, key=lambda x: x['votes'])
        # TODO: Check if None
        this = this_winner['name'] + \
            " with " + str(this_winner['votes']) + " votes"
        final_list.append(this)
        candidate_data.remove(this_winner)
    return ", &nbsp;".join(final_list)


class PrintView(PDFView):
    template_name = 'admin/print.html'
    prompt_download = True

    @property
    def download_name(self):
        return "result.pdf"

    def get_context_data(self, *args, **kwargs):
        title = "E-voting"
        try:
            file = open(settings.ELECTION_TITLE_PATH, 'r')
            title = file.read()
        except:
            pass
        context = super().get_context_data(*args, **kwargs)
        position_data = {}
        for position in Position.objects.all():
            candidate_data = []
            winner = ""
            for candidate in Candidate.objects.filter(position=position):
                this_candidate_data = {}
                votes = Votes.objects.filter(candidate=candidate).count()
                this_candidate_data['name'] = candidate.fullname
                this_candidate_data['votes'] = votes
                candidate_data.append(this_candidate_data)
            print("Candidate Data For  ", str(
                position.name), " = ", str(candidate_data))
            # ! Check Winner
            if len(candidate_data) < 1:
                winner = "Position does not have candidates"
            else:
                # Check if max_vote is more than 1
                if position.max_vote > 1:
                    winner = find_n_winners(candidate_data, position.max_vote)
                else:

                    winner = max(candidate_data, key=lambda x: x['votes'])
                    if winner['votes'] == 0:
                        winner = "No one voted for this yet position, yet."
                    else:
                        """
                        https://stackoverflow.com/questions/18940540/how-can-i-count-the-occurrences-of-an-item-in-a-list-of-dictionaries
                        """
                        count = sum(1 for d in candidate_data if d.get(
                            'votes') == winner['votes'])
                        if count > 1:
                            winner = f"There are {count} candidates with {winner['votes']} votes"
                        else:
                            winner = "Winner : " + winner['name']
            print("Candidate Data For  ", str(
                position.name), " = ", str(candidate_data))
            position_data[position.name] = {
                'candidate_data': candidate_data, 'winner': winner, 'max_vote': position.max_vote}
        context['positions'] = position_data
        print(context)
        return context


def dashboard(request):
    active_election = Election.objects.filter(started=True)
    try:
        user_data = ElectoralCommittee.objects.get(fullname_id = request.user.id)
    except Exception:
        user_data = None
    context = {}
    chart_data = {}
    search = "all"
    show_chart = False
    if not active_election:
        positions : Position = Position.objects.all()
        candidates = Candidate.objects.all()
        voters = Voter.objects.all()
        voted_voters = Voter.objects.filter(voted=1)
        context["has_election"] = False
        context["positions"] = []
    else:
        positions : Position = Position.objects.filter(candidate__election_id=active_election[0]).distinct().order_by('priority')
        candidates = Candidate.objects.filter(election=active_election[0])
        if active_election[0].scope == "1":
            if user_data and user_data.ssc == True or request.user.user_type == "1":
                voters = Voter.objects.all()
                voted_voters = Voter.objects.filter(voted=1)
                show_chart = True
            else:
                voters = Voter.objects.filter(id=0)
                voted_voters = Voter.objects.filter(id=0)
                show_chart = False
        elif active_election[0].scope == "2":
            if user_data and user_data.scope == active_election[0].college_limit or request.user.user_type == "1":
                voters = Voter.objects.filter(course__college=active_election[0].college_limit)
                voted_voters = Voter.objects.filter(course__college=active_election[0].college_limit,voted=1)
                search = active_election[0].college_limit
                show_chart = True
        elif active_election[0].scope == "3":
            course_college = College.objects.get(course=active_election[0].course_limit)
            if user_data and user_data.scope == course_college or request.user.user_type == "1":
                voters = Voter.objects.filter(course=active_election[0].course_limit, year_level=active_election[0].year_level_limit)
                voted_voters = Voter.objects.filter(course=active_election[0].course_limit, year_level=active_election[0].year_level_limit, voted=1)
                search = f"{active_election[0].course_limit}-{active_election[0].year_level_limit}"
                show_chart = True
        if show_chart:
            for position in positions:
                list_of_candidates = []
                votes_count = []
                for candidate in Candidate.objects.filter(position=position, election=active_election[0]):
                    list_of_candidates.append(str(candidate.fullname))
                    votes = Votes.objects.filter(candidate=candidate).count()
                    votes_count.append(votes)
                chart_data[position] = {
                    'candidates': list_of_candidates,
                    'votes': votes_count,
                    'pos_id': position.id
                }
        

        context["has_election"] = show_chart
        context["positions"] = positions
        context["election_title"] = str(active_election[0]).title()

    if request.user.user_type == "2":
        if not user_data.ssc:
            voters = Voter.objects.filter(course__college=user_data.scope)
            candidates = Candidate.objects.filter(fullname__course__college=user_data.scope)
            positions = Position.objects.filter(candidate__fullname__course__college=user_data.scope).distinct().order_by('priority')
            search = user_data.scope
    
   
    context["search"] = search
    context["position_count"] = positions.count()  
    context["voters_count"] = voters.count()
    context['candidate_count'] = candidates.count()
    context["voted_voters_count"] = voted_voters.count() 
    context["chart_data"] = chart_data
    context['page_title'] = "Dashboard"
    return render(request, "admin/home.html", context)

#Added method of adding course
def colleges(request):
    collegesForm = CollegeForm(request.POST)         #Get tge form from forms.py
    if request.method == "POST":                        #Ensuring correct usage
        if collegesForm.is_valid():                     #validate the form
            collegesForm.save()                         #Save to database
            messages.success(request, "Added College")  
        else:
            messages.error(request, "Invalid Form or College may already exist.")
    return redirect(reverse("course"))

def remove_college(request):
    if request.method == "POST":
        college_to_delete = College.objects.get(id=request.POST.get("college"))
        college_to_delete.delete()
        messages.success(request, "Deleted")
    else:
        messages.error(request, "Access To this Resources is Denied!")
    return redirect(reverse("course"))

#Added method for adding course and rendering the html
def course(request):
    colleges = Course.objects.annotate(voter_count=Count('voter')) #Query with the count of voter each course
    courseForm = CourseForm(request.POST or None)
    collegeForm = CollegeForm(request.POST or None)
    context = {
        'course' : courseForm,
        'college' : collegeForm,
        'colleges' : colleges,
        'page_title' : "Courses/college"
    }

    if request.method == "POST":
        if courseForm.is_valid():
            courseForm.save()
            messages.success(request, "Added Course")
    return render(request, "admin/colleges.html", context)


#Added method for deleting a course
def delete_course(request):
    if request.method != "POST":
        messages.error(request, "Acces To This Resources is Denied!")
    else:
        try:
            course_id = Course.objects.get(id=request.POST.get("course_delete"))
            course_id.delete()
            messages.success(request, "Course Deleted!")
        except Exception:
            messages.error(request, "Access To This Resources is Denied!")
    return redirect(reverse("course"))

def voters(request):
    ordering = ["course", "year_level", "admin"]
    voters = Voter.objects.all().order_by(*ordering)
    userForm = CustomUserForm(request.POST or None)
    voterForm = VoterForm(request.POST or None)
    fileupload = FileUploadForm()
    context = {
        'form1': userForm,
        'form2': voterForm,
        'voters': voters,
        'page_title': 'Voters List',
        'userupload' : fileupload
    }
    if request.method == 'POST':
        if userForm.is_valid() and voterForm.is_valid():
            user = userForm.save(commit=False)
            voter = voterForm.save(commit=False)
            voter.admin = user
            user.save()
            voter.save()
            messages.success(request, "New voter created")
        else:
            messages.error(request, "Form validation failed")
    return render(request, "admin/voters.html", context)


#Function handler when uploading a file of voters
def uploadUser(request : object):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            save_file = form.save()
            filepath = UploadFile.objects.get(id=save_file.pk)
            try:
                error_student = upload_voters(filepath.voters_file)
            except Exception:
                os.remove(f"./media/{str(filepath.voters_file)}")
                messages.error(request, "Invalid File Format! Did you ask for a form from CCS?")
            else:
                if error_student:
                    invalid_student = ""
                    for student in error_student:
                        invalid_student += f"{student}, "
                    messages.error(request, f"Invalid Students: {invalid_student}")
                else:
                    messages.success(request, "Uploading Voters Now")
        else:
            messages.error(request, "File mismatch")
    else:
        messages.error(request, "Access To This Resource Denied")
    return redirect(reverse("adminViewVoters"))


def view_voter_by_id(request):
    voter_id = request.GET.get('id', None)
    voter = Voter.objects.filter(id=voter_id)
    context = {}
    if not voter.exists():
        context['code'] = 404
    else:
        context['code'] = 200
        voter = voter[0]
        context['first_name'] = voter.admin.first_name
        context['last_name'] = voter.admin.last_name
        context['id'] = voter.id
    return JsonResponse(context)


def view_position_by_id(request):
    pos_id = request.GET.get('id', None)
    pos = Position.objects.filter(id=pos_id)
    context = {}
    if not pos.exists():
        context['code'] = 404
    else:
        context['code'] = 200
        pos = pos[0]
        context['name'] = pos.name
        context['max_vote'] = pos.max_vote
        context['id'] = pos.id
    return JsonResponse(context)


def updateVoter(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        instance = Voter.objects.get(id=request.POST.get('id'))
        user = CustomUserForm(request.POST or None, instance=instance.admin)
        voter = VoterForm(request.POST or None, instance=instance)
        user.save()
        voter.save()
        messages.success(request, "Voter's bio updated")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('adminViewVoters'))


def deleteVoter(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        admin = Voter.objects.get(id=request.POST.get('id')).admin
        admin.delete()
        messages.success(request, "Voter Has Been Deleted")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('adminViewVoters'))


def viewPositions(request):
    positions = Position.objects.order_by('-priority').all()
    form = PositionForm(request.POST or None)
    context = {
        'positions': positions,
        'form1': form,
        'page_title': "Positions"
    }
    if request.method == 'POST':
        if form.is_valid():
            form = form.save(commit=False)
            form.priority = positions.count() + 1  # Just in case it is empty.
            form.save()
            messages.success(request, "New Position Created")
        else:
            messages.error(request, "Form errors")
    return render(request, "admin/positions.html", context)


def updatePosition(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        instance = Position.objects.get(id=request.POST.get('id'))
        pos = PositionForm(request.POST or None, instance=instance)
        pos.save()
        messages.success(request, "Position has been updated")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('viewPositions'))

def deletePosition(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        pos = Position.objects.get(id=request.POST.get('id'))
        pos.delete()
        messages.success(request, "Position Has Been Deleted")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('viewPositions'))

#For fething all the elections that the database have
def viewElections(request):
    electionForm = ElectionForm(request.POST or None)
    on_going = Election.objects.all().order_by('title')
    if request.user.user_type == "2":
        user_data = ElectoralCommittee.objects.get(fullname_id=request.user.id)
        if not user_data.ssc:
            on_going = Election.objects.filter(Q(course_limit__college = user_data.scope) | Q(college_limit = user_data.scope))
        else:
            on_going = Election.objects.filter(scope=1)
    context = {
        "electionForm" : electionForm,
        "on_going" : on_going,
        'page_title' : "Election"
    }
    if request.method == "POST":
        electionForm.save()
        messages.success(request, "Added")
    return render(request, "admin/election.html", context)

#For deleting an election instance in the database
def delete_election(request):
    if request.method == "POST":
        try:
            election = Election.objects.get(id=request.POST.get('id'))
            election.delete()
            messages.success(request, "Deleted!")
        except Exception:
            messages.error(request, "Form Error!")
    else:
        messages.error(request, "Access To This Resource Denied!")
    return redirect(reverse("viewElections"))

#Fetching single election given an ID of the election
def election_by_id(request):
    election_id = request.GET.get('id', None)
    election = Election.objects.filter(id=election_id)
    context = {}
    if not election.exists():
        context['code'] = 404
    else:
        election = election[0]
        context['code'] = 200
        context['title'] = election.title
        previous = ElectionForm(instance=election)
        context['form'] = str(previous.as_p())
    return JsonResponse(context)
 
def startElection(request):
    if request.method != "POST":
        messages.error(request, "Access To This Resources Denied!")
    else:
        started = Election.objects.filter(started=True)
        if started.count() >= 1:
            messages.error(request, f"{started[0]} Election is on-going!")
        else:
            e = Election.objects.filter(id=request.POST.get("start_id"))
            if request.user.user_type == "1":
                e.update(started=True)
                messages.success(request, f"{e[0].title} Election Started.")
            elif request.user.user_type == "2":
                cmt = ElectoralCommittee.objects.get(fullname_id=request.user.id)
                if e[0].course_limit and e[0].course_limit.college == cmt.scope or e[0].college_limit and e[0].college_limit == cmt.scope or cmt.ssc and e[0].scope == "1":
                    e.update(started=True)
                    messages.success(request, f"{e[0].title} Election Started.")
                else:
                    messages.error(request, "Access to that resource is denied!")
            else:
                messages.error(request, "No access here!") 
                
        
    return redirect(reverse("viewElections"))

def stopElection(request):
    req = stoper(request)
    return redirect(req)

def viewCandidates(request):
    form = CandidateForm(request.POST or None, request.FILES or None)
    try:
        election_id = Election.objects.get(id=request.GET.get("id"))
    except Exception:
        if Election.objects.filter(started = True).count() <= 0:
            messages.success(request, "Viewing all candidates.")
            candidates = Candidate.objects.all()
            election_id = False
    else:
        candidates = Candidate.objects.filter(election=election_id)

    if election_id.scope == "1":
        prospects = Voter.objects.all()
    elif election_id.scope == "2":
        prospects = Voter.objects.filter(course__college = election_id.college_limit)
    else:
        prospects = Voter.objects.filter(course=election_id.course_limit, year_level=election_id.year_level_limit)

    context = {
        'candidates': candidates,
        'form1': form,
        'page_title': 'Candidates',
        'election_id' : election_id,
        "prospects" : prospects
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                fullname = request.POST.get('fullname_id').split(",")
            except Exception:
                messages.error(request, "Invalid Name!")
            else:
                voter_data = Voter.objects.get(admin__first_name = fullname[0], admin__last_name = fullname[1].strip())
                if voter_data.id_number != form.cleaned_data['student_id']:
                    messages.error(request, "Student ID is from other student!")
                else:
                    form = form.save(commit=False)
                    form.fullname = voter_data
                    form.election = election_id
                    form.save()
                    messages.success(request, "New Candidate Created")
        else:
            messages.error(request, "Student not enrolled.")
    return render(request, "admin/candidates.html", context)

def updateCandidate(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        candidate_id = request.POST.get('id')
        candidate = Candidate.objects.get(id=candidate_id)
        form = CandidateForm(request.POST or None,
                             request.FILES or None, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, "Candidate Data Updated")
        else:
            messages.error(request, "Form has errors")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('viewCandidates') + f'?id={candidate.election.id}')


def deleteCandidate(request):
    if request.method != 'POST':
        messages.error(request, "Access Denied")
    try:
        pos = Candidate.objects.get(id=request.POST.get('id'))
        pos.delete()
        messages.success(request, "Candidate Has Been Deleted")
    except:
        messages.error(request, "Access To This Resource Denied")

    return redirect(reverse('viewCandidates') + f'?id={pos.election.id}')


def view_candidate_by_id(request):
    candidate_id = request.GET.get('id', None)
    candidate = Candidate.objects.filter(id=candidate_id)
    context = {}
    if not candidate.exists():
        context['code'] = 404
    else:
        candidate = candidate[0]
        context['code'] = 200
        context['fullname'] = str(candidate.fullname)
        previous = CandidateForm(instance=candidate)
        context['form'] = str(previous.as_p())
    return JsonResponse(context)


def ballot_position(request):
    context = {
        'page_title': "Ballot Position"
    }
    return render(request, "admin/ballot_position.html", context)


def update_ballot_position(request, position_id, up_or_down):
    try:
        context = {
            'error': False
        }
        position = Position.objects.get(id=position_id)
        if up_or_down == 'up':
            priority = position.priority - 1
            if priority == 0:
                context['error'] = True
                output = "This position is already at the top"
            else:
                Position.objects.filter(priority=priority).update(
                    priority=(priority+1))
                position.priority = priority
                position.save()
                output = "Moved Up"
        else:
            priority = position.priority + 1
            if priority > Position.objects.all().count():
                output = "This position is already at the bottom"
                context['error'] = True
            else:
                Position.objects.filter(priority=priority).update(
                    priority=(priority-1))
                position.priority = priority
                position.save()
                output = "Moved Down"
        context['message'] = output
    except Exception as e:
        context['message'] = e

    return JsonResponse(context)


def ballot_title(request):
    from urllib.parse import urlparse
    url = urlparse(request.META['HTTP_REFERER']).path
    from django.urls import resolve
    try:
        redirect_url = resolve(url)
        title = request.POST.get('title', 'No Name')
        file = open(settings.ELECTION_TITLE_PATH, 'w')
        file.write(title)
        file.close()
        messages.success(
            request, "Election title has been changed to " + str(title))
        return redirect(url)
    except Exception as e:
        messages.error(request, e)
        return redirect("/")


def viewVotes(request):
    votes = Votes.objects.all()
    context = {
        'votes': votes,
        'page_title': 'Votes'
    }
    return render(request, "admin/votes.html", context)


def resetVote(request):
    Votes.objects.all().delete()
    Voter.objects.all().update(voted=False)
    messages.success(request, "All votes has been reset")
    return redirect(reverse('viewVotes'))


def committee(request):
    committees = ElectoralCommittee.objects.all()
    committeeForm = CommitteeForms(request.POST or None)
    customUserForm = CustomUserForm(request.POST or None)
    if request.method == "POST":
        if committeeForm.is_valid() and customUserForm.is_valid():
            if committeeForm.cleaned_data["ssc"] == False and committeeForm.cleaned_data["scope"] == None:
                messages.error(request, "SSC field is set to No but no college scope!")
            else:
                user = customUserForm.save(commit=False)
                com = committeeForm.save(commit=False)
                user.user_type = "2"
                user.is_staff = True
                user.save()
                com.fullname = user
                com.save()
                messages.success(request, "Added Electoral Committee.")
        else:
            messages.error(request, "Invalid Form!")
    context = {
        "committeeForm" : committeeForm,
        "userForm" : customUserForm,
        "committees" : committees,
        "page_title" : "Committee"
    }
    return render(request, "admin/committee.html", context)

def committee_delete(request):
    if request.method == "POST":
        com = ElectoralCommittee.objects.get(id=request.POST.get("id"))
        com.delete()
        cstmsr = CustomUser.objects.get(id=com.fullname.id)
        cstmsr.delete()
        messages.success(request, "Deleted Electoral Committee.")
    else:
        messages.error(request, "Access to this resorcce is denied!")
    return redirect(reverse("committee"))


def committee_by_id(request):
    committee_id = request.GET.get('id', None)
    committee = ElectoralCommittee.objects.filter(id=committee_id)
    context = {}
    if not committee.exists():
        context['code'] = 404
    else:
        committee = committee[0]
        context['code'] = 200
        context['first_name'] = committee.fullname.first_name
        context['last_name'] = committee.fullname.last_name
        context['username'] = committee.fullname.username
        context['id'] = committee.id
        previous = CommitteeForms(instance=committee)
        context['form'] = str(previous.as_p())
    return JsonResponse(context)

def update_committee(request):
    if request.method == "POST":
        committee_id = ElectoralCommittee.objects.get(id=request.POST.get("id"))
        form = CustomUserForm(request.POST or None, instance=committee_id.fullname)
        if form.is_valid():
            form.save()
            messages.success(request, "Committee updated!")
        else:
            messages.error(request, "Form validation error!")
    else:
        messages.error(request, "Access to this resource is denied!")
    return redirect(reverse("committee"))