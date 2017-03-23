"""This module realise class "Roadmap"."""
from copy import deepcopy
from datetime import date
from task import Task
from yaml import load
from yaml import Loader


class Roadmap(object):
    """This is class "Roadmap"."""

    def __init__(self, tasks=[]):
        """This is constructor of class."""
        self.tasks = deepcopy(tasks)

    @property
    def today(self):
        """This function returns today's tasks."""
        return [t for t in self.tasks if t.estimate == date.today()]

    def filter(self, state):
        """This function returns tasks with setted state."""
        if state in Task.__availableStates:
            return list(filter((lambda x: x.state() == state), self.tasks))
        else:
            raise AttributeError("State '%s' does not exist" % state)

    @classmethod
    def create_from_file(cls, path):
        """This function creates example of class from .yaml file."""
        with open(path, "rt", encoding="utf-8") as input:
            package = load(input, Loader=Loader)
            dataset = package.get("dataset")
            if not isinstance(dataset, list):
                raise ValueError("wrong format")
        rm = Roadmap()
        rm.tasks = [Task(t[0], t[2], t[1]) for t in dataset]
        return rm

    def save(self, path):
        """This function saves example in file."""
        pass
