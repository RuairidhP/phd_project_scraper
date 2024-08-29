import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
import xlsxwriter
import re
from datetime import date

# Scraping functions
def collect_st_andrews():
    standrews_titles = []
    standrews_description = []
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=True) # Opens chromium. headless=True opens in the background, False makes it visible.
        # Open a new page
        page = browser.new_page()
        # Go to the target URL
        page.goto('https://www.st-andrews.ac.uk/physics-astronomy/prospective/pgr/phd-project-search/?form=simple&profile=_default&query=!nullquery&collection=uosa-web-physics-phd-projects&f.Theme|theme=Condensed+Matter&start_rank=11&num_ranks=50')

        # Wait for the results to load
        page.wait_for_selector('li.search-result')

        # Scrape the relevant data
        projects = page.query_selector_all('li.search-result')
        for project in projects:
            standrews_titles.append(project.query_selector('h3.search-result__heading').inner_text())
            standrews_description.append(project.query_selector('div > p').inner_text())

        page = browser.new_page()

        page.goto('https://www.st-andrews.ac.uk/physics-astronomy/prospective/pgr/phd-project-search/?form=simple&profile=_default&query=!nullquery&num_ranks=50&collection=uosa-web-physics-phd-projects&f.Theme|theme=Photonics')
        page.wait_for_selector('li.search-result')
        projects = page.query_selector_all('li.search-result')
        for project in projects:
            standrews_titles.append(project.query_selector('h3.search-result__heading').inner_text())
            standrews_description.append(project.query_selector('div > p').inner_text())

        # Close the browser
        browser.close()
    return standrews_titles, standrews_description

def collect_strathclyde():
    strath_base_url = 'https://www.strath.ac.uk'
    source_strath_phys = requests.get('https://www.strath.ac.uk/courses/research/physics/')
    soup_strath_phys = BeautifulSoup(source_strath_phys.text, 'html.parser')

    phd_opportunities_div = soup_strath_phys.find('div',id='current-opportunities')  # '.' stands for class, # stands for id. Find the content under the <div class = "accordion-content-inner"... ...> section of the html page.
    phd_articles = phd_opportunities_div.find_all('a')  # Find all articles <a> tags within the above div tag.

    strath_phd_titles = []
    strath_phd_links = []
    strath_phd_desc = []
    for article in phd_articles:
        strath_phd_titles.append(article.find('h3').get_text())
        strath_phd_links.append(urljoin(strath_base_url, article.get('href')))
        strath_phd_desc.append(article.find('p').get_text())
    return strath_phd_titles, strath_phd_links, strath_phd_desc

def collect_glasgow():
    glasgow_base_url = 'https://www.gla.ac.uk/'
    source_glasgow_mcmp = requests.get('https://www.gla.ac.uk/schools/physics/research/groups/mcmp/phdstudy/phdprojects/')
    soup_glasgow_mcmp = BeautifulSoup(source_glasgow_mcmp.text, 'html.parser')
    project_divs = soup_glasgow_mcmp.find_all('div', class_='maincontent-inner')

    glas_materials_titles = []
    glas_materials_desc = []

    for project in project_divs:
        glas_materials_titles.append(project.find('h2').get_text())
        temp = ' '
        for p in project.find_all('p'):
            temp += p.get_text()
        glas_materials_desc.append(temp)
    return glas_materials_titles, glas_materials_desc


# Assign lists to variables for use in Excel writer
strath_titles, strath_links, strath_desc = collect_strathclyde()
st_andrews_titles, st_andrews_desc = collect_st_andrews()
glas_materials_title, glas_materials_descriptions = collect_glasgow()


# Write to excel document in different sheets
with pd.ExcelWriter(f'current_phd_opportunities_{date.today()}.xlsx', engine='xlsxwriter') as writer:
    df_strath = pd.DataFrame({
        'Title': strath_titles,
        'Description': strath_desc,
        'Link' : strath_links,
    })
    df_strath.to_excel(writer, sheet_name='Strathclyde', index=False)

    df_standrews = pd.DataFrame({
        'Title': st_andrews_titles,
        'Description': st_andrews_desc,
        'Link' : (len(st_andrews_titles)) * ['https://www.st-andrews.ac.uk/physics-astronomy/prospective/pgr/phd-project-search/?form=simple&profile=_default&query=!nullquery&collection=uosa-web-physics-phd-projects&f.Theme|theme=Condensed+Matter&start_rank=11&num_ranks=50']
    })
    df_standrews.to_excel(writer, sheet_name='St_Andrews', index=False)

    df_glasgow = pd.DataFrame({
        'Title': glas_materials_title[1:],
        'Description': glas_materials_descriptions[1:],
        'Link': len(glas_materials_title[1:]) * ['https://www.gla.ac.uk/schools/physics/research/groups/mcmp/phdstudy/phdprojects/']
    })
    df_glasgow.to_excel(writer, sheet_name='Glasgow', index=False)
