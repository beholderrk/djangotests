from django.db import models
from core.models import DateTimeModel, get_first_or_None


class DataSet(DateTimeModel):
    name = models.CharField(blank=True, max_length=25)
    user = models.ForeignKey('auth.User')


class DataItem(DateTimeModel):
    a = models.IntegerField()
    b = models.IntegerField()
    dataset = models.ForeignKey(DataSet)


class ExecHistory(DateTimeModel):
    success = models.BooleanField()
    error = models.BooleanField()
    result = models.TextField(blank=True)
    exception = models.TextField('Exception', blank=True)
    dataset = models.OneToOneField(DataSet)


class LastCheck(DateTimeModel):
    success = models.BooleanField()
    count = models.PositiveIntegerField(default=0)

    @classmethod
    def get_instance(cls):
        item = get_first_or_None(cls.objects.all()) or cls.objects.create(success=False)
        return item

    @classmethod
    def set_success(cls, count):
        item = cls.get_instance()
        item.success = True
        item.count = count
        item.save()

    @classmethod
    def set_fail(cls, count):
        item = cls.get_instance()
        item.success = False
        item.count = count
        item.save()