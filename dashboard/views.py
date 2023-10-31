from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
# from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
# from .models import Organization
# from .forms import ContributorForm
from django.db.models import Sum
import requests
from django.conf import settings
import json
from user.models import Profile, BankAccount
# import pandas as pd
from django.contrib import messages
# Create your views here.
from .utils import generate_date_range
from .models import Transaction, Budget, RecurringBills
from datetime import datetime
from django.http import HttpResponse



from .forms import BudgetForm


from django.contrib.auth import get_user_model


User = get_user_model()



def home(request):
    if request.user.is_authenticated:
        return render(request, "dashboard/dashboard.html", {})
    else:
        return render(request, "landing_page.html", {})

@login_required
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
    new_bank, created = BankAccount.objects.get_or_create(user=user, auth_id=auth_id)

    if not created:
        return redirect('accounts')

    # auth_id = new_bank.auth_id
    auth_id = json.loads(auth_id)['id']
    bank_account_url = f"https://api.withmono.com/accounts/{auth_id}"
    response = requests.request("GET", bank_account_url, headers=headers)
    data = json.loads(response.text)

    print(data, auth_id)
    # Extract relevant information from the object
    account_data = data['account']
    institution_data = data['account']['institution']

    # Create a BankAccount object and populate its fields

    new_bank.account_name=account_data['name'],
    new_bank.account_number=account_data['accountNumber'],
    new_bank.bank=institution_data['name'],
    new_bank.bvn=account_data['bvn'],
    new_bank.account_balance = int(account_data['balance'])
    new_bank.currency=account_data['currency']
    

    # Save the BankAccount object to the database
    new_bank.save()

    return redirect('accounts')


@login_required
def get_live_data(request):

    bank_accounts = BankAccount.objects.filter(user=request.user)
    start_date, end_date = generate_date_range()
    headers = {
    "Accept": "application/json",
    "mono-sec-key": settings.MONO_SEC_KEY,
    }


    for bank_account in bank_accounts:
        auth_id = bank_account.auth_id
        auth_id = json.loads(auth_id)['id']


        # statement_url = f"https://api.withmono.com/accounts/{auth_id}/statement?period=last1months"
        transactions_url =  f'https://api.withmono.com/v1/accounts/{auth_id}/transactions?start={start_date}&end={end_date}'
        
        transaction_response = requests.request("GET", transactions_url, headers=headers)
        transaction_res = json.loads(transaction_response.text).get('data')

        # Iterate through each transaction in the list and store it in the database
        for transaction_data in transaction_res:
            # Extract relevant information from the transaction data
            transaction_id = transaction_data['_id']
            _type = transaction_data['type']
            date = datetime.strptime(transaction_data['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
            amount = transaction_data['amount'] / 100  # Assuming the amount is in the smallest unit of the currency
            description = transaction_data['narration']


            # Use get_or_create to check if the transaction_id exists
            transaction, created = Transaction.objects.get_or_create(
                transaction_id=transaction_id,
                user=request.user,
                defaults={
                    'bank_account': bank_account,
                    'date': date,
                    'amount': amount,
                    'description': description,
                    'type':_type
                }
            )

    return redirect('dashboard')
@login_required
def dashboard(request):
    accounts = BankAccount.objects.filter(user=request.user)
    networth = sum(account.account_balance for account in accounts)
    all_debit_transactions = Transaction.objects.filter(bank_account__in=accounts, budget=None, type='debit')
    all_credit_transactions = Transaction.objects.filter(bank_account__in=accounts, type='credit')

    
    budgets = Budget.objects.filter(user=request.user, is_active=True)

    total_budgeted_amount = 0
    total_spent_from_budget = 0
    for budget in budgets:
        total_transactions_amount = budget.calculate_total_transactons()
        if total_transactions_amount is None:
            total_transactions_amount = 0
        total_spent_from_budget += total_transactions_amount
        total_budgeted_amount += budget.amount

        # total_transactions_amount = budget.transaction_set.aggregate(total_amount=Sum('amount'))['total_amount']
        # if total_transactions_amount is None:
        #     total_transactions_amount = 0
        # total_budget_transaction_amount += total_transactions_amount
        # amount_left = budget.amount - total_transactions_amount
        # total_budget_amount_left += amount_left

    difference = float(total_budgeted_amount - total_spent_from_budget)

    top_5_budgets = (
        Budget.objects.filter(user=request.user)
        .annotate(total_transaction_amount=Sum('transaction__amount'))
        .order_by('-total_transaction_amount')[:5]
    )

    labels = [transaction.date.strftime("%d %b") for transaction in all_credit_transactions]
    data = [float(transaction.amount) for transaction in all_credit_transactions]

    recurring_bills = RecurringBills.objects.filter(user=request.user)

    # print(all_credit_transactions)
    context = {
        "networth": networth,
        "all_debit_transactions": all_debit_transactions,
        "all_credit_transactions": all_credit_transactions,
        "budgets": budgets,
        "total_budget": total_budgeted_amount,
        "total_spent_from_budget": total_spent_from_budget,
        "top_5_budgets": top_5_budgets,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        "difference": json.dumps(difference),
        "recurring_bills": recurring_bills,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def budget(request):
    budgets = Budget.objects.filter(user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            return redirect('budget')
    else:
        form = BudgetForm()
    return render(request, 'dashboard/budget.html', {'budgets': budgets, 'form': form})

@login_required
def update_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id)
    budget_id = request.POST.get('budget')
    budget = get_object_or_404(Budget, pk=budget_id)
    transaction.budget = budget
    transaction.save()
    return HttpResponse(f"{transaction.budget.title}")

@login_required
def accounts(request):
    accounts = BankAccount.objects.filter(user=request.user)
    return render(request, 'dashboard/account.html', {'accounts': accounts})

@login_required
def transactions(request):
    accounts = BankAccount.objects.filter(user=request.user)
    all_debit_transactions = Transaction.objects.filter(bank_account__in=accounts, budget=None, type='debit')
    all_credit_transactions = Transaction.objects.filter(bank_account__in=accounts, type='credit')
    return render(request, 'dashboard/transactions.html', {'all_debit_transactions': all_debit_transactions})

@login_required
def tester(request):
    return render(request, "dashboard/cow.html", {})



# total budget =  28583.13000000000

# networth = ₦ 100000