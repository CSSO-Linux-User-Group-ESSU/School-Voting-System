from django.db import models
from account.models import CustomUser
from django import forms

# Create your models here.

class College(models.Model):
    college = models.CharField(max_length=100, null=False)

    def __str__(self) -> str:
        return self.college

class Course(models.Model):
    course = models.CharField(null=False, max_length=50)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    
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

class Election(models.Model):
    class Scope(models.TextChoices):
        University = 1,
        College = 2,
        Program = 3

    title = models.CharField(max_length=50)
    scope = models.TextField(choices=Scope.choices)
    started = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title
    
class Candidate(models.Model):
    
    fullname = models.ForeignKey(Voter, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="candidates")
    bio = models.TextField()
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    scope = models.BooleanField(default=False)

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