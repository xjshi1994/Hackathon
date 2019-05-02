from django import forms
from django.forms import widgets
from drchrono.models import List


# Add your forms here

class DemographicForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField(label="E-mail")
    gender = forms.ChoiceField(choices=[('Male', 'male'), ('Female', 'female'), ('Other', 'other')])
    cell_phone = forms.CharField()
    state = forms.ChoiceField(
        choices=[('AL', 'Alabama'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'),
                 ('CT', 'Connecticut'), ('DE', 'Delaware'), ('DC', 'District of Columbia'), ('FL', 'Florida'),
                 ('GA', 'Georgia'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'),
                 ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
                 ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
                 ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'),
                 ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'),
                 ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'),
                 ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'),
                 ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'),
                 ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')])
    address = forms.CharField(widget=forms.Textarea)

    body_weight = forms.IntegerField()
    height = forms.IntegerField()
    blood_pressure = forms.IntegerField()
    heart_rate_bpm = forms.IntegerField()
    body_temperature = forms.FloatField()


class AddForm(forms.Form):
    duration = forms.IntegerField()
    exam_room = forms.IntegerField()
    office = forms.IntegerField()
    patient = forms.IntegerField()
    scheduled_date = forms.DateField(widget=forms.SelectDateWidget)


class ListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ['item', 'finished']
