from urllib.parse import parse_qs
from roadmap import Roadmap

class WSGIApp(object):

    def __init__(self, environment, start_response):
        self.environment = environment
        self.start_response = start_response
        self._params = None

    @property
    def params(self):
        if not self._params:      # если параметров ещё нет, то парсим их из сроки запроса
            query_string = self.environment.get("QUERY_STRING", "")
            self._params = {key : value if len(value) > 1 else value[0]
                            for (key, value) in parse_qs(query_string).items()}
        return self._params

    def __iter__(self):
        status = "200 OK"
        headers = [("Content-Type", "text/html; charset=utf8"),
                   ("Server", "DreamTeam server")]

        self.start_response(status, headers)

        rmp = Roadmap.create_from_file("dataset.yml")
        task_type = self.params.get("type", "critical")

        if task_type == "ready":
            page = "Выполненные"
            tasks = rmp.filter("ready")
        elif task_type == "in_progress":
            page = "Текущие"
            tasks = rmp.filter("in_progress")
        elif task_type == "failed":
            page = "Проваленные"
            tasks = [t for t in rmp.tasks if t.is_failed]
        elif task_type == "critical":
            page = "Критические"
            tasks = [t for t in rmp.tasks if t.is_critical]
        else:
            page = "<h2>Ошибка:</h2>" + \
                   "<p>Упс, такая страница не существует. " + \
                   "Возможные значения /?type = {ready, in_progress, failed, critical}</p>"
            yield page.encode("utf-8")

        page = "<h2>" + page + " задачи:</h2>\n\n"
        page += "<ul>\n"
        for t in tasks:
            page += "\t<li>" + str(t) + "</li>\n"
        page += "</ul>"

        yield page.encode("utf-8")
