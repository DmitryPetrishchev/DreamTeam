import os
from hashlib import sha256
from datetime import date, datetime, timedelta
from random import randrange
from isoweek import Week
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Count, DateField, ExpressionWrapper, F, Sum, DurationField
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractWeek
from django.views import View
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from src.forms import TaskCreationForm, TaskChangeForm, RoadmapCreationForm, \
                      UserCreationForm, UserChangeForm, PasswordChangeForm, \
                      LoginForm, UploadImageForm
from src.models import Task, Roadmap, Scores

#именно в таком порядке
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import matplotlib.ticker as ticker


@require_GET
@login_required
@transaction.atomic
def generate_tasks(request, *, value):
    """Генерация списка с рандомными решенными и нерешенными задачами."""

    roadmap = Roadmap.objects.create(user=request.user, title='Random roadmap')
    value = int(value)
    if value > 5000:
        value = 5000
    for i in range(value):
        title = 'Random task (num=%s)' % i
        year = randrange(2007, 2017)
        month = randrange(1, 13)
        day = randrange(1, 29)
        estimate = date(year, month, day)
        task = Task.objects.create(title=title, estimate=estimate, roadmap_id=roadmap.id)
        task.create_date = estimate - timedelta(days=randrange(10, 1000))
        task.save()
        if randrange(0, 2):
            task.state = 'ready'
            task.save()
            score = task.scores
            score.date = estimate + timedelta(days=randrange(-10, 11))
            score.save()
    return redirect(reverse('src:main'))


class Login(View):
    """Аутентификация и авторизация."""

    http_method_names = ['get', 'post']

    def get(self, request, error=False):
        """Рендеринг и вывод логин/пароль формы."""

        form = LoginForm()
        return render(request, 'login.html', {
            'form': form,
            'error': error,
        })

    def post(self, request):
        """Валидация формы, авторизация."""

        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)
        if user is not None:
            if not request.POST.get('remember'):
                request.session.set_expiry(0)
            else:
                pass
            login(request, user)
            return redirect(reverse('src:main'))
        else:
            return self.get(request, error=True)


@require_GET
@login_required
def Logout(request):
    """Выход."""

    logout(request)
    return redirect(reverse('src:login'))


class Registration(View):
    """Регистрация пользователя."""

    http_method_names = ['get', 'post']

    def get(self, request):
        """Рендеринг и вывод формы."""

        form = UserCreationForm()
        return render(request, 'registration.html', {
            'form': form,
        })

    def post(self, request):
        """Валидация формы, создание пользователя."""

        form = UserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return redirect(reverse('src:login'))
        else:
            return render(request, 'registration.html', {
                'form': form,
            })


@require_GET
@login_required
def user_profile(request):
    """Просмотр профиля пользователя."""

    form = UploadImageForm()
    return render(request, 'user_profile.html', {
        'user': request.user,
        'form': form,
    })


class UserChange(LoginRequiredMixin, View):
    """Редактирование профиля пользователя."""

    http_method_names = ['get', 'post']

    def get(self, request):
        """Рендеринг, заполнение и вывод формы."""

        request.session['return_path'] = request.META.get('HTTP_REFERER', '/')
        form = UserChangeForm(instance=request.user)
        return render(request, 'user_change.html', {
            'form': form,
            'return_path': request.session['return_path'],
        })

    def post(self, request):
        """Валидация формы, сохранение изменений."""

        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return redirect(request.session['return_path'])
        else:
            return render(request, 'user_change.html', {
                'form': form,
                'return_path': request.session['return_path'],
            })


@require_POST
@login_required
@transaction.atomic
def image_upload(request):
    """Загрузка нового аватара пользователя, удаление старого аватара."""

    form = UploadImageForm(request.POST, request.FILES)
    if form.is_valid():
        user = request.user
        user.image.delete()
        user.image = form.cleaned_data['image']
        user.save()
        return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        raise Http404('Неверный формат изображения.')


@require_POST
@login_required
@transaction.atomic
def image_delete(request):
    """Удаление аватара пользователя."""

    return_path = request.META.get('HTTP_REFERER', '/')
    try:
        value = int(request.POST.get('id', -1))
    except ValueError:
        raise Http404('Ах-хах, хакер, что ты делаешь, прекрати!')
    else:
        if value > 0:
            if value == request.user.id:
                request.user.image.delete()
            else:
                raise Http404('У Вас недостаточно прав на удаление данного изображения.')
        else:
            raise Http404('Запрос не содержит параметра "id".')
    return redirect(return_path)


class PasswordChange(LoginRequiredMixin, View):
    """Изменение пароля пользователя."""

    http_method_names = ['get', 'post']

    def get(self, request):
        """Рендеринг и вывод формы."""

        request.session['return_path'] = request.META.get('HTTP_REFERER', '/')
        form = PasswordChangeForm(user=request.user)
        return render(request, 'password_change.html', {
            'form': form,
            'return_path': request.session['return_path'],
        })

    def post(self, request):
        """Валидация формы и сохранение изменений."""

        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                update_session_auth_hash(request, form.user)
            return redirect(request.session['return_path'])
        else:
            return render(request, 'password_change.html', {
                'form': form,
                'return_path': request.session['return_path'],
            })


@require_GET
@login_required
def main(request):
    """Главная страница."""
    return render(request, 'main.html')


class TaskCreate(LoginRequiredMixin, View):
    """Создание задачи."""

    http_method_names = ['get', 'post']

    def get(self, request):
        """Рендеринг и вывод формы."""

        form = TaskCreationForm(user=request.user)
        return render(request, 'form.html', {
            'form': form,
            'title': 'Создание задачи',
        })

    def post(self, request):
        """Валидация формы и прав доступа, сохранение задачи."""

        form = TaskCreationForm(request.POST, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return render(request, 'success.html', {
                'title': 'Задача создана',
                'title_body': 'Задача успешно создана',
                'form': form,
            })
        else:
            return render(request, 'form.html', {
                'form': form,
                'title': 'Создание задачи',
            })


class RoadmapCreate(LoginRequiredMixin, View):
    """Создание списка задач."""

    http_method_names = ['get', 'post']

    def get(self, request):
        """Рендериг и вывод формы."""

        form = RoadmapCreationForm()
        return render(request, 'form.html', {
            'form': form,
            'title': 'Создание списка задач'
        })

    def post(self, request):
        """Валидация формы, прав доступа, сохранение списка задач."""

        form = RoadmapCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                roadmap = Roadmap(user=request.user)
                form = RoadmapCreationForm(request.POST, instance=roadmap)
                form.save()
            return render(request, 'success.html', {
                'title': 'Список создан',
                'title_body': 'Список задач успешно создан',
                'form': form,
            })
        else:
            return render(request, 'form.html', {
                'form': form,
                'title': 'Создание списка задач',
            })


@require_POST
@login_required
@transaction.atomic
def task_delete(request):
    """Удаление задачи."""

    return_path = request.META.get('HTTP_REFERER', '/')
    try:
        value = int(request.POST.get('id', -1))
    except ValueError:
        raise Http404('Ах-хах, хакер, что ты делаешь, прекрати!')
    else:
        if value > 0:
            task = get_object_or_404(Task, id=value)
            if task.roadmap.user == request.user:
                task.delete()
            else:
                raise Http404('У Вас недостаточно прав на удаление данной задачи.')
        else:
            raise Http404('Запрос не содержит параметра "id".')
    return redirect(return_path)


@require_POST
@login_required
@transaction.atomic
def roadmap_delete(request):
    """Удаление списка задач."""

    return_path = request.META.get('HTTP_REFERER', '/')
    try:
        value = int(request.POST.get('id', -1))
    except ValueError:
        raise Http404('Ах-хах, хакер, что ты делаешь, прекрати!')
    else:
        if value > 0:
            roadmap = get_object_or_404(Roadmap, id=value)
            if roadmap.user == request.user:
                roadmap.delete()
            else:
                raise Http404('У Вас недостаточно прав на удаление данного списка задач.')
        else:
            raise Http404('Запрос не содержит параметра "id".')
    return redirect(return_path)


@require_GET
@login_required
@transaction.atomic
def task_list(request):
    """Вывод всех задач пользователя."""

    tasks = Task.objects.filter(roadmap__user=request.user).order_by('state', 'estimate')
    return render(request, 'task_list.html', {'tasks': tasks})


@require_GET
@login_required
@transaction.atomic
def roadmap_list(request):
    """Вывод всех списков задач пользователя."""

    roadmaps = Roadmap.objects.filter(user=request.user).order_by('title')
    return render(request, 'roadmap_list.html', {'roadmaps': roadmaps})


@require_GET
@login_required
@transaction.atomic
def roadmap_tasks(request, *, value=-1):
    """Вывод всех задач из списка задач, проверка прав доступа."""

    roadmap = get_object_or_404(Roadmap, id=value)
    if roadmap.user != request.user:
        raise Http404('У Вас недостаточно прав для просмотра данного списка задач.')
    if hasattr(roadmap, 'tasks'):
        tasks = roadmap.tasks.order_by('state', 'estimate')
    else:
        tasks = {}
    return render(request, 'task_list.html', {
        'tasks': tasks,
        'return_path': reverse('src:roadmap_list')
    })


class TaskChange(LoginRequiredMixin, View):
    """Редактирвоание задачи."""

    http_method_names = ['get', 'post']

    def get(self, request, *, value=-1):
        """Рендеринг и вывод формы, проверка прав доступа."""

        task = get_object_or_404(Task, id=value)
        if task.roadmap.user != request.user:
            raise Http404('У Вас недостаточно прав для редактирования данной задачи.')
        form = TaskChangeForm(user=request.user, instance=task)
        request.session['return_path'] = request.META.get('HTTP_REFERER', '/')
        return render(request, 'form.html', {
            'title': 'Редактирование задачи',
            'form': form,
            'return_path': request.session['return_path'],
        })

    def post(self, request, *, value=-1):
        """Валидация формы."""

        form = TaskChangeForm(request.POST, user=request.user)
        if form.is_valid():
            task = get_object_or_404(Task, id=value)
            if task.roadmap.user != request.user:
                raise Http404('У Вас недостаточно прав для редактирования данной задачи.')
            form = TaskChangeForm(request.POST, user=request.user, instance=task)
            with transaction.atomic():
                form.save()
            return redirect(request.session['return_path'])
        else:
            return render(request, 'form.html', {
                'title': 'Редактирование задачи',
                'form': form,
                'return_path': request.session['return_path']
            })


class RoadmapStatistics(LoginRequiredMixin, View):
    """Вывод статистики по списку задач."""

    http_method_names = ['get', 'post']

    @transaction.atomic
    def graph_plot(self, user, tasks, scores, year):
        """Построение графиков на стороне сервера, сохранение графиков."""

        if user.statistics:
            user.statistics.delete()

        if int(year):
            fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(20, 25))

            axes[0].hist(
                list(map(lambda x: int(x[0]), tasks.filter(year=year).values_list('week'))),
                bins=range(1, 54),
                facecolor='blue',
                edgecolor='black'
            )
            axes[0].set_title('Статистика созданных задач за %s год' % year)
            axes[0].set_xlabel('Недели')
            axes[0].set_ylabel('Создано')
            axes[0].xaxis.set_major_locator(ticker.MultipleLocator(1))
            axes[0].yaxis.set_major_locator(ticker.MultipleLocator(1))
            axes[0].set_xlim(1, 53)

            axes[1].hist(
                list(map(lambda x: int(x[0]), scores.filter(year=year).values_list('week'))),
                bins=range(1, 54),
                facecolor='green',
                edgecolor='black'
            )
            axes[1].set_title('Статистика решенных задач за %s год' % year)
            axes[1].set_xlabel('Недели')
            axes[1].set_ylabel('Решено')
            axes[1].xaxis.set_major_locator(ticker.MultipleLocator(1))
            axes[1].yaxis.set_major_locator(ticker.MultipleLocator(1))
            axes[1].set_xlim(1, 53)

            x = list(range(1, 54))
            y = []
            for week in x:
                y.append(scores.filter(year=year, week=week).aggregate(sum=Sum('points')).get('sum'))
                if not y[-1]:
                    y[-1] = 0
            axes[2].plot(x, y)
            axes[2].set_title('Статистика заработанных очков за %s год' % year)
            axes[2].set_xlabel('Недели')
            axes[2].set_ylabel('Очки')
            axes[2].text(
                x[0],
                max(y),
                s='Всего заработано %s очков' % sum(y),
                bbox={'facecolor': 'green', 'alpha': 0.5},
                fontsize=16
            )
            axes[2].xaxis.set_major_locator(ticker.MultipleLocator(1))
            axes[2].set_xlim(x[0], x[-1])

            media_path = 'users/statistics/'
            filename = sha256(str(datetime.now()).encode()).hexdigest()
            full_path = os.path.join(settings.MEDIA_ROOT, media_path, filename)
            plt.savefig(full_path, format='png', dpi=300)
            plt.close(fig)

            user.statistics = os.path.join(media_path, filename)
            user.save()
        else:
            fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(20, 25))

            list1 = list(map(lambda x: int(x[0]), tasks.values_list('year')))
            axes[0].hist(
                list1,
                bins=range(min(list1), max(list1) + 1),
                facecolor='blue',
                edgecolor='black'
            )
            axes[0].set_title('Статистика созданных задач за все года')
            axes[0].set_xlabel('Года')
            axes[0].set_ylabel('Создано')
            axes[0].xaxis.set_major_locator(ticker.MultipleLocator(1))
            axes[0].set_xlim(min(list1), max(list1))

            list2 = list(map(lambda x: int(x[0]), scores.values_list('year')))
            axes[1].hist(
                list2,
                bins=range(min(list2), max(list2) + 1),
                facecolor='green',
                edgecolor='black'
            )
            axes[1].set_title('Статистика решенных задач за все года')
            axes[1].set_xlabel('Года')
            axes[1].set_ylabel('Решено')
            axes[1].xaxis.set_major_locator(ticker.MultipleLocator(1))
            axes[1].set_xlim(min(list2), max(list2))

            x = list(range(min(list2), max(list2) + 1))
            y = []
            for i in x:
                y.append(scores.filter(year=i).aggregate(sum=Sum('points')).get('sum'))
                if not y[-1]:
                    y[-1] = 0
            axes[2].plot(x, y)
            axes[2].set_title('Статистика заработанных очков за все года')
            axes[2].set_xlabel('Недели')
            axes[2].set_ylabel('Очки')
            axes[2].text(
                x[0],
                max(y),
                'Всего заработано %s очков' % sum(y),
                bbox={'facecolor': 'green', 'alpha': 0.5},
                fontsize=16
            )
            axes[2].xaxis.set_major_locator(ticker.MultipleLocator(1))
            axes[2].set_xlim(x[0], x[-1])

            media_path = 'users/statistics/'
            filename = sha256(str(datetime.now()).encode()).hexdigest()
            full_path = os.path.join(settings.MEDIA_ROOT, media_path, filename)
            plt.savefig(full_path, format='png', dpi=300)
            plt.close(fig)

            user.statistics = os.path.join(media_path, filename)
            user.save()

    @transaction.atomic
    def get(self, request, *, value=-1, **kwargs):
        """Рендеринг и вывод страницы, проверка прав доступа."""

        roadmap = get_object_or_404(Roadmap, id=value)
        if roadmap.user != request.user:
            raise Http404('У Вас недостаточно прав на просмотр статистики по данному списку задач.')
        if hasattr(roadmap, 'tasks'):
            tasks = roadmap.tasks.only('create_date').annotate(
                year=ExtractYear('create_date'),
                week=ExtractWeek('create_date')
            )
            scores = Scores.objects.filter(task__roadmap=roadmap).only(
                'date',
                'points',
            ).annotate(
                year=ExtractYear(
                    ExpressionWrapper(F('date'), output_field=DateField())
                ),
                month=ExtractMonth(
                    ExpressionWrapper(F('date'), output_field=DateField())
                ),
                week=ExtractWeek(
                    ExpressionWrapper(F('date'), output_field=DateField())
                )
            )
            created_tasks = tasks.values('year', 'week').annotate(created=Count('week'))
            solved_tasks = scores.values('year', 'week').annotate(solved=Count('week'))
            points = scores.values('year', 'month').annotate(
                points=Sum('points')
            ).order_by('year', 'month')

            if kwargs.get('graphs'):
                self.graph_plot(
                    request.user,
                    tasks,
                    scores,
                    kwargs.get('select_year')
                )

            table1 = {}
            for tasks in (created_tasks, solved_tasks):
                for task in tasks:
                    if not table1.get(task.get('year')):
                        table1[task.get('year')] = {}
                    if not table1[task.get('year')].get(task.get('week')):
                        start_date = Week(task.get('year'), task.get('week')).monday()
                        end_date = start_date + timedelta(days=6)
                        dates = str(start_date) + ' / ' + str(end_date)
                        table1[task.get('year')][task.get('week')] = {
                            'dates': dates,
                            'created': 0,
                            'solved': 0
                        }
                    if task.get('created'):
                        table1[task.get('year')][task.get('week')]['created'] = task.get('created')
                    elif task.get('solved'):
                        table1[task.get('year')][task.get('week')]['solved'] = task.get('solved')

            table2 = {}
            for row in points:
                if not table2.get(row.get('year')):
                    table2[row.get('year')] = []
                data = {
                    'month': row.get('month'),
                    'points': row.get('points')
                }
                table2[row.get('year')].append(data)

        else:
            table1 = {}
            table2 = {}

        return render(request, 'roadmap_statistics.html', {
            'data': table1,
            'points': table2,
            'user': request.user,
            'return_path': reverse('src:roadmap_list'),
            'tables': kwargs.get('tables', False),
            'graphs': kwargs.get('graphs', False),
            'select_year': int(kwargs.get('select_year', -1)),
        })

    def post(self, request, *, value=-1):
        """Обработка запроса пользователя."""

        data = {
            'tables': request.POST.get('tables', False),
            'graphs': request.POST.get('graphs', False),
            'select_year': request.POST.get('year', None),
        }

        return self.get(request, value=value, **data)
