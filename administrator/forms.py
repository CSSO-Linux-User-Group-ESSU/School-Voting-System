from administrator.models import ElectoralCommittee
from django import forms
from account.forms import FormSettings

class CommitteeForms(FormSettings):
    class Meta:
        model = ElectoralCommittee
        fields = ["ssc", "scope"]
        widgets = {
            "password" : forms.TextInput(attrs={
                "type" : "password"
            })
        }