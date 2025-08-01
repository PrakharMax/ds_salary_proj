import time
import random
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_glassdoor_jobs(num_jobs=100):
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    # options.add_argument("--headless")  # Uncomment for headless
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/114.0.0.0 Safari/537.36")

    driver = uc.Chrome(options=options)
    wait = WebDriverWait(driver, 25)

    url = "https://www.glassdoor.com/Job/united-states-data-scientist-jobs-SRCH_IL.0,13_IN1_KO14,28.htm"
    print(f"Opening URL: {url}")
    driver.get(url)
    time.sleep(random.uniform(5, 8))

    jobs = []
    seen_ids = set()  # Will store (title, company, location) tuples now
    popup_closed = False
    max_clicks =50
    clicks = 0

    while len(jobs) < num_jobs and clicks < max_clicks:
        print(f"\nScroll attempt #{clicks + 1}")

        # Scroll slowly to bottom to trigger lazy loading
        for y in range(0, 3000, 300):
            driver.execute_script(f"window.scrollTo(0, {y});")
            time.sleep(random.uniform(0.3, 0.6))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(3, 5))

        job_cards = driver.find_elements(By.CSS_SELECTOR, 'li[data-test="jobListing"]')
        print(f"Found {len(job_cards)} job cards so far")

        for card in job_cards:
            try:
                title = card.find_element(By.CSS_SELECTOR, 'a[data-test="job-title"]').text.strip()
                company = card.find_element(By.CSS_SELECTOR, 'span.EmployerProfile_compactEmployerName__9MGcV').text.strip()
                location = card.find_element(By.CSS_SELECTOR, 'div[data-test="emp-location"]').text.strip()
                unique_key = (title, company, location)

                if unique_key in seen_ids:
                    continue
                seen_ids.add(unique_key)

                try:
                    salary = card.find_element(By.CSS_SELECTOR, 'div[data-test="detailSalary"]').text.strip()
                except:
                    salary = None
                try:
                    rating = card.find_element(By.CSS_SELECTOR, 'span.rating-single-star_RatingText__XENmU').text.strip()
                except:
                    rating = None

                jobs.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'salary': salary,
                    'rating': rating
                })

                if len(jobs) >= num_jobs:
                    break
            except Exception as e:
                print(f"Error parsing job card: {e}\nCard text snippet: {card.text[:150]}")

        if len(jobs) >= num_jobs:
            print("Reached target number of jobs")
            break

        # Click "Show more jobs" button if possible
        try:
            show_more = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-test="load-more"]')))
            driver.execute_script("arguments[0].scrollIntoView();", show_more)
            time.sleep(random.uniform(1, 2))
            show_more.click()
            print("Clicked 'Show more jobs' button")
            clicks += 1

            if not popup_closed:
                time.sleep(3)
                try:
                    close_btn = driver.find_element(By.CSS_SELECTOR, 'button.CloseButton, button[data-test="job-alert-modal-close"]')
                    close_btn.click()
                    print("Closed popup")
                    popup_closed = True
                except:
                    print("No popup found to close")

            time.sleep(random.uniform(4, 6))
        except Exception as e:
            print(f"No 'Show more jobs' button or could not click: {e}")
            break

    driver.quit()
    print(f"\nFinished scraping {len(jobs)} jobs.")
    return pd.DataFrame(jobs)


if __name__ == "__main__":
    df = get_glassdoor_jobs(1000)
    print(df.head())
    df.to_csv("glassdoor_jobs_fixed_4.csv", index=False)
    print("Saved to glassdoor_jobs_fixed.csv")
