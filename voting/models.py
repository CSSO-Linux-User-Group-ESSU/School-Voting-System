from django.db import models
from account.models import CustomUser
from django import forms

# Create your models here.

class College(models.Model):
    college = models.CharField(max_length=100, null=False, unique=True)

    def __str__(self) -> str:
        return self.college

class Course(models.Model):
    course = models.CharField(null=False, max_length=50)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.course

class Voter(models.Model):
    class YearLevel(models.IntegerChoices):
        First = 1, "First"
        Second = 2, "Second"
        Third = 3,  "Third"
        Fourth = 4 , "Fourth"

    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    mother_maiden_middle_name = models.CharField(max_length=20)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    year_level = models.IntegerField(choices=YearLevel.choices)
    voted = models.BooleanField(default=False)
    id_number = models.CharField(null=True, max_length=20)

    def save(self, *args, **kwargs):
        self.id = str(self.admin.id)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name


class Position(models.Model):
    name = models.CharField(max_length=50, unique=True)
    max_vote = models.IntegerField()
    representative = models.BooleanField(default=False, choices=[
        (True, "Yes"),
        (False, "No")
    ])
    priority = models.IntegerField()

    def __str__(self):
        return self.name

class Election(models.Model):
    class Scope(models.TextChoices):
        University = '1', 'University' 
        College = '2', 'College'
        Program = '3', 'Program'

    title = models.CharField(max_length=50)
    scope = models.TextField(choices=Scope.choices)
    started = models.BooleanField(default=False)
    college_limit = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)
    course_limit = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    year_level_limit = models.IntegerField(choices=Voter.YearLevel.choices, null=True, blank=True)

    def __str__(self) -> str:
        return self.title
    
class Candidate(models.Model):
    
    fullname = models.ForeignKey(Voter, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=10)
    photo = models.ImageField(upload_to="candidates")
    bio = models.TextField()
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)

    def __str__(self):
        return self.fullname


class Votes(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)


def validate_voter_file(voter_file):
    if not voter_file.name.endswith(".csv"):
        raise forms.ValidationError("Not a csv file")

class UploadFile(models.Model):
    voters_file = models.FileField(upload_to='voters', validators=[validate_voter_file])