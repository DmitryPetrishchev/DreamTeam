from datetime import date, timedelta
from django import forms
from django.contrib.auth import forms as auth_forms
from django.utils.translation import ugettext_lazy as _
from src.models import Task, Roadmap, User

class UserCreationForm(auth_forms.UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите ваш e-mail',
            'maxlength': '32'
        })
        setattr(self.fields['email'], 'error_messages', {
            'unique': 'Пользователь с таким адресом уже существует.'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите имя',
            'maxlength': '32'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите фамилию',
            'maxlength': '32'
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите телефон',
            'maxlength': '16'
        })
        self.fields['age'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите возраст',
            'maxlength': '3'
        })
        self.fields['region'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите регион',
            'maxlength': '64'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль',
        })

    class Meta(auth_forms.UserCreationForm.Meta):
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'phone',
            'age',
            'region',
            'password1',
            'password2',
        ]
        labels = {
            'email': _('E-mail'),
            'first_name': _('Имя'),
            'last_name': _('Фамилия'),
            'phone': _('Телефон'),
            'age': _('Возраст'),
            'region': _('Регион'),
            'password1': _('Пароль'),
            'password2': _('Подтверждение пароля'),
        }

class LoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите e-mail',
            'maxlength': '32',
            'type': 'login',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль',
            'type': 'password',
        })
    email = forms.CharField(max_length=32, label='E-mail', widget=forms.EmailInput)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

class PasswordChangeForm(auth_forms.PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите текущий пароль',
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите новый пароль',
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтвердите новый пароль',
        })
    class Meta:
        fields = ['__all__']
        labels = {
            'old_password': _('Текущий пароль'),
            'new_password1': _('Новый пароль'),
            'new_password2': _('Подтверждение'),
        }

class TaskForm(forms.ModelForm):
    def __init__(self, *args, hidden=False, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите задачу',
            'maxlength': '64'
        })
        self.fields['state'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['roadmap'].widget.attrs.update({
            'class': 'form-control'
        })

        if hidden:
            self.fields['state'].widget = forms.HiddenInput()

    class Meta:
        model = Task
        fields = '__all__'
        widgets = {
            'estimate': forms.SelectDateWidget(attrs={'class': 'form-control'})
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
                'Можно ввести дату не раньше сегодняшнего дня.'
            )
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
            'class': 'form-control',
            'placeholder': 'Введите название списка задач',
            'maxlength': '64'
        })

    class Meta:
        model = Roadmap
        fields = '__all__'
        labels = {
            'title': _('Название')
        }
