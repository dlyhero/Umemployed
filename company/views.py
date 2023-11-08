from django.shortcuts import render,redirect

from django.contrib import messages
from .models import Company
from users.models import User
from .forms import UpdateCompanyForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404



#update company

@login_required
def update_company(request):
    if request.user.is_recruiter:
        company = get_object_or_404(Company, user=request.user)

        if request.method == 'POST':
            form = UpdateCompanyForm(request.POST, instance=company)
            if form.is_valid():
                var = form.save(commit=False)
                user = request.user
                user.has_company = True
                var.save()
                user.save()
                messages.info(request, 'Your company info has been Updated.')
                return redirect('dashboard')
            else:
                messages.warning(request, 'Something went wrong.')
        else:
            form = UpdateCompanyForm(instance=company)
        
        context = {'form': form}
        return render(request, 'company/update_company.html', context)
    else:
        messages.warning(request,"Permission Denied")

def company_details(request, pk):
    company = get_object_or_404(Company, pk=pk)
    context = {'company': company}
    return render(request, 'company/company_details.html', context)