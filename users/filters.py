import django_filters
from job.models import *

class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Job
        fields = ['title','company','location','requirements']