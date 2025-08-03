import requests
from bs4 import BeautifulSoup
from scraping_and_processing.scrape import get_fight_links_from_event
from scraping_and_processing.utils import get_fight_stats, get_fighter_stats
from scraping_and_processing.preprocess import make_fight_features
import numpy as np
import pandas as pd
import tensorflow as tf
import os
import time
import random
from dotenv import load_dotenv

def table_features(red, blue, odds):
    winner = red if odds > 0.5 else blue
    score = round((abs(0.5-odds)*2.0)**0.25)
    return winner, f"{score}/10"

load_dotenv()
model = tf.keras.models.load_model("models/nn_raw_output.keras")
UPCOMING_FIGHTS = "http://www.ufcstats.com/statistics/events/upcoming?page=all"
SHEETY_ENDPOINT = "https://api.sheety.co/5fd22a7303f8e2e588ecbc975f0cee99/predictions/ufc"
header = {"Authorization": f"Basic {os.getenv('basic_auth')}"}

print("\n"* 10)

session = requests.Session()
response = session.get(UPCOMING_FIGHTS)
response.raise_for_status()
soup = BeautifulSoup(response.content, "lxml")
event_links = [a["href"] for a in soup.select("a.b-link.b-link_style_black")]
upcoming_fight_links = []
for event in event_links:
    upcoming_fight_links.extend(get_fight_links_from_event(event, session))

people_links = []
names_and_events = []
for upcoming_fight in upcoming_fight_links:
    resp = session.get(upcoming_fight)
    resp.raise_for_status()
    upcoming = BeautifulSoup(resp.content, "lxml")
    fighters = [a["href"] for a in upcoming.select("a.b-link.b-fight-details__person-link")]
    names = [a.text.strip() for a in upcoming.select("a.b-link.b-fight-details__person-link")]
    event_name = upcoming.select_one("a.b-link").text.strip()
    names_and_events.append((names[0], names[1], event_name, fighters[0], fighters[1]))
    if fighters[0] not in people_links:
        people_links.append(fighters[0])
    if fighters[1] not in people_links:
        people_links.append(fighters[1])

historical_fights_links = []

for i, person in enumerate(people_links):
    print(f"procesing {i+1}/{len(people_links)} people:", end="")
    print("\r", end="")
    resp = session.get(person)
    resp.raise_for_status()
    person_soup = BeautifulSoup(resp.content, "lxml")
    links = [tr["data-link"] for tr in person_soup.select("tr.b-fight-details__table-row.b-fight-details__table-row__hover.js-fight-details-click")]
    for link in links:
        if link not in historical_fights_links:
            historical_fights_links.append(link)

print("\n\n")
data = []

for i, link in enumerate(historical_fights_links):
    print(f"getting stats for {i+1}/{len(historical_fights_links)} fights", end= "")
    print("\r", end="")
    try:
        data.append(get_fight_stats(link, session))
    except ValueError as e:
        print(f"\n{e}\n")
    except IndexError as e:
        print(f"\n{e}\n")
    time.sleep(random.uniform(1,3))

df = pd.DataFrame.from_dict(data)
df["date"] = pd.to_datetime(df["date"])
df.sort_values(["date"], ascending= False, inplace=True)

response = session.get(SHEETY_ENDPOINT, headers=header)
response.raise_for_status()
for row in response.json()["ufc"]:
    session.delete(f"{SHEETY_ENDPOINT}/{row['id']}", headers=header)
    time.sleep(0.25)

for i, (red_fighter, blue_fighter, event_name, red_fighter_link, blue_fighter_link) in enumerate(names_and_events):
    try:
        print(f"Predicting {i+1}/{len(names_and_events)} fights:", end="")
        print("\r", end="")
        row = {}
        row["date"] = "August 20, 2205"
        row["red fighter"] = red_fighter
        row["blue fighter"] = blue_fighter
        row["red height"], row["red weight"], row["red reach"], row["red stance"], row["red age"] = get_fighter_stats(red_fighter_link, session)
        row["blue height"], row["blue weight"], row["blue reach"], row["blue stance"], row["blue age"] = get_fighter_stats(blue_fighter_link, session)
        row["winner"] = "not given"
        x = make_fight_features(df= df,row=row,is_this_function_used_for_future_inference=True)
        y = 100.0*float(np.array(tf.sigmoid(model.predict(np.array([x]))))[0][0])
        winner, score = table_features(red_fighter, blue_fighter, y)
        outcome = {"eventName":event_name, "redFighter":red_fighter, "blueFighter":blue_fighter, "winner":winner, "score":score}
        response = session.post(SHEETY_ENDPOINT,json= {"ufc" : outcome}, headers= header)
        response.raise_for_status()
    except ValueError:
        print("\nUnsuccessful fight processing\n")
    except IndexError:
        print("\nUnsuccessful fight processing\n")
    time.sleep(0.2)
    


print("\nDone!")
    



session.close()
