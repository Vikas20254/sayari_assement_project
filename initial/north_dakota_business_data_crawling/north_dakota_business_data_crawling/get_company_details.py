import pandas as pd
import json
import requests
import time

def fetch_filing_detail(source_id):
    url = f"https://firststop.sos.nd.gov/api/FilingDetail/business/{source_id}/false"
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "authorization": "undefined",  # Remove or replace with a valid token if required
        "cookie": "ASP.NET_SessionId=ifbrvyidrv5ciyzao4qj4yil",  # Update this if session expires
        "referer": "https://firststop.sos.nd.gov/search/business",
        "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }

    session = requests.Session()  # Reuse a session for performance improvement

    for attempt in range(3):  # Retry up to 3 times
        try:
            response = session.get(url, headers=headers)
            if response.status_code == 200:
                return json.dumps(response.json())  # Successful response
            elif response.status_code == 500:
                print(f"Server error for ID {source_id}: Retrying ({attempt+1}/3)")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"Unexpected error {response.status_code} for ID {source_id}: {response.text}")
                break
        except requests.RequestException as e:
            print(f"Request failed for ID {source_id}: {e}. Retrying ({attempt+1}/3)")
            time.sleep(2 ** attempt)

    print(f"Failed to fetch details for ID {source_id} after 3 attempts.")
    return None

# Load the data
business_data_df = pd.read_csv('business_data.csv')
business_data_df['company_data'] = None  # Initialize with None for clarity

# Fetch and update `company_data` for each `source_id`
for idx, source_id in enumerate(business_data_df['source_id']):
    data = fetch_filing_detail(source_id)
    if data:
        business_data_df.at[idx, 'company_data'] = data  # Update directly by index
        print(f"Successfully updated company data for source_id {source_id}.")
    else:
        print(f"Could not retrieve filing detail for ID {source_id}")

# Save the updated DataFrame
business_data_df.to_csv('company_data.csv', index=False)
