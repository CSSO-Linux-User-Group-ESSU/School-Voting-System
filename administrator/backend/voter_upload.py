from account.models import CustomUser
from voting.models import Voter, Course
from voting.forms import *
from django.contrib.auth.hashers import make_password
from pandas import read_excel, notna
from administrator.backend.course_checker import course_checker
from typing import Union

def upload_voters(filepath : str) -> Union[list[str], str]:
    error_student = []
    try:
        data = read_excel(f'./media/{str(filepath)}')
        for i in data.index:
            index = data.loc[i, "NO"]
            section = data.loc[i, "CODE"]
            if section == "Section:":

                course_acrnym = data.loc[i, "NAME"].split(" ")[0]
                full_course_name = course_checker(course_acrnym)
                if not full_course_name:
                    return "Invalid Course"
                
                course = Course.objects.get(course=full_course_name)
                year_level = int(data.loc[i, "NAME"].split(" ")[1][0])
            
            if notna(index):
                try:

                    number = int(index)
                    student_id = data.loc[i, "CODE"]
                    name = data.loc[i, "NAME"].split(",")
                    last_name = name[0].title()
                    _middle_name = name[1].split(" ")[-1].title()
                    first_name = " ".join(name[1].split(" ")[:-1]).strip().title()
                    
                    raw_pass = f"{_middle_name}@{student_id}"

                    userObj = CustomUser.objects.create(
                        password = make_password(raw_pass),
                        first_name = first_name,
                        last_name = last_name,
                        username = f"{student_id}@{_middle_name}",
                    )
                
                    voter = Voter.objects.create(
                        admin = userObj,
                        course = course,
                        id_number = student_id,
                        year_level = year_level,
                        middle_name = _middle_name
                        )

                    voter.save()

                except ValueError as e:
                    print(e)
                    
                except IndexError:
                    error_student.append(str(number))

    except Exception as e:
        return e

    return error_student