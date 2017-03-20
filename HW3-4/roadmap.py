from copy import deepcopy
from datetime import date
from yaml import load, Loader

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
    def create_from_file(cls, path):
        '''Парсит файл типа yaml и возвращает экземпляр Roadmap'''

        with open(path, 'rt', encoding='utf-8') as input:
            package = load(input, Loader=Loader)
            dataset = package.get('dataset')
            if not isinstance(dataset, list):
                raise ValueError('wrong format')
           
        rm = Roadmap() 
        rm.tasks = [Task(t[0], t[2], t[1]) for t in dataset]
        return rm

    def save(self, path):
        '''Сохраняет экземпляр Roadmap в yaml файл'''
        pass