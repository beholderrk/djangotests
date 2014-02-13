from django.test import TestCase
from .models import Component, Yandex, Google


class DownCastTestCase(TestCase):
    def setUp(self):
        Yandex.objects.create(name='Frist',     goal_id=111111)
        Yandex.objects.create(name='Second',    goal_id=222222)

        Google.objects.create(name='Frist',     project_id="b70a372d-4d02-4d7b-9480-9d464736a233")

    def test_component_downcast(self):
        items = Component.objects.select_subclasses()
        do_work_results = map(lambda item: item.do_work(), items)
        self.assertEquals(
            ['Awesome 111111', 'Awesome 222222', 'Good work for b70a372d-4d02-4d7b-9480-9d464736a233'],
            do_work_results
        )
