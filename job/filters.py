import django_filters

from .models import *


class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Job
        fields = "__all__"
