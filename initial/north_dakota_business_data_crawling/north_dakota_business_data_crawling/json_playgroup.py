import requests
import json
import pandas as pd

headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://firststop.sos.nd.gov",
    "referer": "https://firststop.sos.nd.gov/search/business",
    "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "cookie": "ASP.NET_SessionId=b5eudwvpmasaqyejvokanbro"
}

payload = {
    "SEARCH_VALUE": "X",
    "STARTS_WITH_YN": True,
    "ACTIVE_ONLY_YN": True
}

url = "https://firststop.sos.nd.gov/api/Records/businesssearch"  # Define the URL

# Send the POST request using requests
response = requests.post(url, headers=headers, data=json.dumps(payload))

if response.status_code == 200:
    data = response.json()  # Parse the response JSON
    
    # Step 1: Extract data for 'rows'
    rows = data['rows']
    
    # Step 2: Prepare a list to store row data in the desired format
    data_for_df = []

    # Step 3: Iterate over each row in 'rows' and extract the relevant columns
    for company_id, company_data in rows.items():
        company_name = company_data['TITLE'][0]  # Get the first item in 'TITLE' as the company name
        row = {
            'source_id': company_data['ID'],
            'company_name': company_name,
            'company_id': company_data['ID'],
            'FILING_DATE': company_data['FILING_DATE'],
            'RECORD_NUM': company_data['RECORD_NUM'],
            'STATUS': company_data['STATUS'],
            'STANDING': company_data['STANDING'],
            'ALERT': company_data['ALERT'],
            'CAN_REINSTATE': company_data['CAN_REINSTATE'],
            'CAN_FILE_AR': company_data['CAN_FILE_AR'],
            'CAN_ALWAYS_FILE_AR': company_data['CAN_ALWAYS_FILE_AR'],
            'CAN_FILE_REINSTATEMENT': company_data['CAN_FILE_REINSTATEMENT']
        }
        data_for_df.append(row)

    # Step 4: Create the DataFrame
    df = pd.DataFrame(data_for_df)
    df.to_csv('business_data.csv')

    # Display the DataFrame
    print(df)
else:
    print(f"Request failed with status code: {response.status_code}")
