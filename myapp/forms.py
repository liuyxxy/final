from django import forms

DEMO_CHOICES =( 
    ("1", "20s"), 
    ("2", "30s"), 
    ("3", "40s"), 
)

class CreateHostForm(forms.Form):
    hostname = forms.CharField(label="hostname", max_length=100)
    num_rounds = forms.IntegerField(label='num_rounds')
    time = forms.ChoiceField(choices = DEMO_CHOICES, label='time')
    
class CreatePlayerForm(forms.Form):
    playername=forms.CharField(label="playername", max_length=100)
    
class CreateSentenceForm(forms.Form):
    body=forms.CharField(label="body", max_length=1000000, widget=forms.Textarea)