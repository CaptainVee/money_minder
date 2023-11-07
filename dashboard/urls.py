from django.urls import path
from .views import (
    home,
    collect,
    connect,
    dashboard,
    tester,
    get_live_data,
    budget,
    update_transaction,
    accounts,
    transactions,
    investment,
)

# app_name = "courses"

urlpatterns = [
    path("", home, name="home"),
    path("test", tester, name="test"),
    path("collect/<uuid:user_id>/", collect, name="collect"),
    path("connect/<uuid:user_id>/", connect, name="connect"),
    path("dashboard/", dashboard, name="dashboard"),
    path("get_live_data/", get_live_data, name="get_live_data"),
    path("budget/", budget, name="budget"),
    path("accounts/", accounts, name="accounts"),
    path("transactions/", transactions, name="transactions"),
    path("investment/", investment, name="investment"),

    path('update_transaction/<int:transaction_id>/', update_transaction, name='update_transaction'),
]

