from .models import Voter,  Election

def access_validator(request : object) -> bool:
    user_data : Voter = Voter.objects.get(id=request.user.id)
    try:
        election_data : Election = Election.objects.filter(started = True)[0]
    except Exception:
        return False
    if election_data.scope == "1":
        return True
    elif election_data.scope == "2":
        return election_data.college_limit.id == user_data.course.college.id
    elif election_data.scope == "3":
        if election_data.course_limit.id == user_data.course.id:
            return election_data.year_level_limit == user_data.year_level
        return False