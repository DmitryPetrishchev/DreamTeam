from datetime import date, timedelta

available_states = { 'in_progress', 'ready' }

class Task(object):
    '''Doc of class Task'''

    def __init__(self, title, estimate, state = 'in_progress'):
        self.title = title
        self.estimate = estimate
        self.state = state

    def __str__(self):
        return self.title + ' до ' + str(self.estimate) + '. Статус: ' + self.state

    @property           #state.getter создается автоматически
    def state(self):
        '''Doc of property state'''
        return self._state

    @state.setter
    def state(self, new_state):
        if new_state in available_states:
            self._state = new_state
        else:
            raise AttributeError('State \"' + new_state + '\" doesn\'t exist')

    def ready(self):
        self.state = 'ready'

    @property
    def remaining(self):
        if self.state == 'in_progress':
            return self.estimate - date.today()
        else:
            return timedelta(0)

    @property
    def is_failed(self):
        return self.state == 'in_progress' and self.estimate < date.today()

