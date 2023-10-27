from django.db import models
from account.models import CustomUser
from voting.models import College
# Create your models here.

class ElectoralCommittee(models.Model):
    fullname = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    ssc = models.BooleanField(choices=[
        (True, "Yes"),
        (False, "No")
    ])
    scope = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return self.fullname