"""Module realise class "Task"."""
from datetime import date, timedelta


class Task(object):
    """Class "Task"."""

    def __init__(self, title: str, estimate: date, state: str="in_progress"):
        """Constructor of class."""
        if isinstance(title, str):
            self.title = title
        else:
            raise ValueError("Argument 'title' must have a 'string' type.")
        if isinstance(estimate, date):
            self.estimate = estimate
        else:
            raise ValueError("Argument 'estimate' must have a 'datetime.date' type.")
        if isinstance(state, str):
            self._state = None
            self.state = state
        else:
            raise ValueError("Argument 'state' must have a 'string' type.")

    def __repr__(self) -> str:
        """Set string format of class."""
        return self.title + " until " + str(self.estimate) + ". Status: " + self.state

    @property           # state.getter создается автоматически
    def state(self) -> str:
        """Return state of task."""
        return self._state

    available_states = frozenset({"in_progress", "ready"})

    @state.setter
    def state(self, value: str):
        """This function checks available states of task."""
        if value in self.available_states:
            self._state = value
        else:
            raise AttributeError("State '%s' does not exist" % value)

    def ready(self):
        """Change state of task to "ready"."""
        self.state = "ready"

    @property
    def remaining(self) -> date:
        """Calculate remaining time of task."""
        if self.state == "in_progress" and not self.is_failed:
            return self.estimate - date.today()
        else:
            return timedelta(0)

    @property
    def is_failed(self) -> bool:
        """Check failed status of task."""
        return self.state == "in_progress" and self.estimate < date.today()

    @property
    def is_critical(self) -> bool:
        """Check critical status of task."""
        return (self.is_failed or self.remaining < timedelta(days=3)
                and self.state == "in_progress")
