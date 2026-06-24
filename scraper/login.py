
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from streamlit import title
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import requests
import os
import time
#======================================


#======================================
# Load environment variables
#======================================

load_dotenv()

USERNAME = os.getenv("MOODLE_USERNAME")
PASSWORD = os.getenv("MOODLE_PASSWORD")

#======================================
# Create Folder for Raw Documents
#======================================
os.makedirs("documents/raw", exist_ok=True)

#======================================
# Start Chrome
#======================================

driver = webdriver.Chrome(
    service = Service(ChromeDriverManager().install())
)

wait = WebDriverWait(driver, 20)

#======================================
# Open RUConnected Login Page and Perform Login
#======================================

driver.get("https://ruconnected.ru.ac.za/login/index2.php")

#Step 1: Click Rhodes Login
rhodes_login = wait.until(
    EC.element_to_be_clickable((By.LINK_TEXT, "Rhodes Login"))
)

rhodes_login.click()

#Step 2: Click Students
students_button = wait.until(
    EC.element_to_be_clickable((By.ID, "button-ldap-students"))
)

students_button.click()

#Step 3: Wait for username/password page
username_input = wait.until(
    EC.visibility_of_element_located((By.NAME, "username"))
)

password_input = wait.until(
    EC.visibility_of_element_located((By.NAME, "password"))
)

#Step 4: Enter credentials and submit
username_input.send_keys(USERNAME)
password_input.send_keys(PASSWORD)

#Step 5: Submit form
password_input.send_keys(Keys.RETURN)

time.sleep(5)  # Wait for login to complete, adjust as necessary    

print("logged in successfully")
print(driver.current_url)
print(driver.title)

#======================================
# Find course links
#======================================

course_links = driver.find_elements(By.TAG_NAME, "a")

courses = []

for link in course_links:
    href = link.get_attribute("href")
    title = link.text.strip()

    if href and "course/view.php?id=" in href:
        courses.append({
            "title": title if title else "Unknown Course",
            "url": href
        })

# Remove duplicates
unique_courses = []

seen = set()

for course in courses:

    if course["url"] not in seen:
        unique_courses.append(course)
        seen.add(course["url"])

print("\n======================================")
print(f"Unique Courses Found: {len(unique_courses)}")
print("======================================\n")

for index, course in enumerate(unique_courses):

    print(f"{index + 1}. {course['title']}")
    print(course["url"])
    print()


#======================================
# Create session
#======================================

session = requests.Session()

for cookie in driver.get_cookies():

    session.cookies.set(
        cookie['name'],
        cookie['value']
    )


#======================================
# Visit each course
#======================================

downloaded_urls = set()

allowed_content_types = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain"
]

for course_index, course in enumerate(unique_courses, start=1):


    driver.get(course["url"])

    try:

        course_title = wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "h1.header-heading")
            )
        ).text.strip()

        print("\n======================================")
        print("Course Title")
        print(repr(course_title))
        print(f"{course_index}/{len(unique_courses)}")
        print("======================================\n")

    except Exception as e:
        print(f"Could not get course title: {e}")
        continue

    # ========================================
    # OPTIONAL COURSE FILTER
    # ========================================

    interesting_keywords = [
        "ACC"
        "CSc",
        "Cs",
        "IS3",
        "Operating",
        "Programming",
        "Software",
        "web",
        "Systems"
    ]

    if  not any(
        keyword.lower() in course_title.lower()
        for keyword in interesting_keywords
    ): 
        print("Skipping non-academic courses")
        continue

    time.sleep(3)

    links = driver.find_elements(By.TAG_NAME, "a")

    file_count = 0

    #-------------------------------------------
    #Create folder for course
    #-------------------------------------------

    safe_course_name = "".join(
        c for c in course_title
        if c.isalnum() or c in (" ", "_", "-")
    ).strip()

    course_folder = os.path.join(
        "documents",
        "raw",
        safe_course_name
    )

    os.makedirs(course_folder, exist_ok=True)

    # -------------------------------------------
    # Scan resources
    # -------------------------------------------

    resource_urls = set()

    for link in links:

        try:

            href = link.get_attribute("href")

            if href and "mod/resource/view.php" in href:

                resource_urls.add(href)

        except Exception:
            pass

    print(f"\nFound {len(resource_urls)} resource pages")

    print(f"Before dedup: {len(resource_urls)}")
    resource_urls = list(dict.fromkeys(resource_urls))
    print(f"After dedup: {len(resource_urls)}")

    for  resource_index, resource_url in enumerate(resource_urls, start=1):

        try:

            print("\n---------------------------------------")
            print("Opening Resource")
            print(f"{resource_index}/{len(resource_urls)}")
            print(resource_url)

            driver.get(resource_url)

            print("\nWaiting...\n")

            time.sleep(5)

            print("Current URL:")
            print(driver.current_url)

            print("Page Title:")
            print(driver.title)

            final_url = driver.current_url

            print("Final URL:")
            print(final_url)

            if "pluginfile.php" not in final_url:

                print("Not a downloadable file")
                continue
        
            response = session.get(final_url)

            final_name = unquote(
                final_url.split("/")[-1].split("?")[0]
            )

            print("File:", final_name)

            file_path = os.path.join(
                course_folder,
                final_name
            )

            if os.path.exists(file_path):

                print("File already exists, skipping download")
                continue

            with open(file_path, "wb") as f:
                f.write(response.content)

            print("Downloaded")

            file_count += 1

        except Exception as e:
            print(f"Failed to download resource: {e}")

    # for link in links:

    #     href = link.get_attribute("href")

    #     if not href:
    #         continue

    #     if "pluginfile.php" in href:
    #         continue

    #     if href in downloaded_urls:
    #         continue
    #     downloaded_urls.add(href)

    #     print("\n---------------------------------------")
    #     print("Resource found")
    #     print("Link text:", repr(link.text))
    #     print("URL:", href)

    #     try:

    #         # -------------------------------------------
    #         # Check file info before downloading
    #         # -------------------------------------------

    #         head_response = session.head(
    #             href,
    #             allow_redirects=True
    #         )

    #         content_type = head_response.headers.get(
    #             "Content-Type",
    #             ""
    #         )

    #         file_size_mb = (
    #             int(
    #                 head_response.headers.get(
    #                     "Content-Length",
    #                     0
    #                 )
    #             )
    #             / (1024 * 1024)
    #         )

    #         print("Content Type:", content_type)
    #         print(f"File Size: {file_size_mb:.2f} MB")

    #         # -------------------------------------------
    #         # Skip Unwanted Files
    #         # -------------------------------------------

    #         if content_type not in allowed_content_types:

    #             print("Skipping unsupported file type")
    #             continue

    #         if file_size_mb > 50:
    #             print("Skipping huge file")
    #             continue

    #         # -------------------------------------------
    #         # Extract Real Filename
    #         # -------------------------------------------

    #         url_parts = href.split("/")

    #         file_name = None

    #         for part in reversed(url_parts):

    #             part = unquote(part)

    #             if "." in part:
    #                 file_name = part
    #                 break

    #         if not file_name:

    #             file_name = f"resource_{file_count}"

    #         # Clean filename

    #         file_name = "".join(
    #             c for c in file_name
    #             if c.isalnum() or c in (" ", "_", "-", ".")
    #         ).strip()

    #         print("File name:", file_name)

    #         file_path = os.path.join(
    #             course_folder,
    #             file_name
    #         )

    #         # -------------------------------------------
    #         # Download File
    #         # -------------------------------------------

    #         response = session.get(
    #             href,
    #             allow_redirects=True
    #         )

    #         with open(file_path, "wb") as f:

    #             f.write(response.content)

    #         print("Download Successfully")

    #         file_count += 1

    #     except Exception as e:
    #         print(f"Download failed: {e}")

    
    # print(
    #     f"\nTotal files downloaded for "
    #     f"{course_title}: {file_count}"
    # )


print("\n======================================")
print("Scraping complete")
print("======================================\n")

driver.quit()