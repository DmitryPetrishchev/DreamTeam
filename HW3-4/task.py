"""This module realise class "Task"."""
from datetime import date
from datetime import timedelta


class Task(object):
    """This is class "Task"."""

    def __init__(self, title, estimate, state="in_progress"):
        """This is constructor of class."""
        self.title = title
        self.estimate = estimate
        self.state = state

    def __str__(self):
        """This function sets string format of class."""
        return self.title + " until " + str(self.estimate) + ". Status: " + self.state

    @property           # state.getter создается автоматически
    def state(self):
        """This function returns state of task."""
        return self._state

    __availableStates = {"in_progress", "ready"}

    @state.setter
    def state(self, newState):
        """This function checks available states of task."""
        if newState in self.__availableStates:
            self._state = newState
        else:
            raise AttributeError("State '%s' does not exist" % newState)

    def ready(self):
        """This function changes state of task to "ready"."""
        self.state = "ready"

    @property
    def remaining(self):
        """This function calculates remaining time of task."""
        if self.state == "in_progress":
            return self.estimate - date.today()
        else:
            return timedelta(0)

    @property
    def is_failed(self):
        """This function checks failed tasks."""
        return self.state == "in_progress" and self.estimate < date.today()

    @property
    def is_critical(self):
        """This function checks critical tasks."""
        return self.is_failed() and self.remaining < timedelta(days=3)
