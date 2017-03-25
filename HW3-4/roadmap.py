"""This module realise class "Roadmap"."""
from copy import deepcopy
from datetime import date
from task import Task
from yaml import load, Loader


class Roadmap(object):
    """This is class "Roadmap"."""

    def __init__(self, tasks=()):
        """This is constructor of class."""
        self.tasks = deepcopy(list(tasks))

    @property
    def today(self):
        """This function returns today's tasks."""
        return [t for t in self.tasks if t.estimate == date.today()]

    def filter(self, state):
        """This function returns tasks with setted state."""
        if state in Task.available_states:
            return [t for t in self.tasks if t.state == state]
        else:
            raise AttributeError("State '%s' does not exist" % state)

    @classmethod
    def create_from_file(cls, path):
        """Returns instance of class from .yaml file."""
        with open(path, "rt", encoding="utf-8") as istream:
            package = load(istream, Loader=Loader)
            dataset = package.get("dataset")
            if not isinstance(dataset, list):
                raise ValueError("Wrong format")
        rmp = Roadmap()
        rmp.tasks = [Task(t[0], t[2], t[1]) for t in dataset]
        return rmp

    def save(self, path):
        """This function saves example in file."""
        pass
