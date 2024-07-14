import django_filters
from job.models import Job

class OrderFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    company = django_filters.CharFilter(field_name='company__name', lookup_expr='icontains')
    location = django_filters.CharFilter(field_name='location', lookup_expr='icontains')
    requirements = django_filters.CharFilter(field_name='requirements', lookup_expr='icontains')

    class Meta:
        model = Job
        fields = ['title', 'company', 'location', 'requirements', 'salary', 'job_type', 'experience_levels', 'job_location_type']
