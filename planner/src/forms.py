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
            'maxlength': '32',
        })
        setattr(self.fields['email'], 'error_messages', {
            'unique': 'Пользователь с таким электронным адресом уже существует.'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите имя',
            'maxlength': '32',
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите фамилию',
            'maxlength': '32',
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите телефон',
            'maxlength': '16',
        })
        self.fields['age'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите возраст',
            'maxlength': '3',
        })
        self.fields['region'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите регион',
            'maxlength': '32',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль',
            'maxlength': '16',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтвердите пароль',
            'maxlength': '16',
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
            'type': 'login',
            'maxlength': '32',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите пароль',
            'type': 'password',
            'maxlength': '16',
        })
    email = forms.CharField(max_length=32, label='E-mail', widget=forms.EmailInput)
    password = forms.CharField(max_length=16, label='Пароль', widget=forms.PasswordInput)


class PasswordChangeForm(auth_forms.PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите текущий пароль',
            'maxlength': '16',
        })
        self.fields['old_password'].label = 'Текущий пароль'
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите новый пароль',
            'maxlength': '16',
        })
        self.fields['new_password1'].label = 'Новый пароль'
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтвердите новый пароль',
            'maxlength': '16',
        })
        self.fields['new_password2'].label = 'Подтверждение пароля'


class UserChangeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите ваш e-mail',
            'maxlength': '32',
        })
        setattr(self.fields['email'], 'error_messages', {
            'unique': 'Пользователь с таким электронным адресом уже существует.'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите имя',
            'maxlength': '32',
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите фамилию',
            'maxlength': '32',
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите телефон',
            'maxlength': '16',
        })
        self.fields['age'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите возраст',
            'maxlength': '3',
        })
        self.fields['region'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите регион',
            'maxlength': '32',
        })
    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'phone',
            'age',
            'region',
        ]
        labels = {
            'email': _('E-mail'),
            'first_name': _('Имя'),
            'last_name': _('Фамилия'),
            'phone': _('Телефон'),
            'age': _('Возраст'),
            'region': _('Регион'),
        }

class TaskCreationForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super(TaskCreationForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите задачу',
            'maxlength': '32'
        })
        self.fields['roadmap'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['roadmap'].queryset = Roadmap.objects.filter(user=user)
    class Meta:
        model = Task
        fields = [
            'title',
            'estimate',
            'roadmap',
        ]
        widgets = {
            'estimate': forms.SelectDateWidget(attrs={'class': 'form-control'})
        }
        labels = {
            'title': _('Задача'),
            'estimate': _('Срок выполнения'),
            'roadmap': _('Список задач')
        }

    def clean_estimate(self):
        if self.cleaned_data['estimate'] < date.today():
            raise forms.ValidationError(
                'Можно ввести дату не раньше сегодняшнего дня.'
            )
        return self.cleaned_data['estimate']

class TaskChangeForm(TaskCreationForm):
    def __init__(self, *args, **kwargs):
        super(TaskChangeForm, self).__init__(*args, **kwargs)
        self.fields['state'].widget.attrs.update({
            'class': 'form-control',
        })
    class Meta(TaskCreationForm.Meta):
        model = Task
        fields = TaskCreationForm.Meta.fields + ['state',]
        labels = TaskCreationForm.Meta.labels
        labels.update({'state': _('Статус задачи')})


class RoadmapCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RoadmapCreationForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите название списка задач',
            'maxlength': '64',
        })
    class Meta:
        model = Roadmap
        fields = ['title',]
        labels = {
            'title': _('Название'),
        }

class UploadImageForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(UploadImageForm, self).__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update({
            'class': 'form-control',
        })
        self.fields['image'].label = 'Выберите файл'
    image = forms.ImageField()
