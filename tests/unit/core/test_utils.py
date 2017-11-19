import pytest
#from core.utils import development

def dev(a, b):
    if b == 0:
        return None
    else:
        return a / b

class TestDev:
    @pytest.yield_fixture()
    def gen_5(self):
        print('start')
        yield 5
        print('end')

    @pytest.fixture(params=[1, 2, 3])
    def gen_1_2_3(self, request):
        return request.param

    @pytest.fixture()
    def gen_0(self):
        return 0

    def test_zero(self, gen_5, gen_1_2_3):
        result = dev(gen_5, gen_1_2_3)
        assert result == gen_5 / gen_1_2_3

    def test_success(self):
        result = dev(5, 2)
        assert result == 2.5
