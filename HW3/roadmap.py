from copy import deepcopy
from datetime import date
from task import Task, available_states

class Roadmap(object):
    '''Doc of class Roadmap'''

    def __init__(self, tasks = []):
        self.tasks = deepcopy(tasks)

    @property
    def today(self):
        return [t for t in self.tasks if t.estimate == date.today()]

    def filter(self, state):
        if state in available_states:
            return [t for t in self.tasks if t.state == state]
        else:
            raise AttributeError('State \"' + new_state + '\" doesn\'t exist')

    @classmethod
    def CreateFromFile(cls, path):
        '''Парсит файл типа yaml и возвращает экземпляр Roadmap'''
        pass

    def save(self, path):
        '''Сохраняет экземпляр Roadmap в yaml файл'''
        pass