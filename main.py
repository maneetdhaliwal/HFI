import requests
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from datetime import datetime, timedelta

host = 'data.usajobs.gov'
user_agent = 'name@example.com'
auth_key = 'YourAPIKey'

# Fetch countries
url_countries = 'https://data.usajobs.gov/api/codelist/countries'
headers = {
    "User-Agent": user_agent,
    "Authorization-Key": auth_key
}

response_countries = requests.get(url_countries, headers=headers)

state_job_counts = {}
total_jobs = 0  # Initialize sum for all jobs

if response_countries.status_code == 200:
    data = response_countries.json()
    countries = data['CodeList'][0]['ValidValue']  # Access the list of countries

    # Fetch US state subdivisions
    url_states = 'https://data.usajobs.gov/api/codelist/countrysubdivisions'
    response_states = requests.get(url_states, headers=headers, params={'country': 'US'})

    if response_states.status_code == 200:
        states_data = response_states.json()
        # Extract valid state codes
        state_codes = [
            state['Code'].strip() for state in states_data['CodeList'][0]['ValidValue']
            if state['IsDisabled'] == 'No'
        ]
    else:
        print(f'Error fetching states: {response_states.status_code}, {response_states.text}')
        state_codes = []

    # Sum jobs for each state
    for state in state_codes:
        url = 'https://data.usajobs.gov/api/search'
        params = {
            'LocationName': state,
            'ResultsPerPage': 1
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            jobs_count = data['SearchResult']['SearchResultCountAll']
            print(f'Jobs in {state}: {jobs_count}')
            state_job_counts[state] = jobs_count  # Store job counts for each state
            total_jobs += jobs_count
        else:
            print(f'Error for {state}: {response.status_code}, {response.text}')

    print(f'Total jobs across selected states: {total_jobs}')

    # Sum jobs for countries excluding US
    country_job_counts = {}
    for country in countries:
        code = country['Code']
        if code not in ['99', '98', 'US']:  # Exclude codes 99, 98, and US
            params = {
                'Keyword': '',  # Leave empty to get all jobs
                'LocationName': country['Value'],  # Set location to current country
                'ResultsPerPage': 1  # Set to 1 to get total count in response
            }
            
            # Get job count for the current country
            job_response = requests.get('https://data.usajobs.gov/api/search', headers=headers, params=params)
            if job_response.status_code == 200:
                job_data = job_response.json()
                job_count = job_data['SearchResult']['SearchResultCountAll']  # Extract total jobs
                country_job_counts[country['Value']] = job_count  # Store job counts for each country
                total_jobs += job_count  # Add to total jobs
                print(f"Jobs in {country['Value']}: {job_count}")
            else:
                print(f'Error fetching jobs for {country["Value"]}: {job_response.status_code}, {job_response.text}')

    print(f'Total jobs across all regions: {total_jobs}')

    # Graphing
    start_date = datetime.now()
    date_labels = [start_date + timedelta(days=90 * i) for i in range(6)]  # Next 6 tri-monthly intervals
    formatted_dates = [date.strftime('%Y-%m-%d') for date in date_labels]

    # Prepare job counts: only the first bar shows a job count, others are 0
    job_counts = [total_jobs] + [0] * (len(formatted_dates) - 1)

    # Plotting
    plt.figure(figsize=(12, 6))

    plt.bar(formatted_dates, job_counts, color='blue', alpha=0.7)

    plt.xlabel('Date (Every 3 Months)')
    plt.ylabel('Number of Jobs')
    plt.title('Projected Job Counts Every 3 Months')
    plt.xticks(rotation=45)
    plt.ylim(0, max(job_counts) + 1000)  # Adjust Y-axis limit
    plt.tight_layout()
    plt.grid(axis='y')

    plt.show()
