# %%
import requests
from bs4 import BeautifulSoup
import pandas as pd

# %%
def get_html(job: str = 'Data Engineer', region: str = None, country: str = 'UK', page: int = 0, pos: int = 1) -> bytes:
    '''
    Returns the html for a given LinkedIn job search.
    Takes a job title, region (e.g. Manchester) and country,
    as well as the page number for the results.
    '''
    # Url parts
    search = job.replace(' ', '-')                          # The job title
    if region:                                              # The region (e.g. Manchester) if required
        search += f'-{region.replace(" ", "-")}-area'

    domain = country.replace(' ', '-')                      # The country

    # Create search url
    url = f'https://www.linkedin.com/jobs/{search}-jobs/?originalSubdomain={domain}&pageNum={page}&position={pos}'
    print(url)

    # Get html for page
    response = requests.get(url)

    return response.content

html = get_html()

# %%
def get_job_data(html: bytes, df_cols: list) -> pd.DataFrame:
    
    # Parse html into soup object
    soup = BeautifulSoup(html, 'html.parser')

    # Find all job cards in page
    cards = soup.find_all('div', attrs={'class': 'base-card'})

    # Scrape data from elements
    df_page = pd.DataFrame(columns=df_cols)

    for card in cards[:10]:   
        if list_date := card.find(
            'time', attrs={'class': 'job-search-card__listdate'}
            ):
            list_date = list_date.get('datetime')

        if job_title := card.find(
            'h3', attrs={'class': 'base-search-card__title'}
            ):
            job_title = job_title.text.strip()

        if company := card.find(
            'a', attrs={'class': 'hidden-nested-link'}
            ):
            company = company.text.strip()

        if location := card.find('span', attrs={'class': 'job-search-card__location'}
            ):
            location = location.text.strip()
        
        if salary := card.find('span', attrs={'class': 'job-search-card__salary-info'}
            ):
            salary = salary.text.strip()

        if link := card.find('a', attrs={'class': 'base-card__full-link'}
            ):
            link = link.get('href')

        # Create list of item values
        row_list = [[list_date], [job_title], [company], [location], [salary], [link]]

        # Create dictionary of items and headers
        row_dict = dict(zip(df_cols, row_list))

        # Create dataframe of row from dict
        df_row = pd.DataFrame(row_dict, index=None)


        # Join row of data to dataframe
        df_page = pd.concat([df_page, df_row], ignore_index=True)
        
    return df_page


# %%
cols = ['list_date', 'job_title', 'company', 'location', 'salary', 'link']
df = pd.DataFrame(columns= cols)

for i in range(1):
    html = get_html(page = i)
    df_page = get_job_data(html, cols)
    df = pd.concat([df, df_page])

# %%
df.info()
# %%
df.to_csv('jobs.csv')
# %%
