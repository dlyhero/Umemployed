import django_filters
from django_ckeditor_5.fields import CKEditor5Field
from django_filters import CharFilter

from job.models import Job


class JobFilter(django_filters.FilterSet):
    class Meta:
        model = Job
        fields = [
            "title",
            "company",
            "location",
            "job_type",
            "level",
            "salary_range",
            "ideal_candidate",
        ]
        filter_overrides = {
            CKEditor5Field: {"filter_class": CharFilter},
        }
