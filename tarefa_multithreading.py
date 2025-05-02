import requests
import time
import csv
import random
import concurrent.futures
from bs4 import BeautifulSoup


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

MAX_TREADS = 10

def extract_movie_details(movie_link):
    time.sleep(random.uniform(1, 3))
    response = requests.get(movie_link, headers=headers)
    movie_soup = BeautifulSoup(response.content, 'html.parser')

    if movie_soup is not None:
        title = None
        date = None
        rating = None
        plot_text = None

        page_section = movie_soup.find('section', class_='ipc-page-section')

        if page_section is not None:
            divs = page_section.find_all('div', recursive=False)

            if len(divs) > 1:
                target_div = divs[1]

                title = target_div.find('h1')
                if title:
                    title = title.find('span').get_text()

                date_tag = target_div.find('a', href=lambda href: href and 'releaseinfo' in href)
                if date_tag:
                    date = date_tag.get_text().strip()

                rating_tag = movie_soup.find('div', attrs={'data-testid': 'hero-rating-bar__aggregate-rating__score'})
                rating = rating_tag.find('span').get_text() if rating_tag else None

                plot_tag = movie_soup.find('span', attrs={'data-testid': 'plot-xs_to_m'})
                plot_text = plot_tag.get_text() if plot_tag else None

                with open('movies.csv', 'a', newline='', encoding='utf-8') as file:
                    movie_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    if all([title, date, rating, plot_text]):
                        print(title, date, rating, plot_text)
                        movie_writer.writerow([title, date, rating, plot_text])

def extract_movies_from_page(soup):
    movies_tables = soup.find('div', attrs={'data-testid': 'chart-layout-main-column'}).find('ul')
    movies_tables_rows = movies_tables.find_all('li')
    movie_links = ['https://www.imdb.com' + movie.find('a')['href'] for movie in movies_tables_rows]

    threads = min(MAX_TREADS, len(movie_links))
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(extract_movie_details, movie_links)

def main():
    with open('movies.csv', 'w', newline='', encoding='utf-8') as file:
        movie_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        movie_writer.writerow(['Título', 'Data de Lançamento', 'Avaliação', 'Sinopse'])

    start_time = time.time()

    popular_movies_url = 'https://www.imdb.com/chart/moviemeter/?ref_=nv_mv_mpm'
    response = requests.get(popular_movies_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    extract_movies_from_page(soup)

    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()