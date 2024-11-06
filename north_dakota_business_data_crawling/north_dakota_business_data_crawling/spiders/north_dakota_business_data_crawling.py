import scrapy, json, pandas as pd, requests, time, networkx as nx, matplotlib.pyplot as plt
from networkx.algorithms.community import girvan_newman

class BusinessSpider(scrapy.Spider):
    name = "north_dakota_business_data_crawling"
    start_urls = ["https://firststop.sos.nd.gov/api/Records/businesssearch"]

    def start_requests(self):
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0"
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
            "user-agent": "Mozilla/5.0"
        }
        # Retry the request up to 3 times
        for attempt in range(3):
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    return response.json()
                time.sleep(2 ** attempt)  # Exponential backoff
            except requests.RequestException:
                time.sleep(2 ** attempt)
        return None

    def parse(self, response):
        if response.status == 200:
            rows = response.json().get('rows', {})
            business_data = [
                {
                    'source_id': data['ID'],
                    'company_name': data['TITLE'][0],
                    'FILING_DATE': data['FILING_DATE'],
                    'RECORD_NUM': data['RECORD_NUM'],
                    'STATUS': data['STATUS'],
                    'STANDING': data['STANDING']
                } 
                for data in rows.values()
            ]
            # Create DataFrame with the fetched business data
            business_data_df = pd.DataFrame(business_data)
            # Apply function to fetch filing details for each source_id
            business_data_df['company_data'] = business_data_df['source_id'].apply(self.fetch_filing_detail)
            # Save to CSV
            business_data_df.to_csv('company_data.csv', index=False)
            # Process company data
            self.process_company_data(business_data_df)
        else:
            print(f"Request failed with status code: {response.status}")

    def process_company_data(self, df):
        # Define required columns for extracting company data
        required_columns = {
            "Company Name": "company_name",
            "Company ID": "source_id",
            "Owner Name": "owner_name",
            "registered_agent": "registered_agent",
            "Commercial Registered Agent": "commercial_registered_agent"
        }

        rows = []
        # Iterate through each company's filing details
        for idx, company_data in df['company_data'].iteritems():
            row_data = {col: "unknown" for col in required_columns.values()}
            row_data[required_columns['Company Name']] = df.at[idx, 'company_name']
            row_data[required_columns['Company ID']] = df.at[idx, 'source_id']
            
            if company_data:
                # Extract drawer details from the filing data
                drawer_details = company_data.get("DRAWER_DETAIL_LIST", [])
                for detail in drawer_details:
                    if detail["LABEL"] in required_columns:
                        # Clean up the label and assign to appropriate field
                        row_data[required_columns[detail["LABEL"]]] = detail["VALUE"].replace("\n", ", ")

            rows.append(row_data)

        # Create a DataFrame from extracted rows
        final_df = pd.DataFrame(rows)
        # Fill primary agent information
        final_df['primary_agent'] = final_df[['owner_name', 'registered_agent', 'commercial_registered_agent']] \
            .replace("unknown", pd.NA) \
            .bfill(axis=1) \
            .iloc[:, 0]
        # Fill missing agent info with 'No Agent Info'
        final_df['primary_agent'].fillna("No Agent Info", inplace=True)
        # Save the final DataFrame to CSV
        final_df.to_csv('final_company_data.csv', index=False)
        # Create and display the graph
        self.create_graph(final_df)

    def create_graph(self, df):
        # Create a network graph using NetworkX
        G = nx.Graph()

        # Add nodes and edges based on the companies and their primary agents
        for _, row in df.iterrows():
            G.add_node(row['company_name'], type='company')
            G.add_node(row['primary_agent'], type='agent')
            G.add_edge(row['company_name'], row['primary_agent'])

        # Use Girvan-Newman algorithm for community detection
        communities = next(girvan_newman(G))

        # Assign colors to nodes based on community detection
        color_map = ["lightblue" if node in communities[0] else "orange" for node in G]
        size_map = [200 + G.degree[node] * 100 for node in G]  # Adjust node size based on degree

        # Position nodes using spring layout
        pos = nx.spring_layout(G, k=0.8, iterations=100)

        # Plot the graph
        plt.figure(figsize=(18, 18))
        nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=size_map, font_size=8,
                font_weight="bold", edge_color="gray", font_color="black")
        plt.title("Enhanced Company-Primary Agent Network Graph with Increased Spacing")
        plt.show()
