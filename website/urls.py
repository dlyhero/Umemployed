from django.urls import path

from . import views

urlpatterns = [
    # path("",views.home, name="home"),
    path("job-listing", views.job_listing, name="job-listing"),
]
