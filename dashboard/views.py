from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
# from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
# from .models import Organization
# from .forms import ContributorForm
from django.db.models import Q
import requests
from django.conf import settings
import json
from user.models import Profile
# import pandas as pd
from django.contrib import messages
# Create your views here.





from django.contrib.auth import get_user_model


User = get_user_model()




def home(request):
    if request.user.is_authenticated:
        return render(request, "dashboard/dashboard.html", {})
    else:
        return render(request, "landing_page.html", {})


def connect(request, user_id):
    user = get_object_or_404(User, id=user_id)
    context = {
        'user_id': user.id,
    }
    return render(request, 'dashboard/connect.html', context)

@login_required
def collect(request, user_id):
    code = list(request.GET.keys())
    code = str(code[0])
    url = "https://api.withmono.com/account/auth"
    payload = {"code": code }
    headers = {
    "Accept": "application/json",
    "mono-sec-key": settings.MONO_SEC_KEY,
    "Content-Type": "application/json"
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    auth_id = response.text

    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)
    profile.auth_id = auth_id
    profile.save()
    # context = { "id" : response.text }
    return redirect('dashboard', request.user.id)


def account_identity(request, pk, auth_id):
	url = f"https://api.withmono.com/accounts/{auth_id}/identity"
	headers = {
	"Accept": "application/json",
	"mono-sec-key": settings.MONO_SEC_KEY,
	}
	response = requests.request("GET", url, headers=headers)
	return response.text


def dashboard(request, user_id):
	# if profile.auth_id == None:
	# 	messages.success(request, 'Please Connect an Account to the Organisation')
	# 	return redirect('profile-details', pk)
    profile = get_object_or_404(Profile, user=request.user)
    auth_id = json.loads(profile.auth_id)
    auth_id = auth_id.get('id')
    
    url = f"https://api.withmono.com/accounts/{auth_id}/"
    statement_url = f"https://api.withmono.com/accounts/{auth_id}/statement?period=last6months"
    account_info_url = f"https://api.withmono.com/accounts/{auth_id}"

    headers = {
    "Accept": "application/json",
    "mono-sec-key": settings.MONO_SEC_KEY,
    }


    response = requests.request("GET", url, headers=headers)
	# statement_response = requests.request("GET", statement_url, headers=headers)
    # account_info = requests.request("GET", account_info_url, headers=headers)

    res = json.loads(response.text)
    # account_info_res = json.loads(account_info.text).get('account')

	# statement_res = json.loads(statement_response.text).get('data')
	# monthly_total = total_amount_spent(statement_res)
	# debit_credit_res = debit_credit(statement_res)


    context = { "account" : res,
                # "statement" : statement_res,
                # "monthly_total":monthly_total,
                # "account_info" : account_info_res,
                # "last_transaction" : statement_res[0],
                # "debit_credit" :debit_credit_res,
                }


    return render(request, 'dashboard/dashboard.html', context)
