import csv
from account.models import CustomUser
from voting.models import Voter
from voting.forms import *
from django.contrib.auth.hashers import make_password

def upload_voters(filepath : str) -> None:
    with open(f'./media/{str(filepath)}', "r") as voter_file:
        users = csv.DictReader(voter_file)
        for user in users:
            user_course = Course.objects.get(course=user["Course"])
            year_level = Voter.YearLevel[user['Year']]
            uname = f"{str(user['Last name']).lower()}.{str(user['First name']).lower().replace(' ', '')}"
        
            userObj = CustomUser.objects.create(
                    password = make_password(user["ID number"]),
                    first_name = user["First name"],
                    last_name = user["Last name"],
                    username = uname
                    )
            
            voter = Voter.objects.create(
                    admin = userObj,
                    course = user_course,
                    id_number = user["ID number"],
                    year_level = year_level
                    )

            voter.save()