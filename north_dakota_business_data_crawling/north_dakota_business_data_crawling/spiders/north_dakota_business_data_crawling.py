import scrapy, json, pandas as pd, requests, time, networkx as nx, matplotlib.pyplot as plt
from networkx.algorithms.community import girvan_newman

class BusinessSpider(scrapy.Spider):
    name = "north_dakota_business_data_crawling"
    start_urls = ["https://firststop.sos.nd.gov/api/Records/businesssearch"]

    def start_requests(self):
        headers = {
                "Content-Type": "application/json",
                "Origin": "https://firststop.sos.nd.gov",
                "Referer": "https://firststop.sos.nd.gov/search/business",
                "Sec-CH-UA-Platform": '"macOS"',
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Cookie": "ASP.NET_SessionId=b5eudwvpmasaqyejvokanbro"
                 }

        payload = {"SEARCH_VALUE": "X", "STARTS_WITH_YN": True, "ACTIVE_ONLY_YN": True}
        yield scrapy.Request(url=self.start_urls[0], method="POST", headers=headers, body=json.dumps(payload), callback=self.parse)

    def fetch_filing_detail(self, source_id):
        url = f"https://firststop.sos.nd.gov/api/FilingDetail/business/{source_id}/false"
        headers = {"authorization": "undefined"}
        for attempt in range(3):
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json()
                time.sleep(2 ** attempt)
            except requests.RequestException:
                time.sleep(2 ** attempt)
        return None

    def parse(self, response):
        if response.status == 200:
            rows = response.json().get('rows', {})
            business_data = [{
                'source_id': data['ID'],
                'company_name': data['TITLE'][0],
                'FILING_DATE': data['FILING_DATE'],
                'RECORD_NUM': data['RECORD_NUM'],
                'STATUS': data['STATUS'],
                'STANDING': data['STANDING']
            } for data in rows.values()]
            business_data_df = pd.DataFrame(business_data)
             #Filter out rows where the company name does not start with 'X'
            business_data_df = business_data_df[business_data_df['company_name'].str.startswith("X")]
            business_data_df.to_csv('test.csv')
            business_data_df['company_data'] = business_data_df['source_id'].apply(self.fetch_filing_detail)
            business_data_df.to_csv('company_data.csv', index=False)
            self.process_company_data(business_data_df)
        else:
            print(f"Request failed with status code: {response.status}")

    def process_company_data(self, df):
        required_columns = {
            "Company Name": "company_name",
            "Company ID": "source_id",
            "Owner Name": "owner_name",
            "Registered Agent": "registered_agent",
            "Commercial Registered Agent": "commercial_registered_agent"
        }
        rows = []
        for idx, company_data in df['company_data'].items():
            row_data = {col: "unknown" for col in required_columns.values()}
            row_data[required_columns['Company Name']] = df.at[idx, 'company_name']
            row_data[required_columns['Company ID']] = df.at[idx, 'source_id']
            if company_data:
                drawer_details = company_data.get("DRAWER_DETAIL_LIST", [])
                for detail in drawer_details:
                    if detail["LABEL"] in required_columns:
                        row_data[required_columns[detail["LABEL"]]] = detail["VALUE"].replace("\n", ", ")
            rows.append(row_data)
        final_df = pd.DataFrame(rows)
        final_df['primary_agent'] = final_df[['owner_name', 'registered_agent', 'commercial_registered_agent']].replace("unknown", pd.NA).bfill(axis=1).iloc[:, 0]
        final_df['primary_agent'].fillna("No Agent Info", inplace=True)
        final_df.to_csv('final_company_data.csv', index=False)
        self.create_graph(final_df)

    def create_graph(self, df):
        G = nx.Graph()
        for _, row in df.iterrows():
            G.add_node(row['company_name'], type='company')
            G.add_node(row['primary_agent'], type='agent')
            G.add_edge(row['company_name'], row['primary_agent'])
        communities = next(girvan_newman(G))
        color_map = ["lightblue" if node in communities[0] else "orange" for node in G]
        size_map = [200 + G.degree[node] * 100 for node in G]
        pos = nx.spring_layout(G, k=0.8, iterations=100)
        plt.figure(figsize=(18, 18))
        nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=size_map, font_size=8, font_weight="bold", edge_color="gray", font_color="black")
        plt.title("Enhanced Company-Primary Agent Network Graph with Increased Spacing")
        plt.show()


