import datetime
import requests

def generate_date_range():
    # Get the current date
    current_date = datetime.datetime.now().date()

    # Get the first day of the current month
    first_day_of_month = current_date.replace(day=1)

    # Format the dates in the required format
    start_date = first_day_of_month.strftime('%d-%m-%Y')
    end_date = current_date.strftime('%d-%m-%Y')

    return start_date, end_date
