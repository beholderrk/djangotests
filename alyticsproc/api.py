from django.contrib.auth.models import User
from tastypie.authentication import BasicAuthentication
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.validation import FormValidation
from django import forms
from .models import DataItem, DataSet, ExecHistory


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
        allowed_methods = ['get']
        authentication = BasicAuthentication()


class DataSetAuthorization(Authorization):
    def allowed_objs(self, object_list, bundle):
        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.user == bundle.request.user:
                allowed.append(obj)

        return allowed

    def read_list(self, object_list, bundle):
        return object_list.filter(user=bundle.request.user)

    def read_detail(self, object_list, bundle):
        return bundle.request.user == bundle.obj.user

    def create_list(self, object_list, bundle):
        return object_list

    def create_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def update_list(self, object_list, bundle):
        return self.allowed_objs(object_list, bundle)

    def update_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def delete_list(self, object_list, bundle):
        return self.allowed_objs(object_list, bundle)

    def delete_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user


class DataSetResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    items = fields.ToManyField('alyticsproc.api.DataItemResource', 'dataitem_set', full=True)

    class Meta:
        queryset = DataSet.objects.all()
        resource_name = 'dataset'
        authentication = BasicAuthentication()
        authorization = DataSetAuthorization()


class DataItemAuthorization(Authorization):
    def allowed_objs(self, object_list, bundle):
        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.dataset.user == bundle.request.user:
                allowed.append(obj)

        return allowed

    def read_list(self, object_list, bundle):
        return object_list.filter(dataset__user=bundle.request.user)

    def read_detail(self, object_list, bundle):
        return bundle.request.user == bundle.obj.dataset.user

    def create_list(self, object_list, bundle):
        return object_list

    def create_detail(self, object_list, bundle):
        return bundle.obj.dataset.user == bundle.request.user

    def update_list(self, object_list, bundle):
        return self.allowed_objs(object_list, bundle)

    def update_detail(self, object_list, bundle):
        return bundle.obj.dataset.user == bundle.request.user

    def delete_list(self, object_list, bundle):
        return self.allowed_objs(object_list, bundle)

    def delete_detail(self, object_list, bundle):
        return bundle.obj.dataset.user == bundle.request.user


class DataItemResource(ModelResource):

    class Meta:
        queryset = DataItem.objects.all()
        resource_name = 'dataitem'
        authentication = BasicAuthentication()
        authorization = DataItemAuthorization()