# coding=utf-8
from django.db import models
from django.db.models.fields.related import SingleRelatedObjectDescriptor
from django.db.models.query import QuerySet


class DownCastQuerySet(QuerySet):
    """
    Queryset который приводит каждую модель к дочернему классу
    """

    def select_subclasses(self, *subclasses):
        # если подмодели не выбраны определяем их по модели, записываем их в поле класса
        # для дальнейшего использования
        self.subclasses = subclasses or [o for o in dir(self.model)
                                         if isinstance(getattr(self.model, o), SingleRelatedObjectDescriptor)
                                         and issubclass(getattr(self.model, o).related.model, self.model)]
        # мы хотим вытянуть из базы сразу все данные вместе с подмоделями
        new_qs = self.select_related(*self.subclasses)
        return new_qs

    def _clone(self, klass=None, setup=False, **kwargs):
        """При клонировании теперь нужно учесть что есть список подмоделей"""
        if getattr(self, 'subclasses', False):
            kwargs.update({'subclasses': self.subclasses})
        return super(DownCastQuerySet, self)._clone(klass, setup, **kwargs)

    def iterator(self):
        # берем итератор от базового класса
        it = super(DownCastQuerySet, self).iterator()
        if getattr(self, 'subclasses', False):

            def try_get_rel(item, attr):
                """Функция пробует взять связанный объект, если не удается перехватывает исключение"""
                try:
                    return getattr(item, attr)
                except models.ObjectDoesNotExist:
                    return None

            for obj in it:
                # пробуем взять все связанные подмодели
                rel = [try_get_rel(obj, s) for s in self.subclasses]
                # если хоть что-то нашлось возвращаем это, иначе возвращаем сам объект
                rel = [x for x in rel if x] or [obj]
                yield rel[0]
        else:
            for obj in it:
                yield obj


class DowncastManager(models.Manager):
    def get_queryset(self):
        return DownCastQuerySet(self.model, using=self.db)

    def select_subclasses(self, *args):
        return self.get_queryset().select_subclasses(*args)


class Component(models.Model):
    name = models.CharField(max_length=100)
    objects = DowncastManager()

    def do_work(self):
        pass


class Google(Component):
    project_id = models.CharField(max_length=36)

    def do_work(self):
        return "Good work for %s" % self.project_id


class Yandex(Component):
    goal_id = models.IntegerField()

    def do_work(self):
        return "Awesome %s" % self.goal_id


