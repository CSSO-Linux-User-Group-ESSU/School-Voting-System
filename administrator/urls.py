from django.urls import path
from . import views
from administrator.backend import (
    ElectionStop, ElectionStart, College, CollegeRemover, Dashboard, Course, CourseRemover,
    Voters, BulkUpload, VoterAjax, PositionAjax
)


urlpatterns = [
    path('', Dashboard.dashboard, name="adminDashboard"),
    # * Voters
    path('voters', Voters.voters, name="adminViewVoters"),
    path('voters/view', VoterAjax.view_voter_by_id, name="viewVoter"),
    path('voters/delete', views.deleteVoter, name='deleteVoter'),
    path('voters/update', views.updateVoter, name="updateVoter"),
    path("voters/upload", BulkUpload.uploadUser, name="uploadUser"),
    
    #Added path for managing the course
    path("voters/course", Course.course, name="course"),
    path("voters/colleges", College.colleges, name="colleges"), 
    path("voters/course/delete", CourseRemover.delete_course, name="deleteCourse"),
    path("voters/college/delete", CollegeRemover.remove_college, name="removeCollege"),   

    # * Position
    path('position/view', PositionAjax.view_position_by_id, name="viewPosition"),
    path('position/update', views.updatePosition, name="updatePosition"),
    path('position/delete', views.deletePosition, name='deletePosition'),
    path('positions/view', views.viewPositions, name='viewPositions'),

    # * Candidate
    path('candidate/', views.viewCandidates, name='viewCandidates'),
    path('candidate/update', views.updateCandidate, name="updateCandidate"),
    path('candidate/delete', views.deleteCandidate, name='deleteCandidate'),
    path('candidate/view', views.view_candidate_by_id, name='viewCandidate'),

    # * Election
    path('election/select', views.viewElections, name="viewElections"),
    path('election/delete', views.delete_election, name="deleteElection"),
    path('election/select/id', views.election_by_id, name="viewElection"),
    path('election/start', ElectionStart.startElection, name="startElection"),
    path('election/stop', ElectionStop.stoper, name="stopElection"),


    # * Settings (Ballot Position and Election Title)
    path("settings/ballot/position", views.ballot_position, name='ballot_position'),
    path("settings/ballot/title/", views.ballot_title, name='ballot_title'),
    path("settings/ballot/position/update/<int:position_id>/<str:up_or_down>/",
         views.update_ballot_position, name='update_ballot_position'),

    # * Votes
    path('votes/view', views.viewVotes, name='viewVotes'),
    path('votes/reset/', views.resetVote, name='resetVote'),
    path('votes/print/', views.PrintView.as_view(), name='printResult'), 

    # * Committe
    path("committe/manage", views.committee, name="committee"),
    path("committee/delte", views.committee_delete, name="deleteCommittee"),
    path("committe/by_id", views.committee_by_id, name="committeeById"),
    path("committee/update", views.update_committee, name="committeeUpdate") 

]
