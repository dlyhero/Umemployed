from django.shortcuts import render

# Create your views here.
def assessments(request):
    return render(request, 'assessments/assessment.html')

def assessment_detail(request):
    return render(request, 'assessments/assessment_detail.html')