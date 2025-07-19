from utils import get_fight_stats, EXAMPLE_FIGHT_URL
from bs4 import BeautifulSoup
import requests
import csv
UFC_EVERY_EVENT = "http://www.ufcstats.com/statistics/events/completed?page=all"

def get_fight_links_from_event(url:str, session):
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")
    return [a['data-link'] for a in soup.find_all("tr", attrs= {"data-link":True})]

if __name__ == "__main__":

    session = requests.Session()
    
    response = session.get(UFC_EVERY_EVENT)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")
    event_links = [a['href'] for a in soup.select("a.b-link.b-link_style_black")]
    fight_links = []
    for i, event in enumerate(event_links):
        fight_links.extend(get_fight_links_from_event(event, session))
        print(f"Found links for fights from {i+1} events", end="")
        print("\r", end="")
        
    print("\n")
    fieldnames = get_fight_stats(EXAMPLE_FIGHT_URL, session).keys()
    with open("../data/fights.csv", "w", newline= "") as f:
        writer = csv.DictWriter(f, fieldnames= fieldnames)
        writer.writeheader()
    
    lenght = len(fight_links)
    successful = 0
    failed = 0
    for fight in fight_links:
        try:
            fight_info = get_fight_stats(fight, session)
            with open("../data/fights.csv", "a", newline= "") as f:
                writer = csv.DictWriter(f, fieldnames= fieldnames)
                writer.writerow(fight_info)
            successful += 1
        except:
            failed += 1
    
        print(f"Found info for {successful}/{lenght} fights, failed to scrape {failed} fights", end="")
        print("\r", end="")
    
    print("\nDone scraping!")