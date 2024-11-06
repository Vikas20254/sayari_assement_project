import numpy as np
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

driver = selenium.webdriver.Chrome()
driver.get('https://firststop.sos.nd.gov/search/business')

WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "advanced-search-toggle"))).click()
driver.implicitly_wait(10)
WebDriverWait(driver, 1000).until(EC.presence_of_element_located((By.CSS_SELECTOR,
      '.radio-group .option-wrapper input[type="radio"]:not(:checked) + label'))).click()
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'label-ACTIVE_ONLY_YN'))).click()
driver.find_element(By.CSS_SELECTOR, 'input[type="text"].search-input').send_keys('X')
driver.find_element(By.CSS_SELECTOR, '.btn.btn-primary.btn-raised.advanced-search-button').click()
rows = driver.find_elements(By.CSS_SELECTOR, ".div-table-body tr")
data_dict = {'name': [], 'registered_agent': [], 'commercial_registered_agent': [], 'owner_name': []}

for j, row in enumerate(rows):
    cell = row.find_elements(By.TAG_NAME, "td")[0]
    btn = cell.find_element(By.CSS_SELECTOR, '.interactive-cell-button')
    driver.execute_script("arguments[0].click();", btn)
    time.sleep(3)
    company_name = driver.find_element(By.CSS_SELECTOR, '.drawer-inner-wrapper .title-box h4').text.strip()

    if not company_name.startswith('X'):
        continue
    data_dict['name'].append(company_name)
    data = driver.find_elements(By.CSS_SELECTOR, '.scrollable-drawer-wrapper .details-list tbody tr')

    stored_keys = []
    for d in data:
        key = d.find_element(By.CSS_SELECTOR, '.label').text.replace(' ', '_').strip().lower()
        value = d.find_element(By.CSS_SELECTOR, '.value').text.strip()
        if key in data_dict.keys():
            data_dict[key].append(value.split('\n')[0].strip())
            stored_keys.append(key)

    stored_keys.append('name')
    for missed in list(set(data_dict.keys()) - set(stored_keys)):
        data_dict[missed].append(np.nan)

df = pd.DataFrame.from_dict(data_dict)
df.to_csv('company_data.csv', index=False)
driver.quit()
