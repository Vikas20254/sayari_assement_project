import scrapy
import json
from north_dakota_business_data_crawling.items import NorthDakotaBusinessDataCrawlingItem
import pandas as pd
from north_dakota_business_data_crawling.get_company_details import fetch_filing_detail

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

    def parse(self, response):
        data = response.json()  # Assuming the response is JSON
        
        data_rows = data['rows']
        business_data_df = pd.DataFrame.from_dict(data_rows, orient='index')
        # Fetch and update `company_data` for each `source_id`
        for idx, source_id in enumerate(business_data_df['id']):
            data = fetch_filing_detail(source_id)
            if data:
                business_data_df.at[idx, 'company_data'] = data  # Update directly by index
                print(f"Successfully updated company data for source_id {source_id}.")
            else:
                print(f"Could not retrieve filing detail for ID {source_id}")
        
        # Save the updated DataFrame
        business_data_df.to_csv('company_data.csv', index=False)
        

