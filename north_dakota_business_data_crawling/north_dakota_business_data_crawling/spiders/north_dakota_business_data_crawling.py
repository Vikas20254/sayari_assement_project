import scrapy
import json
import pandas as pd
import requests
import time

class BusinessSpider(scrapy.Spider):
    name = "north_dakota_business_data_crawling"
    start_urls = ["https://firststop.sos.nd.gov/api/Records/businesssearch"]

    def start_requests(self):
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

        yield scrapy.Request(
            url=self.start_urls[0],
            method="POST",
            headers=headers,
            body=json.dumps(payload),
            callback=self.parse
        )

    def fetch_filing_detail(self, source_id):
        url = f"https://firststop.sos.nd.gov/api/FilingDetail/business/{source_id}/false"
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "authorization": "undefined",  # Replace if necessary
            "cookie": "ASP.NET_SessionId=ifbrvyidrv5ciyzao4qj4yil",  # Update session ID if expired
            "referer": "https://firststop.sos.nd.gov/search/business",
            "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }

        session = requests.Session()

        for attempt in range(3):  # Retry up to 3 times
            try:
                response = session.get(url, headers=headers)
                if response.status_code == 200:
                    return json.dumps(response.json())
                elif response.status_code == 500:
                    print(f"Server error for ID {source_id}: Retrying ({attempt + 1}/3)")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"Unexpected error {response.status_code} for ID {source_id}: {response.text}")
                    break
            except requests.RequestException as e:
                print(f"Request failed for ID {source_id}: {e}. Retrying ({attempt + 1}/3)")
                time.sleep(2 ** attempt)

        print(f"Failed to fetch details for ID {source_id} after 3 attempts.")
        return None

    def parse(self, response):
        if response.status == 200:
            data = response.json()  # Parse the response JSON

            # Step 1: Extract data for 'rows'
            rows = data['rows']

            # Step 2: Prepare a list to store row data in the desired format
            business_data = []

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
                business_data.append(row)

            # Step 4: Create the DataFrame and save to CSV
            business_data_df = pd.DataFrame(business_data)
            business_data_df.to_csv('business_data.csv', index=False)

            # Fetch and update `company_data` for each `source_id`
            for idx, source_id in enumerate(business_data_df['source_id']):
                print(f'Processing index {idx} with source_id {source_id}')
                data = self.fetch_filing_detail(source_id)
                if data:
                    business_data_df.loc[idx, 'company_data'] = data  # Update directly by index
                    print(f"Successfully updated company data for source_id {source_id}.")
                else:
                    print(f"Could not retrieve filing detail for ID {source_id}")

            # Save the updated DataFrame with the new company data
            business_data_df.to_csv('company_data.csv', index=False)
        else:
            print(f"Request failed with status code: {response.status}")

        # Column mapping for final data
        required_columns = {
            "Company Name": "company_name",
            "Company ID": "company_id",
            "Filing Type": "filing_type",
            "Status": "status",
            "Standing - AR": "standing_ar",
            "Standing - RA": "standing_ra",
            "Standing - Other": "standing_other",
            "Formed In": "formed_in",
            "Term of Duration": "term_of_duration",
            "Initial Filing Date": "initial_filing_date",
            "Principal Address": "principal_address",
            "Mailing Address": "mailing_address",
            "AR Due Date": "ar_due_date",
            "Registered Agent": "registered_agent",
            "Commercial Registered Agent": "commercial_registered_agent",
            "Owner Name": "owner_name"
        }

        # Initialize a list to store each row's data
        rows = []

        # Iterate over each entry in company_data_df['company_data']
        for idx, company_data in enumerate(business_data_df['company_data']):
            # Initialize a dictionary with default values for each required column
            row_data = {col_name: "unknown" for col_name in required_columns.values()}
            row_data[required_columns['Company Name']] = business_data_df.at[idx, 'company_name']
            row_data[required_columns['Company ID']] = business_data_df.at[idx, 'company_id']

            try:
                # Parse the JSON data for each company
                parsed_data = json.loads(company_data)
# Get the drawer details list
                drawer_details = parsed_data.get("DRAWER_DETAIL_LIST", [])
      
               # Populate row_data based on drawer details
                for detail in drawer_details:
                    label = detail["LABEL"]
                    value = detail["VALUE"]
                    
                    # Process address fields to remove newline characters
                    if label in required_columns:
                        if "Address" in label or "Registered Agent" in label:
                            value = value.replace("\n", ", ")  # Replace \n with comma and space
                        row_data[required_columns[label]] = value


                        row_data[required_columns[label]] = value                
                
                # Additional mappings can go here...

            except json.JSONDecodeError as e:
                print(f"Error parsing JSON for company {company_data}: {e}")
                continue

            # Add the row data to the rows list
            rows.append(row_data)

        # Convert the final list of rows into a DataFrame and save to CSV
        final_df = pd.DataFrame(rows)
        final_df.to_csv('final_company_data.csv', index=False)
    # Replace "unknown" with NaN, then backfill to get first valid value
        final_df['primary_agent'] = final_df[['owner_name', 'Registered Agent', 'commercial_registered_agent']].replace("unknown", pd.NA).bfill(axis=1).iloc[:, 0]


     # Replace NaN in primary_agent with "No Agent Info"
        final_df['primary_agent'].fillna("No Agent Info", inplace=True)

        final_df.to_csv('company_data_processed.csv')
