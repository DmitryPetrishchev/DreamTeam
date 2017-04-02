"""Module provides class "Roadmap"."""
from copy import deepcopy
from datetime import date
from task import Task
from yaml import load, Loader, dump, Dumper


class Roadmap(object):

    def __init__(self, tasks: "list of Task's"=()):
        if all((isinstance(t, Task) for t in tasks)):
            self.tasks = deepcopy(list(tasks))
        else:
            raise TypeError("All items in 'tasks' must have 'Task' type.")

    def __repr__(self) -> str:
        string = ""
        for t in self.tasks:
            string += str(t) + "\n"
        return string

    @property
    def today(self) -> list:
        """Return list of today's tasks."""
        return [t for t in self.tasks if t.estimate == date.today()]

    def filter(self, state: str) -> list:
        """Return list of tasks with setted state."""
        if state in Task.available_states:
            return [t for t in self.tasks if t.state == state]
        else:
            raise ValueError("State '%s' does not exist" % state)

    @classmethod
    def create_from_file(cls, path):
        """Return instance of class from .yaml file."""
        with open(path, "rt", encoding="utf-8") as istream:
            package = load(istream, Loader=Loader)
            dataset = package.get("dataset")
            if not isinstance(dataset, list):
                raise ValueError("Wrong format.")
        rmp = Roadmap()
        rmp.tasks = [Task(t[0], t[2], t[1]) for t in dataset]
        return rmp

    def save(self, path):
        """Write instance of class to .yaml file."""
        package = {'dataset' : [[t.title, t.state, t.estimate] for t in self.tasks]}
        with open(path, "wt", encoding="utf-8") as ostream:
            dump(package, ostream, Dumper=Dumper, default_flow_style=False, allow_unicode=True)
