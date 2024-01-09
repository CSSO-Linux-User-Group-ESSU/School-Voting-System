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