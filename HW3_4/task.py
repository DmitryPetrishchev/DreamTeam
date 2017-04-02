"""Module provides class "Task"."""
from datetime import date, timedelta


class Task(object):

    def __init__(self, title: str, estimate: date, state: str="in_progress"):
        if isinstance(title, str):
            self.title = title
        else:
            raise TypeError("Argument 'title' must have a 'string' type.")
        if isinstance(estimate, date):
            self.estimate = estimate
        else:
            raise TypeError("Argument 'estimate' must have a 'datetime.date' type.")
        if isinstance(state, str):
            self._state = None
            self.state = state
        else:
            raise TypeError("Argument 'state' must have a 'string' type.")

    def __repr__(self) -> str:
        return self.title + " until " + str(self.estimate) + ". Status: " + self.state

    @property
    def state(self) -> str:
        return self._state

    available_states = frozenset({"in_progress", "ready"})

    @state.setter
    def state(self, value: str):
        if value in self.available_states:
            self._state = value
        else:
            raise AttributeError("State '%s' does not exist" % value)

    def ready(self):
        self.state = "ready"

    @property
    def remaining(self) -> date:
        if self.state == "in_progress" and not self.is_failed:
            return self.estimate - date.today()
        else:
            return timedelta(0)

    @property
    def is_failed(self) -> bool:
        return self.state == "in_progress" and self.estimate < date.today()

    @property
    def is_critical(self) -> bool:
        return (self.is_failed or self.remaining < timedelta(days=3)
                and self.state == "in_progress")
