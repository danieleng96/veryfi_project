from django import forms
from .models import PersonalFinance, Upload
from crispy_forms.helper import FormHelper

class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ['image']

    #add personal finance form to input user information

required = 'This field is required'

class InputBudget(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
    class Meta:
        model = PersonalFinance
        fields = ['first_name','last_name','monthly_expenses','annual_salary','state']
    
    #add validators

    # first_name = forms.CharField(max_length = 30)
    # last_name = forms.CharField(max_length = 30)
    # monthly_expenses = forms.FloatField()
    # monthly_budget = forms.FloatField()
    # annual_salary = forms.FloatField()
    # state = forms.CharField(label = "State",
    # widget=forms.Select(choices=states))


class SearchUploads(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ['category']

