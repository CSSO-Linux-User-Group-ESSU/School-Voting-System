import csv
from account.models import CustomUser
from voting.models import Voter
from voting.forms import *
from django.contrib.auth.hashers import make_password

def upload_voters(filepath : str) -> None:
    with open(f'./media/{str(filepath)}', "r") as voter_file:
        try:
            users = csv.DictReader(voter_file)
        except Exception as e:
            raise ValueError(e)
        else:
            year_levels = ["First", "Second", "Third", "Fourth"]
            for user in users:
                user_course = Course.objects.get(course=user["Course"])
                int_year_level = int(user['Year'])
                year_level = Voter.YearLevel[year_levels[int_year_level-1]]
                uname = f"{user['mother Maiden Last Name']}.{user['ID Number']}"
            
                userObj = CustomUser.objects.create(
                        password = make_password(uname),
                        first_name = user["First Name"],
                        last_name = user["Last Name"],
                        username = uname,
                        )
                
                voter = Voter.objects.create(
                        admin = userObj,
                        course = user_course,
                        id_number = user["ID Number"],
                        year_level = year_level
                        )

                voter.save()