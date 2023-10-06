from django.db import models
from account.models import CustomUser
from django import forms

# Create your models here.

class Department(models.Model):
    department = models.CharField(max_length=100, null=False)

    def __str__(self) -> str:
        return self.department

class Course(models.Model):
    course = models.CharField(null=False, max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.course

class Voter(models.Model):
    class YearLevel(models.IntegerChoices):
        First = 1,
        Second = 2,
        Third = 3,
        Fourth = 4

    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    year_level = models.IntegerField(choices=YearLevel.choices)
    voted = models.BooleanField(default=False)
    id_number = models.CharField(null=True, max_length=20)

    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name


class Position(models.Model):
    name = models.CharField(max_length=50, unique=True)
    max_vote = models.IntegerField()
    priority = models.IntegerField()

    def __str__(self):
        return self.name


class Candidate(models.Model):  
    fullname = models.CharField(max_length=50)
    photo = models.ImageField(upload_to="candidates")
    bio = models.TextField()
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

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