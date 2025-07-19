import requests
from bs4 import BeautifulSoup
from datetime import datetime
from functools import lru_cache
EXAMPLE_FIGHT_URL = "http://www.ufcstats.com/fight-details/cab4937435d081d0"
EXAMPLE_FIGHTER_URL = "http://www.ufcstats.com/fighter-details/5444c5a201d3ee5a"
EXAMPLE_EVENT_URL = "http://www.ufcstats.com/event-details/ca936c67687789e9"

def time_to_sec(time:str) -> int:
    x= time.split(":")
    return 60*int(x[0]) + int(x[1])
def extract_numbers(s:str): #only positive integers
    list = []
    i = 0
    while(i < len(s)):
        if s[i].isdigit():
            k = i
            while k<len(s) and s[k].isdigit():
                k += 1
            list.append(int(s[i:k]))
            i = k
        else:
            i += 1
    return list
    

def get_fight_stats(url:str, session):
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")
    event_name = soup.find("h2").text.strip() #name of the event, string
    fighters: list[str,str] = [x.text.strip() for x in soup.select("a.b-link.b-fight-details__person-link")] # list that contains reda and blue fighter names
    basic_info = soup.select("p.b-fight-details__text > i")
    method = basic_info[0].find(attrs={"style":True}).text.strip() # the way the fight ended
    round = int(basic_info[1].text.replace("Round:", "").strip()) # number of rounds that the fight lasted
    time = time_to_sec(basic_info[2].text.replace("Time:", "").strip()) # duration of the fight in seconds
    time_format = int(basic_info[3].text.replace("Time format:", "").strip()[0]) # total number of rounds
    stats1 = [x.text.strip() for x in soup.select("p.b-fight-details__table-text")][:20]
    red_kd = int(stats1[2]) # number of knockdowns by red
    blue_kd = int(stats1[3]) # number of knockdowns by blue
    red_total_str = [int(x) for x in stats1[8].split(" of ")] #list with successful and attempted num of strikes by red, both significant and non significant
    blue_total_str = [int(x) for x in stats1[9].split(" of ")] #list with successful and attempted num of strikes by blue, both significant and non significant
    red_td = [int(x) for x in stats1[10].split(" of ")] #list with successful and attempted num of takedowns by red
    blue_td = [int(x) for x in stats1[11].split(" of ")] #list with successful and attempted num of takedowns by blue
    red_sub_att = int(stats1[14]) #number of submission attempts by red
    blue_sub_att = int(stats1[15]) #number of submission attempts by blue
    red_rev = int(stats1[16]) #number of reversalsby red
    blue_rev = int(stats1[17]) #number of reversals by blue
    red_ctrl = time_to_sec(stats1[18]) #number of seconds in control by red
    blue_ctrl = time_to_sec(stats1[19]) #number of seconds in control by blue
    stats2 = [x.text.strip() for x in soup.select("p.b-fight-details__table-text")][(round+1)*20:(round+1)*20+ 18]
    red_head = [int(x) for x in stats2[6].split(" of ")] #list with successful and attempted num of head strikes by red
    blue_head = [int(x) for x in stats2[7].split(" of ")] #list with successful and attempted num of head strikes by blue
    red_body = [int(x) for x in stats2[8].split(" of ")] #list with successful and attempted num of body strikes by red
    blue_body = [int(x) for x in stats2[9].split(" of ")] #list with successful and attempted num of body strikes by blue
    red_leg = [int(x) for x in stats2[10].split(" of ")] #list with successful and attempted num of leg strikes by red
    blue_leg = [int(x) for x in stats2[11].split(" of ")] #list with successful and attempted num of leg strikes by blue
    red_distance= [int(x) for x in stats2[12].split(" of ")] #list with successful and attempted num of distance strikes by red
    blue_distance = [int(x) for x in stats2[13].split(" of ")] #list with successful and attempted num of distance strikes by blue
    red_clinch = [int(x) for x in stats2[14].split(" of ")] #list with successful and attempted num of clinch strikes by red
    blue_clinch = [int(x) for x in stats2[15].split(" of ")] #list with successful and attempted num of clinch strikes by blue
    red_ground = [int(x) for x in stats2[16].split(" of ")] #list with successful and attempted num of ground strikes by red
    blue_ground = [int(x) for x in stats2[17].split(" of ")] #list with successful and attempted num of ground strikes by blue
    fighter_links = [a['href'] for a in soup.select("a.b-link.b-fight-details__person-link")]
    red_height, red_weight, red_reach, red_stance, red_age = get_fighter_stats(fighter_links[0], session)
    blue_height, blue_weight, blue_reach, blue_stance, blue_age = get_fighter_stats(fighter_links[1], session)
    event_link = soup.select_one("a.b-link")['href']
    date = get_event_date(event_link, session) # date of the event
    red_figther_result = soup.select_one("div.b-fight-details__person > i").text.strip()
    winner = None
    if red_figther_result == "W":
        winner = "red"
    elif red_figther_result == "L":
        winner = "blue"
    else:
        winner = "draw"
    data = {
        "event name":event_name,
        "date":date,
        "red fighter":fighters[0],
        "blue fighter":fighters[1],
        "winner":winner,
        "method":method,
        "time":time,
        "time format":time_format,
        "red height":red_height,
        "red weight":red_weight,
        "red reach":red_reach,
        "red stance":red_stance,
        "red age":red_age,
        "red kd":red_kd,
        "red total str done":red_total_str[0],
        "red total str attempted":red_total_str[1],
        "red td done":red_td[0],
        "red td attempted":red_td[1],
        "red sub attempts":red_sub_att,
        "red rev":red_rev,
        "red ctrl":red_ctrl,
        "red head done":red_head[0],
        "red head attempted":red_head[1],
        "red body done":red_body[0],
        "red body attempted":red_body[1],
        "red leg done":red_leg[0],
        "red leg attempted":red_leg[1],
        "red distance done":red_distance[0],
        "red distance attempted":red_distance[1],
        "red clinch done":red_clinch[0],
        "red clinch attempted":red_clinch[1],
        "red ground done":red_ground[0],
        "red ground attempted":red_ground[1],
        "blue height":blue_height,
        "blue weight":blue_weight,
        "blue reach":blue_reach,
        "blue stance":blue_stance,
        "blue age":blue_age,
        "blue kd":blue_kd,
        "blue total str done":blue_total_str[0],
        "blue total str attempted":blue_total_str[1],
        "blue td done":blue_td[0],
        "blue td attempted":blue_td[1],
        "blue sub attempts":blue_sub_att,
        "blue rev":blue_rev,
        "blue ctrl":blue_ctrl,
        "blue head done":blue_head[0],
        "blue head attempted":blue_head[1],
        "blue body done":blue_body[0],
        "blue body attempted":blue_body[1],
        "blue leg done":blue_leg[0],
        "blue leg attempted":blue_leg[1],
        "blue distance done":blue_distance[0],
        "blue distance attempted":blue_distance[1],
        "blue clinch done":blue_clinch[0],
        "blue clinch attempted":blue_clinch[1],
        "blue ground done":blue_ground[0],
        "blue ground attempted":blue_ground[1]
    }
    return data
@lru_cache(maxsize= 10000)
def get_event_date(url:str, session) -> str:
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")
    return soup.select_one("li.b-list__box-list-item").text.replace("Date:", "").strip()
@lru_cache(maxsize= 10000)
def get_fighter_stats(url:str, session):
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")
    stats= [x.text.strip() for x in soup.select_one("ul.b-list__box-list").find_all("li")]
    height_f_inch = extract_numbers(stats[0])
    height = height_f_inch[0]*12 + height_f_inch[1] #fighter height in inches
    weight = extract_numbers(stats[1])[0] #fighter weight in pounds
    reach = extract_numbers(stats[2])[0] #fighter reach in inches
    stance = stats[3].replace("\n", "").replace("STANCE:", "").strip() #stance of the fighter
    age = int(datetime.now().year) - extract_numbers(stats[-1])[-1] # age of the fighter
    return (height, weight, reach, stance, age)


if __name__ == "__main__":
    session = requests.Session()
    print(get_fight_stats("http://www.ufcstats.com/fight-details/426e7a3de68117b0", session))





    

