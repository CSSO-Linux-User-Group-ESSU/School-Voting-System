from django import forms
from .models import *


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Here make some changes such as:
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


#Changes here are mainly all about email switching to username
class CustomUserForm(FormSettings):
    username = forms.CharField(required=True)
    # email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    widget = {
        'password': forms.PasswordInput(),
    }

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)
        if kwargs.get('instance'):
            instance = kwargs.get('instance').__dict__
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"
        else:
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True

    def clean_username(self, *args, **kwargs):
        formUsername = self.cleaned_data['username'].lower()
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(username=formUsername).exists():
                raise forms.ValidationError(
                    "The given username is already registered")
        else:  # Update
            dbUsername = self.Meta.model.objects.get(
                id=self.instance.pk).username.lower()
            if dbUsername != formUsername:  # There has been changes
                if CustomUser.objects.filter(username=formUsername).exists():
                    raise forms.ValidationError(
                        "The given username is already registered")
        return formUsername

    def clean_password(self):
        password = self.cleaned_data.get("password", None)
        if self.instance.pk is not None:
            if not password:
                # return None
                return self.instance.password

        return make_password(password)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'password' ]