import pandas as pd
import csv
EXAMPLE_FIGHTER_NAME = "Jon Jones"
EXAMPLE_DATE = "February 06, 2021"


def make_fighter_features(df: pd.DataFrame,name: str, date:str):
    result_dict = {}
    df = df.copy()
    df["date"]= pd.to_datetime(df["date"])
    df_red = df.loc[(df["red fighter"] == name) & (df["date"] < pd.to_datetime(date))].sort_values(by= ["date"], ascending= False)
    df_blue = df.loc[(df["blue fighter"] == name) & (df["date"] < pd.to_datetime(date))].sort_values(by= ["date"], ascending= False)
    df_all = pd.concat([df_red,df_blue]).sort_values(by= ["date"], ascending= False)
    if len(df_all) == 0:
        raise ValueError(f"No prior fight history for {name}")
    total_time_fighting = float(df_all["time"].sum()) / 60.0 
    result_dict["number of fights"] = len(df_all)
    result_dict["wins"] = len(df_red[df_red["winner"] == "red"]) + len(df_blue[df_blue["winner"] == "blue"])
    result_dict["losses"] = len(df_red[df_red["winner"] == "blue"]) + len(df_blue[df_blue["winner"] == "red"])
    result_dict["draws"] = len(df_all.loc[(df_all["winner"] == "draw") & (df_all["method"] != "Could Not Continue") & (df_all["method"] != "Overturned")])
    result_dict["KO/TKO posibility"] = (len(df_red[(df_red["winner"] == "red") & ((df_red["method"] == "KO/TKO") | (df_red["method"] == "TKO - Doctor's Stoppage"))]) + len(df_blue[(df_blue["winner"] == "blue") & ((df_blue["method"] == "KO/TKO") | (df_blue["method"] == "TKO - Doctor's Stoppage"))]))/len(df_all)
    result_dict["Submission possibility"] = (len(df_red[(df_red["winner"] == "red") & (df_red["method"] == "Submission")]) + len(df_blue[(df_blue["winner"] == "blue") & (df_blue["method"] == "Submission")]))/len(df_all)
    result_dict["percent of 5 round fights"] = len(df_all[df_all["time format"] == 5])/len(df_all)
    result_dict["KD per minute"] = float(df_red["red kd"].sum() + df_blue["blue kd"].sum()) / total_time_fighting
    result_dict["taken KD per minute"] = float(df_red["blue kd"].sum() + df_blue["red kd"].sum()) / total_time_fighting

    result_dict["strikes per minute"] = float(df_red["red total str done"].sum() + df_blue["blue total str done"].sum()) / total_time_fighting
    try:
        result_dict["strike success rate"] = float(df_red["red total str done"].sum() + df_blue["blue total str done"].sum()) / float(df_red["red total str attempted"].sum() + df_blue["blue total str attempted"].sum())
    except ZeroDivisionError:
        result_dict["strike success rate"] = 0.4
    try:
        result_dict["strike absorbment rate"] = float(df_red["blue total str done"].sum() + df_blue["red total str done"].sum()) / float(df_red["blue total str attempted"].sum() + df_blue["red total str attempted"].sum())
    except ZeroDivisionError:
        result_dict["strike absorbment rate"] = 0.4

    result_dict["TD per minute"] = float(df_red["red td done"].sum() + df_blue["blue td done"].sum()) / total_time_fighting
    try:
        result_dict["TD success rate"] = float(df_red["red td done"].sum() + df_blue["blue td done"].sum()) / float(df_red["red td attempted"].sum() + df_blue["blue td attempted"].sum())
    except ZeroDivisionError:
        result_dict["TD success rate"] = 0.4
    try:
        result_dict["TD absorbment rate"] = float(df_red["blue td done"].sum() + df_blue["red td done"].sum()) / float(df_red["blue td attempted"].sum() + df_blue["red td attempted"].sum())
    except ZeroDivisionError:
        result_dict["TD absorbment rate"] = 0.4
    
    try:
        result_dict["submission success rate"] = (len(df_red[(df_red["winner"] == "red") & (df_red["method"] == "Submission")]) + len(df_blue[(df_blue["winner"] == "blue") & (df_blue["method"] == "Submission")])) / float(df_red["red sub attempts"].sum() + df_blue["blue sub attempts"].sum())
    except ZeroDivisionError:
        result_dict["submission success rate"] = 0.4
    try:
        result_dict["submission absorbment rate"] = (len(df_red[(df_red["winner"] == "blue") & (df_red["method"] == "Submission")]) + len(df_blue[(df_blue["winner"] == "red") & (df_blue["method"] == "Submission")])) / float(df_red["blue sub attempts"].sum() + df_blue["red sub attempts"].sum())
    except ZeroDivisionError:
        result_dict["submission absorbment rate"] = 0.4

    result_dict["average control per game"] = float(df_red["red ctrl"].sum() + df_blue["blue ctrl"].sum())/ (result_dict["number of fights"])
    try:
        result_dict["reversal to being controlled ratio"] = float(df_red["red rev"].sum() + df_blue["blue rev"].sum()) / float(df_red["blue ctrl"].sum() + df_blue["red ctrl"].sum())
    except ZeroDivisionError:
        result_dict["reversal to being controlled ratio"] = 0.4

    result_dict["head strikes per minute"] = float(df_red["red head done"].sum() + df_blue["blue head done"].sum()) / total_time_fighting
    try:
        result_dict["head strike success rate"] = float(df_red["red head done"].sum() + df_blue["blue head done"].sum()) / float(df_red["red head attempted"].sum() + df_blue["blue head attempted"].sum())
    except ZeroDivisionError:
        result_dict["head strike success rate"] = 0.4
    try:
        result_dict["head strike absorbment rate"] = float(df_red["blue head done"].sum() + df_blue["red head done"].sum()) / float(df_red["blue head attempted"].sum() + df_blue["red head attempted"].sum())
    except ZeroDivisionError:
        result_dict["head strike absorbment rate"] = 0.4

    result_dict["body strikes per minute"] = float(df_red["red body done"].sum() + df_blue["blue body done"].sum()) / total_time_fighting
    try:
        result_dict["body strike success rate"] = float(df_red["red body done"].sum() + df_blue["blue body done"].sum()) / float(df_red["red body attempted"].sum() + df_blue["blue body attempted"].sum())
    except ZeroDivisionError:
        result_dict["body strike success rate"] = 0.4
    try:
        result_dict["body strike absorbment rate"] = float(df_red["blue body done"].sum() + df_blue["red body done"].sum()) / float(df_red["blue body attempted"].sum() + df_blue["red body attempted"].sum())
    except ZeroDivisionError:
        result_dict["body strike absorbment rate"] = 0.4

    result_dict["leg strikes per minute"] = float(df_red["red leg done"].sum() + df_blue["blue leg done"].sum()) / total_time_fighting
    try:
        result_dict["leg strike success rate"] = float(df_red["red leg done"].sum() + df_blue["blue leg done"].sum()) / float(df_red["red leg attempted"].sum() + df_blue["blue leg attempted"].sum())
    except ZeroDivisionError:
        result_dict["leg strike success rate"] = 0.4
    try:
        result_dict["leg strike absorbment rate"] = float(df_red["blue leg done"].sum() + df_blue["red leg done"].sum()) / float(df_red["blue leg attempted"].sum() + df_blue["red leg attempted"].sum())
    except ZeroDivisionError:
        result_dict["leg strike absorbment rate"] = 0.4

    result_dict["distance strikes per minute"] = float(df_red["red distance done"].sum() + df_blue["blue distance done"].sum()) / total_time_fighting
    try:
        result_dict["distance strike success rate"] = float(df_red["red distance done"].sum() + df_blue["blue distance done"].sum()) / float(df_red["red distance attempted"].sum() + df_blue["blue distance attempted"].sum())
    except ZeroDivisionError:
        result_dict["distance strike success rate"] = 0.4
    try:
        result_dict["distance strike absorbment rate"] = float(df_red["blue distance done"].sum() + df_blue["red distance done"].sum()) / float(df_red["blue distance attempted"].sum() + df_blue["red distance attempted"].sum())
    except ZeroDivisionError:
        result_dict["distance strike absorbment rate"] = 0.4

    result_dict["clinch strikes per minute"] = float(df_red["red clinch done"].sum() + df_blue["blue clinch done"].sum()) / total_time_fighting
    try:
        result_dict["clinch strike success rate"] = float(df_red["red clinch done"].sum() + df_blue["blue clinch done"].sum()) / float(df_red["red clinch attempted"].sum() + df_blue["blue clinch attempted"].sum())
    except ZeroDivisionError:
        result_dict["clinch strike success rate"] = 0.4
    try:
        result_dict["clinch strike absorbment rate"] = float(df_red["blue clinch done"].sum() + df_blue["red clinch done"].sum()) / float(df_red["blue clinch attempted"].sum() + df_blue["red clinch attempted"].sum())
    except ZeroDivisionError:
        result_dict["clinch strike absorbment rate"] = 0.4

    try:
        result_dict["ground strikes per control time"] = float(df_red["red ground done"].sum() + df_blue["blue ground done"].sum()) / float(df_red["red ctrl"].sum() + df_blue["blue ctrl"].sum())
    except ZeroDivisionError:
        result_dict["ground strikes per control time"] = 0
    try:
        result_dict["ground strike success rate"] = float(df_red["red ground done"].sum() + df_blue["blue ground done"].sum()) / float(df_red["red ground attempted"].sum() + df_blue["blue ground attempted"].sum())
    except ZeroDivisionError:
        result_dict["ground strike success rate"] = 0.4
    try:
        result_dict["ground strike absorbment rate"] = float(df_red["blue ground done"].sum() + df_blue["red ground done"].sum()) / float(df_red["blue ground attempted"].sum() + df_blue["red ground attempted"].sum())
    except ZeroDivisionError:
        result_dict["ground strike absorbment rate"] = 0.4

    df_temp = df_all[((df_all["winner"] != "draw") | ((df_all["method"] != "Could Not Continue") & (df_all["method"] != "Overturned")))]
    if len(df_temp) == 0:
        raise ValueError(f"Could not get any fights that are ruled out for {name}")
    history_arr = pd.Series([0]*len(df_temp), index= df_temp.index)

    win_mask = ((df_temp["blue fighter"] == name) & (df_temp["winner"] == "blue")) | ((df_temp["red fighter"] == name) & (df_temp["winner"] == "red"))
    history_arr[win_mask] = 1
    loss_mask = ((df_temp["blue fighter"] == name) & (df_temp["winner"] == "red")) | ((df_temp["red fighter"] == name) & (df_temp["winner"] == "blue"))
    history_arr[loss_mask] = -1
    history_arr = history_arr.values
    
    def get_recent_streak(arr, num):
        for i in range(len(arr)):
            if arr[i] != num:
                return i
        return len(arr)
    def get_longest_streak(arr,num):
        longest_streak= 0
        curr_streak= 0
        i = 0
        while(True):
            if i == len(arr):
                break
            if arr[i] == num:
                curr_streak += 1
                longest_streak = max(curr_streak,longest_streak)
            else:
                curr_streak = 0
            i +=1
        return longest_streak
    def get_appearence_percent(arr,num):
        k = 0
        for i in arr:
            if i == num:
                k += 1
        return k/len(arr)
    
    result_dict["current win streak"] = get_recent_streak(history_arr,1)
    result_dict["longest win streak"] = get_longest_streak(history_arr,1)
    result_dict["current losing streak"] = get_recent_streak(history_arr,-1)
    result_dict["longest losing streak"] = get_longest_streak(history_arr,-1)
    result_dict["last 5 fights win percent"] = get_appearence_percent(history_arr[:5],1)

    return result_dict

def make_fight_features(df: pd.DataFrame, row: pd.Series, with_diff = False):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    red_blue = df[(df["red fighter"] == row["red fighter"]) & (df["blue fighter"] == row["blue fighter"]) & (df["date"] < pd.to_datetime(row["date"]))].sort_values(["date"], ascending= False)
    blue_red = df[(df["red fighter"] == row["blue fighter"]) & (df["blue fighter"] == row["red fighter"]) & (df["date"] < pd.to_datetime(row["date"]))].sort_values(["date"], ascending= False)
    
    if with_diff:
        result_dict = {}
        result_dict["diff height"] = row["red height"] - row["blue height"]
        result_dict["diff weight"] = row["red weight"] - row["blue weight"]
        result_dict["diff reach"] = row["red reach"] - row["blue reach"]
        result_dict["diff age"] = row["red age"] - row["blue age"]
        result_dict["is red orthodox"] = 1 if row["red stance"] == "Orthodox" else 0
        result_dict["is red southpaw"] = 1 if row["red stance"] == "Southpaw" else 0
        result_dict["is red switch"] = 1 if row["red stance"] == "Switch" else 0
        result_dict["is red open stance"] = 1 if row["red stance"] == "Open Stance" else 0
        result_dict["is blue orthodox"] = 1 if row["blue stance"] == "Orthodox" else 0
        result_dict["is blue southpaw"] = 1 if row["blue stance"] == "Southpaw" else 0
        result_dict["is blue switch"] = 1 if row["blue stance"] == "Switch" else 0
        result_dict["is blue open stance"] = 1 if row["blue stance"] == "Open Stance" else 0
        red_stats = make_fighter_features(df,row["red fighter"], row["date"])
        blue_stats = make_fighter_features(df,row["blue fighter"], row["date"])
        for key in red_stats:
            result_dict[f"diff {key}"] = red_stats[key] - blue_stats[key]
        try:
            result_dict["red historical success rate with blue"] = (len(red_blue[red_blue["winner"] == "red"]) + len(blue_red[blue_red["winner"] == "blue"]))/(len(red_blue) + len(blue_red))
        except ZeroDivisionError:
            result_dict["red historical success rate with blue"] = 0.5
    
        try:
            result_dict["blue historical success rate with red"] = (len(red_blue[red_blue["winner"] == "blue"]) + len(blue_red[blue_red["winner"] == "red"]))/(len(red_blue) + len(blue_red))
        except ZeroDivisionError:
            result_dict["blue historical success rate with red"] = 0.5
    
        if row["winner"] == "red":
            result_dict["winner"] = 1
        elif row["winner"] == "blue":
            result_dict["winner"] = 0
        else:
            result_dict["winner"] = 0.5

    else:
        result_dict = {}
        result_dict["red height"] = row["red height"]
        result_dict["red weight"] = row["red weight"]
        result_dict["red reach"] = row["red reach"]
        result_dict["red age"] = row["red age"]
        result_dict["is red orthodox"] = 1 if row["red stance"] == "Orthodox" else 0
        result_dict["is red southpaw"] = 1 if row["red stance"] == "Southpaw" else 0
        result_dict["is red switch"] = 1 if row["red stance"] == "Switch" else 0
        result_dict["is red open stance"] = 1 if row["red stance"] == "Open Stance" else 0
        for key, value in make_fighter_features(df,row["red fighter"], row["date"]).items():
            result_dict[f"red {key}"] = value
        try:
            result_dict["red historical success rate with blue"] = (len(red_blue[red_blue["winner"] == "red"]) + len(blue_red[blue_red["winner"] == "blue"]))/(len(red_blue) + len(blue_red))
        except ZeroDivisionError:
            result_dict["red historical success rate with blue"] = 0.5
    
        result_dict["blue height"] = row["blue height"]
        result_dict["blue weight"] = row["blue weight"]
        result_dict["blue reach"] = row["blue reach"]
        result_dict["blue age"] = row["blue age"]
        result_dict["is blue orthodox"] = 1 if row["blue stance"] == "Orthodox" else 0
        result_dict["is blue southpaw"] = 1 if row["blue stance"] == "Southpaw" else 0
        result_dict["is blue switch"] = 1 if row["blue stance"] == "Switch" else 0
        result_dict["is blue open stance"] = 1 if row["blue stance"] == "Open Stance" else 0
        for key, value in make_fighter_features(df,row["blue fighter"], row["date"]).items():
            result_dict[f"blue {key}"] = value
        try:
            result_dict["blue historical success rate with red"] = (len(red_blue[red_blue["winner"] == "blue"]) + len(blue_red[blue_red["winner"] == "red"]))/(len(red_blue) + len(blue_red))
        except ZeroDivisionError:
            result_dict["blue historical success rate with red"] = 0.5
    
        if row["winner"] == "red":
            result_dict["winner"] = 1
        elif row["winner"] == "blue":
            result_dict["winner"] = 0
        else:
            result_dict["winner"] = 0.5
    
    return result_dict


    


if __name__ == "__main__":
    WITH_DIFF = False
    data = pd.read_csv("../data/fights.csv")
    fieldnames = make_fight_features(data, data.iloc[3400],WITH_DIFF).keys()
    with open(f"../data/{'diff_' if WITH_DIFF else ''}preprocessed.csv", "w", newline= "") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
    
    successful = 0
    failed = 0
    for _ , row in data.iterrows():
        if row["method"] == "Could Not Continue" or row["method"] == "Overturned":
            failed += 1
            continue
        try:
            features= make_fight_features(data, row, WITH_DIFF)
            with open(f"../data/{'diff_' if WITH_DIFF else ''}preprocessed.csv", "a", newline= "") as file:
                writer= csv.DictWriter(file, fieldnames= fieldnames)
                writer.writerow(features)
            successful += 1
        except ValueError:
            failed += 1
        print(f"Successfuly preprocessed {successful}/{len(data)} fights, failed to preprocess {failed} fights", end="")
        print("\r", end="")

    print("\nDone preprocessing!")



