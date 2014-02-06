from django.db import models
from core.models import DateTimeModel, get_first_or_None


class TestData(DateTimeModel):
    json_data = models.TextField('JSON data', blank=True)
    performed = models.BooleanField(default=False)
    result = models.TextField('JSON result', blank=True)
    error = models.BooleanField(default=False)
    exception = models.TextField('Exception', blank=True)


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