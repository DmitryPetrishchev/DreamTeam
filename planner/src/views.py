from django.shortcuts import render
from src.forms import TaskInputForm, TaskEditForm

def task_input_form(request):
    form = TaskInputForm()
    return render(request, 'input_form.html', {'form': form, 'title': 'Добавление задачи'})

def task_edit_form(request):
    form = TaskEditForm()
    return render(request, 'input_form.html', {'form': form, 'title': 'Редактирование задачи'})
