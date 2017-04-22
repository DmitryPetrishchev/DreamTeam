from datetime import date, timedelta
from django import forms
from django.utils.translation import ugettext_lazy as _
from src.models import Task, Roadmap

class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Введите задачу',
            'maxlength': '64'
        })
        self.fields['state'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['roadmap'].widget.attrs.update({
            'class': 'form-control'
        })
    class Meta:
        model = Task
        fields = '__all__'
        widgets = {
            'estimate': forms.SelectDateWidget(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': _('Задача'),
            'estimate': _('Срок выполнения'),
            'state': _('Статус задачи'),
            'roadmap': _('Список задач')
        }

    def clean_estimate(self):
        if self.cleaned_data['estimate'] < date.today():
            raise forms.ValidationError(
                'Можно ввести дату не раньше сегодняшнего дня.')
        return self.cleaned_data['estimate']

    @property
    def is_failed(self):
        return (self.cleaned_data['state'] == "in_progress" and
                self.cleaned_data['estimate'] < date.today())

    @property
    def is_critical(self):
        return (self.is_failed or self.cleaned_data['estimate'] - date.today() <
                timedelta(days=3) and self.cleaned_data['state'] == "in_progress")

class RoadmapForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RoadmapForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Введите название списка задач',
            'maxlength': '64'
        })
    class Meta:
        model = Roadmap
        fields = '__all__'
        labels = {'title': _('Название')}
