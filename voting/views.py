from django.shortcuts import render, redirect, reverse
from account.views import account_login
from .models import Position, Candidate, Voter, Votes, Election
from django.http import JsonResponse
from django.utils.text import slugify
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
import requests
import json
from django.core.paginator import Paginator
from voting.validate_access import access_validator
# Create your views here.


def index(request):
    if not request.user.is_authenticated:
        return account_login(request)
    context = {}
    return render(reverse("show_ballot"))


def generate_ballot(display_controls=False):
    output = ""
    if Election.objects.filter(started = True).count() == 0:
        output += "<div id='admin-no-data'><p>Election Hasn't started yet!</p><p>Stay Tuned!!</p></div>"
        print("Hello world")
    else:
        election_id = Election.objects.get(started=True)
        distinct_positions = Position.objects.filter(candidate__election_id=election_id).distinct().order_by('priority')
        for pos in distinct_positions:
            candidates = Candidate.objects.filter(election_id=election_id, position=pos).order_by('fullname')
            posistion_name = slugify(pos.name)
            up=''
            if pos.priority == 1:
                up = 'disabled'
            down=''
            if pos.priority == distinct_positions.count():
                down = 'disabled'
            output += f"""
                <div class="row">
                    <div class="col-xs-12">
                        <div class="box box-solid" id="{pos.id}">
                            <div class="box-header with-border">
                                <h3 class="box-title"><b>{posistion_name}</b></h3> """
            if display_controls:
                output = output + f"""
                                <div class="pull-right box-tools">
                                    <button type="button" class="btn btn-default btn-sm moveup" data-id="{pos.id}" {up}><i class="fa fa-arrow-up"></i> </button>
                                    <button type="button" class="btn btn-default btn-sm movedown" data-id="{pos.id}" {down}><i class="fa fa-arrow-down"></i></button>
                                </div>"""
            output += """   </div>
                            <div class="box-body">"""
            if not candidates:
                output += """   <div id='admin-no-data'>
                                    <p>No candidate for this position!</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>"""
            else:
                candidate_data = ""
                for candidate in candidates:
                    image = "/media/" + str(candidate.photo)

                    candidate_data += f"""
                        <li style="text-align:center;">
                            <div class="flip-box" id="flip-box{str(candidate.id)}">
                                <div class="flip-box-inner" id="flip-box-inner{str(candidate.id)}">
                                    <div class="flip-box-front">
                                        <img src="{image}" class="candidate-image" onClick="showPlatform('{str(candidate.id)}')">
                                    </div>
                                    <div class="flip-box-back" onClick="hidePlatform('{str(candidate.id)}')">
                                        <h3>Platform</h3>
                                        <p>{candidate.bio}</p>
                                    </div>
                                </div>
                            </div>
                            <label><span class="cname clist" style="vertical-align:middle;">{candidate.fullname}</span></label>
                        </li>"""
                
                output += f"""
                    <div>
                        <ul class="candidate-ul">
                            {candidate_data}
                        </ul>
                    </div>
                </div>
                </div>
                </div>
                </div>
                """  
    return output


def fetch_ballot(request):
    output = generate_ballot(display_controls=True)
    return JsonResponse(output, safe=False)

def dashboard(request):
    user = request.user
    if user.voter.voted:  # * User has voted
        # To display election result or candidates I voted for ?
        context = {
            'my_votes': Votes.objects.filter(voter=user.voter),
        }
        return render(request, "voting/voter/result.html", context)
    else:
        return redirect(reverse('show_ballot'))


def show_ballot(request):
    if request.user.voter.voted:
        messages.error(request, "You have voted already")
        return redirect(reverse('voterDashboard'))
    if Election.objects.filter(started=True).count() <= 0:
        messages.error(request, "No on-going electtion.")
        redirect_url = reverse("accessDenied")
        return redirect(f"{redirect_url}?error_message=Election hasn't started yet!")
    if not access_validator(request):
        messages.error(request, "Access Denied!")
        redirect_url = reverse("accessDenied")
        return redirect(f"{redirect_url}?error_message=You are not allowed in this election!")
    voted_form = voted_candidate_form(request)
    return render(request, "voting/voter/ballot.html", {"voted_form" : voted_form})

def voted_candidate_form(request):
    """
    Server-side html creation of voters ballot.
    """
    election_id : Election = Election.objects.get(started=True)
    positions : Position = Position.objects.filter(candidate__election_id=election_id).distinct().order_by('priority')
    
    temp_form = ""
    for pos in positions: #Iterate over the available position and create an html
        candidates = Candidate.objects.filter(position=pos, election=election_id)
        if pos.representative:
            same_course_count = [i for i in candidates if Voter.objects.get(id_number=i.student_id).course == Voter.objects.get(id=request.user.id).course]
            same_course_year_level = [i for i in candidates 
                                      if Voter.objects.get(id_number=i.student_id).year_level == Voter.objects.get(id=request.user.id).year_level 
                                      and Voter.objects.get(id_number=i.student_id).course == Voter.objects.get(id=request.user.id).course]
            if election_id.scope == "1":
                if len(same_course_count) <= 0:
                    continue
            elif election_id.scope =="2":
                if len(same_course_year_level) <= 0:
                    continue
        if candidates.count() >= 1:
            temp_form += f"""<div class="candidate-name">
                            <p><b>{pos}</b></p>"""
            for _ in range(pos.max_vote):
                temp_form += f"""<p class="voted" id='{slugify(pos.name+str(pos.id))}'>• None</p>
                            <input name='{slugify(pos.name)}' type='hidden'
                                id='{slugify(pos.name+str(pos.id))}-val'></input>"""
                temp_form += "</div>"
    if temp_form:
        form = f"""<div class='col-xs-12' id='forda-modal'>
                <div class='box box-solid'>
                    <div class='box-header with-border'>
                        <h3 class='box-title'>Voted Candidates</h3>
                    </div>
                <div class='voted-body'>
                    {temp_form}
                    <a href='#confirm_vote' data-toggle='modal' class='btn btn-success btn-sm btn-flat custom-button' id='cast-modal'>Cast Vote</a>
                </div>"""
    else:
        form = f"""<div class='col-xs-12' id='forda-modal'>
                <div class='box box-solid'>
                    <div class='box-header with-border'>
                        <h3 class='box-title'>Voted Candidates</h3>
                    </div>
                <div class='voted-body'>
                    <h5>There's no candidate for your course or year level:(</h5>
                </div>"""
    return form

def generate_voters_ballot(request : object):
    html : str = ""
    candidates_html : str = ""
    next_page : str = ""

    election_id : Election = Election.objects.get(started=True)
    distinct_positions : Position = Position.objects.filter(candidate__election_id=election_id).distinct().order_by('priority')
    if distinct_positions:
        items_per_page : int = 1
        paginator : Paginator = Paginator(distinct_positions, items_per_page)
        page_number : int = request.GET.get('page', 1)
        page : Paginator = paginator.get_page(page_number)
        candidates : Candidate = Candidate.objects.filter(election_id=election_id, position=page[0]).order_by('fullname')
        position : Position = distinct_positions[int(page_number) - 1]
        if page.has_next():
            next_page = f'<button onClick="load_candidate({page.next_page_number()})">Next Position</button>'
        
        position_name : str = slugify(position)
        
        if position.max_vote > 1:
            instruction = "You may select up to" + str(position.max_vote) + "candidates"
        else:
            instruction = "Select only one candidate"
        for cand in candidates:
            candidate_data = Voter.objects.get(id_number=cand.student_id)
            if position.representative:
                user_data = Voter.objects.get(id=request.user.id)
                if election_id.scope == "1":
                    if user_data.course.college.id != candidate_data.course.college.id:
                        continue
                elif election_id.scope == "2":
                    if user_data.course != candidate_data.course or user_data.year_level != candidate_data.year_level:
                        continue
                elif election_id.scope == "3":
                    if user_data.year_level != candidate_data.year_level:
                        continue
            paraID : str = slugify(position_name+str(position.id))
            if position.max_vote > 1:
                input_box = '<input type="checkbox" value="'+str(cand.id)+'" class="flat-red ' + \
                    position_name+'" name="' + \
                    position_name+"[]" + '">'
            else:
                input_box = f"""<input value='{str(cand.id)}' type='radio' class='flat-red {position_name}' 
                        name='{position_name}' id='{position_name+str(cand.id)}input'
                        onClick="updateVoted('{paraID}', '{cand.fullname}', '{str(cand.id)}', '{position_name+str(cand.id)}input')">"""
            image = '/media/' + str(cand.photo)
            candidates_html += f"""<li style='text-align:center;'>
                                    <div class='flip-box' id='flip-box{str(cand.id)}'>
                                        <div class='flip-box-inner' id='flip-box-inner{str(cand.id)}'>
                                            <div class='flip-box-front'>
                                                <img src='{image}' class='candidate-image' onClick='showPlatform({str(cand.id)})'/>
                                            </div>
                                            <div class='flip-box-back' onClick='hidePlatform({str(cand.id)})'>
                                                <h3>Platform<h3>
                                                <p>{cand.bio}</p>
                                            </div>
                                        </div>
                                    </div>
                                    <label for='{position_name}{str(cand.id)}input'>{input_box}<span class="cname clist" style="vertical-align:middle;">{cand.fullname}</span></label>
                                </li>"""
        if candidates_html:
            html += f"""
                <div class="col-xs-12">
                    <div class="box box-solid" id="{position.id}">
                        <div class="box-header with-border">
                            <h3 class="box-title">{position_name.title()}</h3>
                        </div>
                        <div class='box-body'>
                            <p>{instruction}
                                <span class='pull-right'>
                                    <button type="button" onClick='updateVoted("{paraID}")' class="btn btn-success btn-sm btn-flat reset" data-desc="{position_name}"><i class="fa fa-refresh"></i> Reset</button>
                                </span>
                            </p>
                            <div class='candidate-ul'>
                                {candidates_html}
                            </div>
                        </div>
                    </div>
                </div>"""
    else:
        html += "<div id='no-data'><p>Stay Tuned!</p></div>"
    
    return JsonResponse({"html" : html, "next_button" : next_page}, safe=False)
    
def preview_vote(request):
    if request.method != 'POST':
        error = True
        response = "Please browse the system properly"
    else:
        output = ""
        form = dict(request.POST)
        # We don't need to loop over CSRF token
        form.pop('csrfmiddlewaretoken', None)
        error = False
        data = []
        positions = Position.objects.all()
        for position in positions:
            max_vote = position.max_vote
            pos = slugify(position.name)
            pos_id = position.id
            if position.max_vote > 1:
                this_key = pos + "[]"
                form_position = form.get(this_key)
                if form_position is None:
                    continue
                if len(form_position) > max_vote:
                    error = True
                    response = "You can only choose " + \
                        str(max_vote) + " candidates for " + position.name
                else:
                    # for key, value in form.items():
                    start_tag = f"""
                       <div class='row votelist' style='padding-bottom: 2px'>
		                      	<span class='col-sm-4'><span class='pull-right'><b>{position.name} :</b></span></span>
		                      	<span class='col-sm-8'>
                                <ul style='list-style-type:none; margin-left:-40px'>
                                
                    
                    """
                    end_tag = "</ul></span></div><hr/>"
                    data = ""
                    for form_candidate_id in form_position:
                        try:
                            candidate = Candidate.objects.get(
                                id=form_candidate_id, position=position)
                            data += f"""
		                      	<li><i class="fa fa-check-square-o"></i> {candidate.fullname}</li>
                            """
                        except:
                            error = True
                            response = "Please, browse the system properly"
                    output += start_tag + data + end_tag
            else:
                this_key = pos
                form_position = form.get(this_key)
                if form_position is None:
                    continue
                # Max Vote == 1
                try:
                    form_position = form_position[0]
                    candidate = Candidate.objects.get(
                        position=position, id=form_position)
                    output += f"""
                            <div class='row votelist' style='padding-bottom: 2px'>
		                      	<span class='col-sm-4'><span class='pull-right'><b>{position.name} :</b></span></span>
		                      	<span class='col-sm-8'><i class="fa fa-check-circle-o"></i> {candidate.fullname}</span>
		                    </div>
                      <hr/>
                    """
                except Exception as e:
                    error = True
                    response = "Please, browse the system properly"
    context = {
        'error': error,
        'list': output
    }
    return JsonResponse(context, safe=False)


def submit_ballot(request):
    if request.method != 'POST':
        messages.error(request, "Please, browse the system properly")
        return redirect(reverse('show_ballot'))

    # Verify if the voter has voted or not
    voter = request.user.voter
    if voter.voted:
        messages.error(request, "You have voted already")
        return redirect(reverse('voterDashboard'))

    form = dict(request.POST)
    form.pop('csrfmiddlewaretoken', None)  # Pop CSRF Token
    form.pop('submit_vote', None)  # Pop Submit Button
    
    #Check if form is empty since this isn't a radio anymore
    form = {submitted: form[submitted] for submitted in form if form[submitted][0]}

    # Ensure at least one vote is selected
    if len(form.keys()) < 1:
        messages.error(request, "Please select at least one candidate")
        return redirect(reverse('show_ballot'))
    positions = Position.objects.all()
    form_count = 0
    for position in positions:
        max_vote = position.max_vote
        pos = slugify(position.name)
        pos_id = position.id
        if position.max_vote > 1:
            this_key = pos + "[]"
            form_position = form.get(this_key)
            if form_position is None:
                continue
            if len(form_position) > max_vote:
                messages.error(request, "You can only choose " +
                               str(max_vote) + " candidates for " + position.name)
                return redirect(reverse('show_ballot'))
            else:
                for form_candidate_id in form_position:
                    form_count += 1
                    try:
                        candidate = Candidate.objects.get(
                            id=form_candidate_id, position=position)
                        vote = Votes()
                        vote.candidate = candidate
                        vote.voter = voter
                        vote.position = position
                        vote.save()
                    except Exception as e:
                        messages.error(
                            request, "Please, browse the system properly " + str(e))
                        return redirect(reverse('show_ballot'))
        else:
            this_key = pos
            form_position = form.get(this_key)
            if form_position is None:
                continue
            # Max Vote == 1
            form_count += 1
            try:
                form_position = form_position[0]
                candidate = Candidate.objects.get(
                    position=position, id=form_position)
                vote = Votes()
                vote.candidate = candidate
                vote.voter = voter
                vote.position = position
                vote.save()
            except Exception as e:
                messages.error(
                    request, "Please, browse the system properly " + str(e))
                return redirect(reverse('show_ballot'))
    # Count total number of records inserted
    # Check it viz-a-viz form_count
    inserted_votes = Votes.objects.filter(voter=voter)
    if (inserted_votes.count() != form_count):
        # Delete
        inserted_votes.delete()
        messages.error(request, "Please try voting again!")
        return redirect(reverse('show_ballot'))
    else:
        # Update Voter profile to voted
        voter.voted = True
        voter.save()
        messages.success(request, "Thanks for voting")
        return redirect(reverse('voterDashboard'))

def noaccess(request):
    if not access_validator(request):
        message_err = request.GET.get("error_message")
        context = {
            "message_err" : message_err.replace("'", "")
        }
        return render(request, "voting/voter/noaccess.html", context)
    return redirect(reverse("show_ballot"))