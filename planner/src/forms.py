from django import forms
from datetime import date

class TaskInputForm(forms.Form):
    title = forms.CharField(max_length=20, label='Название')
    estimate = forms.DateTimeField(widget=CalendarWidget, label='Срок выполнения')

    def clean_estimate(self):
        if self.cleaned_data['estimate'] < date.today():
            raise forms.ValidationError('Проверьте значение поля')

class TaskEditForm(forms.Form):
    title = forms.CharField(max_length=20, label='Название')
    available_states = ('ready', 'in_progress')
    output = ('Выполняется', 'Выполнена')
    state = forms.ChoiceField(zip(available_states, output), label='Статус')
    estimate = forms.DateTimeField(label='Срок выполнения')
