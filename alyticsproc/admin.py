from django.contrib import admin
from .models import TestData, LastCheck


class TestDataAdmin(admin.ModelAdmin):
    list_display = ('json_data', 'performed', 'result', 'error', 'exception', 'date_modified')
    list_filter = ('performed', 'error')
    date_hierarchy = 'date_modified'


class LastCheckAdmin(admin.ModelAdmin):
    list_display = ('success', 'count', 'date_modified')


admin.site.register(TestData, TestDataAdmin)
admin.site.register(LastCheck, LastCheckAdmin)
