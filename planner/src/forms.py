from datetime import date
from django import forms

class TaskInputForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Введите задачу'}), label='Задача')
    estimate = forms.DateField(widget=forms.SelectDateWidget(attrs={
        'class': 'form-control'}), label='Срок выполнения')

    def clean_estimate(self):
        if self.cleaned_data['estimate'] < date.today():
            raise forms.ValidationError('Введите правильную дату.')

class TaskEditForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Введите задачу'}), label='Задача')
    available_states = ('in_progress', 'ready')
    visible_states = ('Выполняется', 'Выполнена')
    state = forms.CharField(widget=forms.Select(attrs={
        'class': 'form-control'}, choices=zip(available_states, visible_states)), label='Статус задачи')
    estimate = forms.DateField(widget=forms.SelectDateWidget(attrs={
        'class': 'form-control'}), label='Срок выполнения')

    def clean_estimate(self):
        if self.cleaned_data['estimate'] < date.today():
            raise forms.ValidationError('Введите правильную дату.')
