import time
from tkinter import messagebox
from scraper import CreateDriver
import tkinter as tk
import threading
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
import os

logging.basicConfig(filename='example.log', level=logging.INFO)
driver = None
import queue

stop_event = threading.Event()


def partition_list(lst, part):
    n = len(lst)
    if n % part != 0:
        # Calculate the sizes of partitions
        part_size = n // part
        remainder = n % part

        # Initialize partitions
        partitions = [[] for _ in range(part)]

        # Distribute elements as evenly as possible
        idx = 0
        for i in range(part):
            for j in range(part_size):
                partitions[i].append(lst[idx])
                idx += 1
            # If there's a remainder, distribute one element to each partition
            if remainder > 0:
                partitions[i].append(lst[idx])
                idx += 1
                remainder -= 1

        return partitions
    else:
        # If the length is divisible by 3, use list slicing to partition
        part_size = n // part
        return [lst[i * part_size:(i + 1) * part_size] for i in range(part)]


# Scrape Single Movie
def scrape_single_movie(movie, driver, result_queue):
    if stop_event.is_set():
        driver.quit()
        return False
    driver.get(movie)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'home_img')))
    except:
        result_queue.put(f'there was error loading {movie}')
        return False
    temp = {}
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="hero__pageTitle"]')))
        element = driver.find_element(By.CSS_SELECTOR, '[data-testid="hero__pageTitle"]').find_element(By.TAG_NAME,
                                                                                                       'span')
        temp['title'] = element.get_attribute('innerHTML')
    except BaseException as e:
        print(f"An error occurred: {e}")
        result_queue.put(f"An error occurred: cant find title")
        temp['title'] = ''
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'cFndlt')))
        element = driver.find_element(By.CLASS_NAME, 'cFndlt').find_element(By.TAG_NAME, 'ul').find_element(
            By.TAG_NAME, 'a')
        temp['releaseyear'] = element.get_attribute('innerHTML')
    except BaseException as e:
        print(f"An error occurred: {e}")
        result_queue.put(f"An error occurred: cant find releaseyear")
        temp['releaseyear'] = ''
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="hero-rating-bar__aggregate-rating__score"]')))
        element = driver.find_element(By.CSS_SELECTOR, '[data-testid="hero-rating-bar__aggregate-rating__score"]'). \
            find_element(By.TAG_NAME, 'span')
        temp['rating'] = element.get_attribute('innerHTML')
    except BaseException as e:
        print(f"An error occurred: {e}")
        result_queue.put(f"An error occurred: cant find rating")
        temp['rating'] = ''
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((
            By.CSS_SELECTOR, '[data-testid= "title-pc-principal-credit"]')))
        director = [sinelem.find_element(By.TAG_NAME, 'a').get_attribute('innerHTML') for sinelem in
                    driver.find_element(By.CSS_SELECTOR,
                                        '[data-testid= "title-pc-principal-credit"]').find_elements(By.TAG_NAME,
                                                                                                    'li')]
        temp['director'] = ','.join(director)
    except BaseException as e:
        print(e)
        result_queue.put(f"An error occurred: cant find director")

        temp['director'] = ''
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((
            By.CSS_SELECTOR, '[data-testid= "title-cast-item"]')))
        cast = []
        for sinelem in driver.find_elements(By.CSS_SELECTOR, '[data-testid= "title-cast-item"]'):
            tempactor = {}
            try:
                tempactor['actorname'] = sinelem.find_element(By.CSS_SELECTOR,
                                                              '[data-testid="title-cast-item__actor"]').text
            except:
                tempactor['actorname'] = 'unknown'
            try:
                tempactor['character'] = sinelem.find_element(By.CSS_SELECTOR,
                                                              '[data-testid="cast-item-characters-link"]').text
            except:
                tempactor['character'] = 'unknown'
            cast.append(tempactor)

        temp['cast'] = cast
    except BaseException as e:
        result_queue.put(f"An error occurred: cant find cast")

        temp['cast'] = ''
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="plot-l"]')))
        element = driver.find_element(By.CSS_SELECTOR, '[data-testid="plot-l"]')
        temp['plot'] = element.get_attribute('innerHTML')
    except BaseException as e:
        print(f"An error occurred: {e}")
        result_queue.put(f"An error occurred: cant find plot")
        temp['plot'] = ''

    return temp


# Scrape MovieList
def scrape_movies(movielist, result_queue, threadindex, visiblity, moviesqueue):
    result_queue.put(f'  scrapping {len(movielist)}  movies')
    mydriver = CreateDriver(visibility=visiblity)
    moviesdata = []

    for index, movie in enumerate(movielist):
        if stop_event.is_set():
            mydriver.quit()
            return False

        result_queue.put(f'{index}-{threadindex}) scrapping {movie}...')

        getmovie = scrape_single_movie(movie, mydriver, result_queue, index)
        result_queue.put(f'{index}-{threadindex}) complete...')
        if getmovie:
            moviesdata.append(getmovie)
        else:
            continue
    mydriver.quit()
    moviesqueue.put(moviesdata)
    return moviesdata


# Scrape all movies links an pagination
def process_query(query, limitcount, result_queue, visiblity, threadcount):
    try:
        mydriver = CreateDriver(visibility=visiblity)
        mydriver.maximize_window()

        # Open the IMDb search page with the specified query

        searchurl = f"https://www.imdb.com/find/?s=tt&q={query}"
        result_queue.put(f"https://www.imdb.com/find/?s=tt&q={query}")

        mydriver.get(searchurl)

        # Initialize an empty list to store final results
        finalresult = []

        # Wait for the home_img element to ensure the page is loaded
        WebDriverWait(mydriver, 10).until(EC.presence_of_element_located((By.ID, 'home_img')))
        paginationcount = 0
        # Loop until the final result count reaches the limit or no more pages to load
        while True:

            if stop_event.is_set():
                mydriver.quit()
                return False

            # Extract the links of the search results
            try:
                result = [i.find_element(By.CLASS_NAME, 'ipc-metadata-list-summary-item__t').get_attribute('href') for i
                          in
                          mydriver.find_element(By.CSS_SELECTOR,
                                                '[data-testid="find-results-section-title"]').find_elements(
                              By.CLASS_NAME, 'ipc-metadata-list-summary-item')]
            except:
                result_queue.put(f' No records Found')
                return
            paginationcount += 1
            # If the limit count is reached, break the loop

            if limitcount <= len(result):
                finalresult += result
                break
            else:
                try:
                    # Find the pagination container element
                    element = WebDriverWait(mydriver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'find-see-more-title-btn')))
                    viewport_height = mydriver.execute_script("return window.innerHeight;")

                    # Get the height of the element
                    element_height = element.size['height']

                    # Calculate the scroll position to center the element
                    scroll_position = element.location['y'] - (viewport_height / 2) + (element_height / 2)

                    # Scroll to the pagination container element
                    mydriver.execute_script("window.scrollTo(0, arguments[0]);", scroll_position)
                    # wait till element is clickable
                    time.sleep(3)
                    WebDriverWait(mydriver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, 'find-see-more-title-btn'))).click()

                except BaseException as e:
                    # Log any exceptions that occur during the process
                    result_queue.put(f"An error occurred: {e}")
                    finalresult += result
                    break
            result_queue.put(f'got {len(result)}   at page {paginationcount}')

        # Inform the result queue about the start of scraping
        result_queue.put(f'starting to scrape movies..')

        # Call the function to scrape movies with the final result list
        mydriver.quit()

        if len(finalresult) > 0:
            moviestoscrape = finalresult if len(finalresult) < limitcount else finalresult[:limitcount]
            threads = []
            moviesdata = []
            dividedforthread = partition_list(moviestoscrape, threadcount)
            moviesqueue = queue.Queue()

            for singlethread in range(threadcount):
                thread = threading.Thread(target=scrape_movies,
                                          args=(dividedforthread[singlethread], result_queue, singlethread, visiblity,
                                                moviesqueue))
                threads.append(thread)
                thread.start()

            for sint in threads:
                scraped_data = sint.join()
            while not moviesqueue.empty():
                moviesdata += moviesqueue.get()

            result_queue.put('...............DONE.....................')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_file = f"data_{timestamp}.csv"
            json_file = f"data_{timestamp}.json"
            df = pd.DataFrame(moviesdata)
            df.to_csv(csv_file, index=False)
            df.to_json(json_file, orient='records')
            os.system(f'start excel {csv_file}')
            return True
        else:
            return result_queue.put(f'No Movie found with query:   {query}')
    except BaseException as e:
        result_queue.put(str(e))


thread2 = None


# User Interface
def search_popup():
    try:
        root = tk.Tk()
        root.title("Search Popup")

        def search():
            global thread2
            stop_event.clear()
            textarea.delete(1.0, tk.END)

            search_query = entry.get()
            limitcount = limit_entry.get()
            threadcount = threadentry.get()
            # process_query(search_query, int(limitcount))
            if not search_query:
                messagebox.showerror("Error", "Please enter eithere Genre or Keyword")
                textarea.insert(1.0, 'Please enter eithere Genre or Keyword')



            else:
                textarea.insert(1.0, '...............START.....................\n')

                result_queue = queue.Queue()
                thread2 = threading.Thread(target=process_query,
                                           args=(
                                               search_query, int(limitcount), result_queue,
                                               visiblity.get(), int(threadcount)))
                thread2.start()
                root.after(100, check_queue, result_queue)

        def check_queue(result_queue):
            # If there are results in the queue, display them in the textarea
            while not result_queue.empty():
                results = result_queue.get()
                textarea.insert(tk.END, results + "\n")
                textarea.see(tk.END)  # Scroll to the end

            else:
                # If no results yet, check again after a short delay
                root.after(100, check_queue, result_queue)

        def stop_thread():
            global thread2
            if thread2 is not None and thread2.is_alive():
                stop_event.set()  # Set the event to signal all functions to stop
                textarea.insert(tk.END, "Scrapper stopped\n")
            else:
                textarea.insert(tk.END, "Scrapper is not running\n")

        label = tk.Label(root, text="Query:")
        label.pack()

        entry = tk.Entry(root, width=100)
        entry.pack()

        limit_label = tk.Label(root, text="Limit:")
        limit_label.pack()

        limit_entry = tk.Entry(root, width=100)
        limit_entry.insert(0, "10")
        limit_entry.pack()

        threadlabel = tk.Label(root, text="Threads(Allocate as per your Hardware and Internet Speed)!")
        threadlabel.pack()

        threadentry = tk.Entry(root, width=100)
        threadentry.insert(0, "3")
        threadentry.pack()

        visiblity = tk.BooleanVar()
        include_option_checkbox = tk.Checkbutton(root, text="Visible", variable=visiblity)
        include_option_checkbox.pack()
        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.BOTTOM)

        button = tk.Button(button_frame, text="Search", command=search, bg="green", fg="white", font=("Arial", 20))
        button.pack(side=tk.LEFT, padx=5)  # Pack the search button to the left
        stop_button = tk.Button(button_frame, text="Stop", command=stop_thread, bg="red", fg="white",
                                font=("Arial", 20))  # Stop button
        stop_button.pack(side=tk.LEFT, padx=5)  # Pack the stop button to the left
        textarea = tk.Text(root, wrap=tk.WORD, width=100, height=20)
        textarea.pack()
        scrollbar = tk.Scrollbar(root, command=textarea.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        textarea.config(yscrollcommand=scrollbar.set)
        root.mainloop()
    except BaseException as e:
        logging.error(e)


if __name__ == '__main__':
    search_popup()
