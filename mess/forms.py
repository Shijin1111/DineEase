from django import forms

class Mess_out_form(forms.Form):
    start_date = forms.DateField(label="start date",widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label="end date",widget=forms.DateInput(attrs={'type': 'date'}))