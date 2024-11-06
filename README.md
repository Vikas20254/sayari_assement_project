```markdown
# North Dakota Business Data Crawling

## Overview

This project is a web scraping tool that extracts business data from the North Dakota FirstStop SOS website, processes the data, and generates a graph to visualize relationships between companies and their primary agents. The scraping script is built using the `scrapy` framework, while the data visualization is done using `NetworkX` and `matplotlib`.

## Features

- **Business Data Extraction**: Scrapes business information such as company name, filing date, status, and more from the North Dakota FirstStop SOS website.
- **Detailed Data Retrieval**: Fetches additional filing details for each business.
- **Data Processing**: Creates a CSV file for the collected data and processes company-agent relationships.
- **Network Graph Visualization**: Uses `NetworkX` to generate a graph to illustrate connections between companies and their agents.

## Prerequisites

- Python 3.x
- Libraries: `scrapy`, `pandas`, `requests`, `networkx`, `matplotlib`

You can install the required libraries using:

```sh
pip install scrapy pandas requests networkx matplotlib
```

## Usage

1. **Run the Spider**: To start the scraping process, run the following command in your terminal:
    
    ```sh
    scrapy runspider business_spider.py
    ```
    
    This will initiate requests to the North Dakota FirstStop SOS website and start extracting business data.

2. **Data Output**: The script will generate two CSV files:
   - `company_data.csv`: Contains basic details of businesses, including company name, filing date, status, etc.
   - `final_company_data.csv`: Contains additional processed information, including details about primary agents.

3. **Graph Generation**: The script will also generate a network graph showing relationships between companies and their primary agents. The graph will automatically be displayed at the end of the scraping and processing.

## Code Structure

- **`start_requests()`**: Initiates the scraping request to the North Dakota FirstStop SOS website with the required headers and payload.
- **`fetch_filing_detail()`**: Fetches additional filing details for each business using the `requests` library.
- **`parse()`**: Parses the initial response and gathers key business details. Stores these details in a DataFrame and fetches further filing details.
- **`process_company_data()`**: Processes the detailed filing information and generates a final DataFrame which is saved to `final_company_data.csv`.
- **`create_graph()`**: Creates a network graph using `NetworkX` to visualize relationships between companies and their primary agents.

## Graph Visualization

The generated graph will display:

- **Nodes**: Companies and their primary agents.
- **Edges**: Relationships between companies and agents.
- **Color Scheme**: Different colors to distinguish between companies and agents, providing a visual representation of their connections.

## Notes

- The script includes a retry mechanism for fetching filing details, with exponential backoff to handle temporary server issues.
- Be mindful of the website's rate limits; excessive requests may result in temporary blocks.
- Some data points may be unavailable, which will be represented as "unknown" in the final dataset.

## Example Output

- **CSV Files**:
  - `company_data.csv`: Initial company data.
  - `final_company_data.csv`: Enhanced company data including agent information.
- **Graph**: A network graph illustrating relationships between businesses and agents.

## License

This project is licensed under the MIT License.

## Disclaimer

This script is for educational purposes only. Ensure that web scraping complies with the site's `robots.txt` file and terms of service.
