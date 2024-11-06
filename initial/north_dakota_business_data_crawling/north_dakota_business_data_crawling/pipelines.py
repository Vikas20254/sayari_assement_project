# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import csv

class SaveToCSVPipeline:
    def open_spider(self, spider):
        self.file = open("data/company_data.csv", "w", newline="")
        self.writer = csv.writer(self.file)
        self.writer.writerow([
            "company_name", "company_id", "filing_type", "status",
            "standing_ar", "standing_ra", "standing_other", "formed_in",
            "term_of_duration", "initial_filing_date", "principal_address",
            "mailing_address", "ar_due_date", "registered_agent",
            "commercial_registered_agent", "owner_name"
        ])

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        self.writer.writerow([
            item.get("company_name"), item.get("company_id"), item.get("filing_type"),
            item.get("status"), item.get("standing_ar"), item.get("standing_ra"),
            item.get("standing_other"), item.get("formed_in"), item.get("term_of_duration"),
            item.get("initial_filing_date"), item.get("principal_address"),
            item.get("mailing_address"), item.get("ar_due_date"),
            item.get("registered_agent"), item.get("commercial_registered_agent"),
            item.get("owner_name")
        ])
        return item
