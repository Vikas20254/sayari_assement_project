# North Dakota Business Data Crawling

## Overview
This project is a web scraping tool that extracts business data from the North Dakota FirstStop SOS website, processes the data, and generates a graph to visualize relationships between companies and their primary agents. The scraping script is built using the `scrapy` framework, while the data visualization is done using `NetworkX` and `matplotlib`.

## Features
1. **Business Data Extraction**: Scrapes business information such as company name, filing date, status, and more from the North Dakota FirstStop SOS website.
2. **Detailed Data Retrieval**: Fetches additional filing details for each business.
3. **Data Processing**: Creates a CSV file for the collected data and processes company-agent relationships.
4. **Network Graph Visualization**: Uses `NetworkX` to generate a graph to illustrate connections between companies and their agents.

## Prerequisites
- Python 3.x
- Libraries: `scrapy`, `pandas`, `requests`, `networkx`, `matplotlib`

You can install the required libraries using:
```sh
pip install scrapy pandas requests networkx matplotlib
