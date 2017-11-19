import pytest
from core.models import Todo


"""
    class TestIndex:
    @pytest.fixture()
    def todo1(self, models):
        return models.create_todo('todo1')

    def test_index(self, todo1, http):
        response = http.get('/')
        assert Todo.objects.count() == 1
        assert response.status_code == 200
"""

class TestIndex:
    @pytest.fixture()
    def todo1(self, db):
        return Todo.objects.create(title='todo1')

    def test_index(self, http, todo1):
        response = http.get('/')
        assert response.status_code == 200
        assert 'todo' is response.content.decode('utf-8')

class TestCreate:
    def tets_success_create(self, db, http):
        response = http.post('/create')
        assert response.status_code == 302
        assert Todo.objects.filter(title='todo1').exists()

    def tets_error_unique(self, http, todo1):
        response = http.post('/create', data={'title': 'todo1'})
        assert response.status_code == 302
        assert Todo.objects.filter(title='todo1').exists()
