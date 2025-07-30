from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

def get_job(job_title, location, num_jobs):
    chrome_driver_path = "C:/Users/prakasp2/PycharmProjects/ds_salary_proj/chromedriver-win64/chromedriver.exe"
    service = Service(executable_path=chrome_driver_path)

    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
   # options.add_argument("--headless")  # comment out to debug visually

    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)
    
    
    #url = f"https://www.glassdoor.com/Job/{location_formatted}-{job_title_formatted}-jobs-SRCH_IL.0,0.htm"

    url="https://www.glassdoor.com/Job/united-states-data-scientist-jobs-SRCH_IL.0,13_IN1_KO14,28.htm"
    #url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={job_title.replace(' ', '%20')}&locKeyword={location.replace(' ', '%20')}"
    print(url)
    driver.get(url)

    try:
        # Wait until at least one job listing loads
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-test="jobListing"]')))
    except:
        print("Timeout waiting for job listings")
        driver.quit()
        return pd.DataFrame()

    job_cards = driver.find_elements(By.CSS_SELECTOR, 'li[data-test="jobListing"]')
    print(f"Found {len(job_cards)} job cards")

    jobs = []
    for card in job_cards[:num_jobs]:
        try:
            # Extract fields using the classes and data-test attributes you provided
            title_elem = card.find_element(By.CSS_SELECTOR, 'a[data-test="job-title"]')
            title = title_elem.text.strip()

            company_elem = card.find_element(By.CSS_SELECTOR, 'span.EmployerProfile_compactEmployerName__9MGcV')
            company = company_elem.text.strip()

            location_elem = card.find_element(By.CSS_SELECTOR, 'div[data-test="emp-location"]')
            location_text = location_elem.text.strip()
            
            try:
                company_rating = card.find_element(By.CSS_SELECTOR, 'span.rating-single-star_RatingText__XENmU').text.strip()
            except:
                    company_rating = None

            try:
                salary_elem = card.find_element(By.CSS_SELECTOR, 'div[data-test="detailSalary"]')
                salary = salary_elem.text.strip()
            except:
                salary = None

            jobs.append({
                'title': title,
                'company': company,
                'location': location_text,
                'salary': salary,
                'Company rating': company_rating
            })
        except Exception as e:
            print(f"Error parsing job card: {e}")

    driver.quit()
    return pd.DataFrame(jobs)

# Sample usage