from urllib.parse import parse_qs

from roadmap import Roadmap

class WSGIApp(object):

    default_headers = [
        ('Content-Type', 'text/html; charset=utf8'),
        ('Server', 'DreamTeam server'),
    ]

    def __init__(self, environment, start_response_callback):
        self.environment = environment
        self.start_response = start_response_callback

    @property
    def params(self):
        params = getattr(self, '_params', None)
        if not params:      # если параметров ещё нет, то парсим их из сроки запроса
            query_string = self.environment.get('QUERY_STRING', '')
            params = {
                key: value if len(value) > 1 else value[0]
                for key, value in parse_qs(query_string).items()
            }
            setattr(self, '_params', params)
        return params


    def __iter__(self):
        self.start_response('200 OK', self.default_headers)

        rm = Roadmap.create_from_file('dataset.yml')

        task_type = self.params.get('type', 'critic')

        if task_type == 'ready':
            page = 'Выполненные'
            tasks = rm.filter('ready')
        elif task_type == 'in_progress':
            page = 'Текущие'
            tasks = rm.filter('in_progress')
        elif task_type == 'failed':
            page = 'Проваленые'
            tasks = [t for t in rm.tasks if t.is_failed]
        else:
            page = 'Критические'
            tasks = [t for t in rm.tasks if t.is_critical]

        page = '<h2>' + page + ' задачи:</h2>\n\n'
        page += '<ul>\n'
        for t in tasks:
            page += '\t<li>' + str(t) + '</li>\n'
        page += '</ul>'

        yield page.encode('utf-8')
