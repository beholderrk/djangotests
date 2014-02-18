from django.contrib import admin
from .models import LastCheck, DataSet, DataItem


class LastCheckAdmin(admin.ModelAdmin):
    list_display = ('success', 'count', 'date_modified')


class DataItemInline(admin.TabularInline):
    model = DataItem
    extra = 0


class DataSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'date_modified')
    inlines = [DataItemInline]


admin.site.register(LastCheck, LastCheckAdmin)
admin.site.register(DataSet, DataSetAdmin)