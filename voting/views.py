from django.shortcuts import render, redirect, reverse
from account.views import account_login
from .models import Position, Candidate, Voter, Votes
from django.http import JsonResponse
from django.utils.text import slugify
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
import requests
import json
from django.core.paginator import Paginator
# Create your views here.


def index(request):
    if not request.user.is_authenticated:
        return account_login(request)
    context = {}
    return render(reverse("show_ballot"))


def generate_ballot(display_controls=False):
    positions = Position.objects.order_by('priority').all()
    output = ""
    has_data = True
    # return None
    if not positions:
        output += "<div id='admin-no-data'><p>Election Hasn't started yet!</p><p>Stay Tuned!!</p></div>"
        has_data = False
    else:
        for position in positions:
            name = position.name
            position_name = slugify(name)
            candidates = Candidate.objects.filter(position=position).order_by("fullname")

            #   Transfer the creation of header to the top instead at the bottom to create a header even though there's no candidate 
            #   so that the ballot can be positioned or arranged
            up = ''
            if position.priority == 1:
                up = 'disabled'
            down = ''
            if position.priority == positions.count():
                down = 'disabled'
            output = output + f"""
                <div class="row">
                    <div class="col-xs-12">
                        <div class="box box-solid" id="{position.id}">
                            <div class="box-header with-border">
                                <h3 class="box-title"><b>{name}</b></h3>"""

            if display_controls:
                output = output + f"""
                                <div class="pull-right box-tools">
                                    <button type="button" class="btn btn-default btn-sm moveup" data-id="{position.id}" {up}><i class="fa fa-arrow-up"></i> </button>
                                    <button type="button" class="btn btn-default btn-sm movedown" data-id="{position.id}" {down}><i class="fa fa-arrow-down"></i></button>
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
                has_data = False
            else:
                for candidate in candidates:
                    candidates_data = ""
                    if position.max_vote > 1:
                        instruction = "You may select up to " + \
                            str(position.max_vote) + " candidates"
                        input_box = '<input type="checkbox" value="'+str(candidate.id)+'" class="flat-red ' + \
                            position_name+'" name="' + \
                            position_name+"[]" + '">'
                    else: 
                        instruction = "Select only one candidate"
                        input_box = '<input value="'+str(candidate.id)+'" type="radio" class="flat-red ' + \
                            position_name+'" name="'+position_name+'" id="'+position_name+str(candidate.id)+'">'
                    image = "/media/" + str(candidate.photo)
                    
                    #Updated html code readability
                    candidates_data = candidates_data + \
                        '<li style="text-align:center;">' + \
                            '<div class="flip-box" id="flip-box'+str(candidate.id)+'">'+\
                                '<div class="flip-box-inner" id="flip-box-inner'+str(candidate.id)+'">'+\
                                    '<div class="flip-box-front">'+\
                                        '<img src="' +image+'" class="candidate-image" onClick="showPlatform('+str(candidate.id)+')">'+\
                                    '</div>'+\
                                    '<div class="flip-box-back" onClick="hidePlatform('+str(candidate.id)+')">'+\
                                        '<h3>Platform</h3>'+\
                                        '<p>'+candidate.bio+'</p>'+\
                                    '</div>'+\
                                '</div>'+\
                            '</div>'+\
                            '<label for="'+position_name+str(candidate.id)+'">'+ input_box+'<span class="cname clist" style="vertical-align:middle;">' +candidate.fullname+'</span></label>' +\
                        '</li>'

                output = output + f"""
                    <p>{instruction}
                    <span class="pull-right">
                        <button type="button" class="btn btn-success btn-sm btn-flat reset" data-desc="{position_name}"><i class="fa fa-refresh"></i> Reset</button>
                    </span>
                    </p>
                    <div>
                        <ul class="candidate-ul">
                            {candidates_data}
                        </ul>
                    </div>
                </div>
                </div>
                </div>
                </div>
                """ 
    return {'html' : output, "has_data" : has_data}


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
    voted_form = voted_candidate_form()
    return render(request, "voting/voter/ballot.html", {"voted_form" : voted_form})

def voted_candidate_form():
    """
    Server-side html creation of voters ballot.
    """
    positions = Position.objects.all().order_by('priority') #Database Query
    form = f"""<div class='col-xs-12' id='forda-modal'>
                    <div class='box box-solid'>
                        <div class='box-header with-border'>
                            <h3 class='box-title'>Voted Candidates</h3>
                        </div>
                    <div class='voted-body'>"""
    
    for pos in positions: #Iterate over the available position and create an html
        candidate_count = Candidate.objects.filter(position=pos).count()
        if candidate_count >= 1:
            form += f"""<div class="candidate-name">
                            <p><b>{pos}</b></p>"""
            for _ in range(pos.max_vote):
                form += f"""<p class="voted" id='{slugify(pos.name+str(pos.id))}'>• None</p>
                            <input name='{slugify(pos.name)}' type='hidden'
                                id='{slugify(pos.name+str(pos.id))}-val'></input>
                        </div>"""
    form += "<a href='#confirm_vote' data-toggle='modal' class='btn btn-success btn-sm btn-flat custom-button' id='cast-modal'>Cast Vote</a></div>"
    return form

def generate_voters_ballot(request):
    queryset = Position.objects.order_by('priority').all()
    html = ""
    candidates_html = ""
    next_page = ""
    if queryset:
        items_per_page = 1
        paginator = Paginator(queryset, items_per_page)
        page_number = request.GET.get('page', 1)
        page = paginator.get_page(page_number)
        candidates = Candidate.objects.filter(position=page[0]).order_by("fullname")
        position = queryset[int(page_number) - 1]
        if page.has_next():
            next_page = f'<button onClick="load_candidate({page.next_page_number()})">Next Position</button>'
        
        position_name = slugify(position)
        if candidates.count() >= 1:
            html+= f"""<div class='col-xs-12'>
                        <div class='box box-solid' id='{position.id}'>
                            <div class='box-header with-border'>
                                <h3 class='box-title'>{position_name.title()}</h3>   
                            </div>"""
            if position.max_vote > 1:
                instruction = "You may select up to" + str(position.max_vote) + "candidates"
            else:
                instruction = "Select only one candidate"
            for cand in candidates:
                paraID = slugify(position_name+str(position.id))
                if position.max_vote > 1:
                    input_box = '<input type="checkbox" value="'+str(cand.id)+'" class="flat-red ' + \
                        position_name+'" name="' + \
                        position_name+"[]" + '">'
                else:
                    input_box = f"""<input value='{str(cand.id)}' type='radio' class='flat-red {position_name}' 
                            name='{position_name}' id='{position_name+str(cand.id)}'
                            onClick="updateVoted('{paraID}', '{cand.fullname}', '{str(cand.id)}')">"""
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
                                        <label for='{position_name}{str(cand.id)}'>{input_box}<span class="cname clist" style="vertical-align:middle;">{cand.fullname}</span></label>
                                    </li>"""
            
            html += f"""<div class='box-body'>
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
            html += "<div id='no-data'><p>No candidate for this position!</p></div>"
    else:
        html += "<div id='no-data'><p>Election Hasn't started yet!</p><p>Stay Tuned!!</p></div>"
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