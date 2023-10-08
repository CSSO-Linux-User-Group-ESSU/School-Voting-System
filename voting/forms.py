from django import forms
from .models import *
from account.forms import FormSettings


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadFile
        fields = ['voters_file']
        widgets = {
            'voters_file' : forms.FileInput(attrs={
                'accept' : '.csv',
                'onchange' : 'changeUploadicon()'
            })
        }

class VoterForm(FormSettings):
    class Meta:
        model = Voter
        fields = ['id_number', 'course', 'year_level']
        widgets = {
            'id_number' : forms.TextInput(attrs= {
                'onkeyup' : 'updateUsername()'
            })
        }


class PositionForm(FormSettings):
    class Meta:
        model = Position
        fields = ['name', 'max_vote']


class CandidateForm(FormSettings):
    class Meta:
        model = Candidate
        fields = ['fullname', 'bio', 'position', 'photo']

class CourseForm(FormSettings):
    class Meta:
        model = Course
        fields = ['course', 'department']

        widgets = {
            'course' : forms.TextInput(attrs={
                'placeholder' : 'BS in ... or BE in ...'
            })
        }


class DepartmentForm(FormSettings):
    class Meta:
        model = Department
        fields = ['department']

        widgets = {
            'department' : forms.TextInput(attrs={
                'placeholder' : "College of ..."
            })
        }