
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import re

orig_url = 'https://draft.shgn.com/nfc/public/dp/788/grid'

driver = webdriver.Chrome('C:\chromedriver_win32\chromedriver.exe')
driver.get(orig_url)
table_entries = WebDriverWait(driver, 40).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "table tr span.lname.ng-binding.medium")))
print(len(table_entries))
print(table_entries)
html = driver.page_source
r = html
open('site.txt', 'wt').write(html)
driver.quit()



# Initialize lists to store the team-owner pairs
player_names_pairs = []

# Open the site.txt file for reading
with open('site.txt', 'r') as f:
    # Read each line of the file
    for line in f:
        # Find all occurrences of the team name between the tags
        first_names = re.findall(r'dbs\.player\.f">(.*?)</span>', line)
        # Find all occurrences of the owner name between the tags
        owner_names = re.findall(r'class="team-owner-name ng-binding">(.*?)</span>', line)
        # Find all occurrences of the last name between the tags
        last_names = re.findall(r'dbs\.player\.l">(.*?)</span>', line)
        # If any team names and owners were found, concatenate them and add to the team_owner_pairs list
        if first_names and last_names:
            for i in range(len(first_names)):
                player_names_pairs.append(f'{first_names[i]} {last_names[i]}')

# Split the team-owner pairs into chunks of 15, filling in empty values if necessary
num_pairs = len(player_names_pairs)
num_cols = 15
player_names_chunked = [player_names_pairs[i:i+num_cols] + ['']*(num_cols-len(player_names_pairs[i:i+num_cols])) for i in range(0, num_pairs, num_cols)]
#player_names_chunked[len(player_names_chunked)-1].reverse()

shift = 0
if(num_pairs!=num_cols*50):
    test1 = int(num_pairs//num_cols)
    test2 = test1%2
    if(test2==1):
        #player_names_chunked[len(player_names_chunked)-1] = player_names_chunked[len(player_names_chunked)-1].reverse()
        shift = sum(1 for e in player_names_chunked[len(player_names_chunked)-1] if e)
        for alfa in range(0,shift):
            player_names_chunked[len(player_names_chunked)-1].append(player_names_chunked[len(player_names_chunked)-1].pop(0))

# Create a dataframe from the chunked team-owner pairs with column headers named after owner names
df = pd.DataFrame(player_names_chunked, columns=[f'{i}' for i in range(15)])

# Print the dataframe
print(df)

url_id_map='https://drive.google.com/file/d/1KdSy7hWrrvpBbDVlR07yv5xxjZdfKK2F/view?usp=share_link'
url_id_map='https://drive.google.com/uc?id=' + url_id_map.split('/')[-2]
df_id_map = pd.read_csv(url_id_map)

# Create a new empty dataframe with the same shape as df
df_id = pd.DataFrame(index=df.index, columns=df.columns)

# Loop through each cell in df and find the corresponding value in df_id_map
for i in range(df.shape[0]):
    for j in range(df.shape[1]):
        # Get the value in the current cell of df
        value = df.iloc[i, j]
        # Find the corresponding row in df_id_map where the value matches the 'Name' column
        match = df_id_map.loc[df_id_map['NFBCNAME'] == value]
        if not match.empty:
            # If a match is found, get the value in the 'NFBCNAME' column
            nfbcname = match.iloc[0]['IDFANGRAPHS']
            # Set the corresponding cell in df_id to the nfbcname value
            df_id.iloc[i, j] = nfbcname
        else:
            # If no match is found, set the corresponding cell in df_id to the original value
            df_id.iloc[i, j] = value

# Print the df_id dataframe
print(df_id)


# Get the column names for the new dataframes
col_names = df_id.columns[0:15]

# Create a dictionary to store the new dataframes
dfs = {}

# Loop through each column name and create a new dataframe
for col_name in col_names:
    new_df = pd.DataFrame(df_id[col_name], columns=[col_name])
    dfs[col_name] = new_df

# Unpack the 15 dataframes from dfs
team01, team02 = dfs['0'], dfs['1']
#team02 = dfs['1']
team03 = dfs['2']
team04 = dfs['3']
team05 = dfs['4']
team06 = dfs['5']
team07 = dfs['6']
team08 = dfs['7']
team09 = dfs['8']
team10 = dfs['9']
team11 = dfs['10']
team12 = dfs['11']
team13 = dfs['12']
team14 = dfs['13']
team15 = dfs['14']

# Load the hitters and pitchers dataframes from CSV files
hitters_df = pd.read_csv('hitters.csv')
pitchers_df = pd.read_csv('pitchers.csv')
pitchers_df['act'] = 'pitcher'

# Define a function that takes a team dataframe as input and returns a merged dataframe
def merge_team_dataframe(team_df):
    # Merge with the hitters dataframe
    merged_df = pd.merge(team_df, hitters_df, left_on=team_df.columns[0], right_on='PlayerId', how='left')

    # Return the merged dataframe
    return merged_df

def merge_team_dataframe2(team_df):
    # Merge with the pitchers dataframe
    merged_df = pd.merge(team_df, pitchers_df, on='PlayerId', how='left')
    # Return the merged dataframe
    return merged_df

rankings = pd.DataFrame(columns=['Team', 'R', 'HR', 'RBI', 'SB', 'AVG', 'W', 'K',
                                 'SV', 'WHIP', 'ERA'])
# Loop through the team dataframes and merge each one with the hitters and pitchers dataframes
for i in range(1, 16):
    # Load the team dataframe
    team_df = globals()[f'team{i:02d}']

    # Merge the team dataframe with the hitters and pitchers dataframes
    merged_df = merge_team_dataframe(team_df)
    merged_df = merged_df.iloc[: , :-2]
    merged_df.columns.values[0] = "PlayerId"
    #print(merged_df)
    merged_df = merge_team_dataframe2(merged_df)
    merged_df = merged_df.loc[:, ['PlayerId', 'Name_x', 'Team_x', 'G_x', 'PA', 
                                  'AB', 'H_x', 'HR_x', 'R_x', 'RBI', 'SB', 
                                  'Name_y', 'Team_y', 'W', 'G_y', 'GS', 'SV', 
                                  'IP', 'H_y', 'ER', 'BB_y', 'SO_y', 'act']]
    merged_df['Name_x'] = merged_df['Name_x'].fillna(merged_df['Name_y'])
    merged_df['act'] = merged_df['act'].fillna('hitter')
    
    
    atbats = merged_df.loc[merged_df['act'] == 'hitter', 'AB'].sum()
    hits = merged_df.loc[merged_df['act'] == 'hitter', 'H_x'].sum()
    rankings.at[i-1, 'Team'] = f'team{i:02d}'
    rankings.at[i-1, 'AVG'] = hits/atbats
    rankings.at[i-1, 'R'] = merged_df['R_x'].sum()
    rankings.at[i-1, 'HR'] = merged_df['HR_x'].sum()
    rankings.at[i-1, 'RBI'] = merged_df['RBI'].sum()
    rankings.at[i-1, 'SB'] = merged_df['SB'].sum()

    earned_r = merged_df.loc[merged_df['act'] == 'pitcher', 'ER'].sum()
    innings = merged_df.loc[merged_df['act'] == 'pitcher', 'IP'].sum()
    walks = merged_df.loc[merged_df['act'] == 'pitcher', 'BB_y'].sum()
    hits = merged_df.loc[merged_df['act'] == 'pitcher', 'H_y'].sum()
    
    rankings.at[i-1, 'ERA'] = (earned_r*9)/innings
    rankings.at[i-1, 'W'] = merged_df['W'].sum()
    rankings.at[i-1, 'K'] = merged_df['SO_y'].sum()
    rankings.at[i-1, 'SV'] = merged_df['SV'].sum()
    rankings.at[i-1, 'WHIP'] = (walks+hits)/innings

    print(merged_df)

    # Save the merged dataframe to a new variable with the same name as the original dataframe
    globals()[f'team{i:02d}'] = merged_df

# Iterate over each column in the original DataFrame
for col in rankings.columns:
    # Sort the column in descending order
    if(col=='WHIP' or col=='ERA'):
        sorted_col = rankings[col].sort_values(ascending=False)
    else:
        sorted_col = rankings[col].sort_values(ascending=True)

    # Assign points to each value based on its rank
    points = pd.Series(range(1, len(sorted_col) + 1), index=sorted_col.index)
    
    # Add the new column to the ranked DataFrame
    rankings[col + '_rank'] = points

acc = 0
for j in range(0,15):
    for col in rankings.columns:
        if(col.endswith('_rank')):
            acc = acc + rankings.iloc[j][col]
    rankings.at[j, 'TOTAL'] = acc
    acc = 0

rankings = rankings.sort_values(by='TOTAL', ascending=False)
temp_cols=rankings.columns.tolist()
new_cols=temp_cols[-1:] + temp_cols[:-1]
rankings=rankings[new_cols]

league_id = re.findall(r'\d+', orig_url)

rankings.to_csv(f'rankings_{league_id[0]}.csv')

# find the matching IDFANGRAPHS values for each player name in the list
id_list = []
for player_name in player_names_pairs:
    match = df_id_map.loc[df_id_map['NFBCNAME'] == player_name, 'IDFANGRAPHS'].values
    if len(match) > 0:
        id_list.extend(match)

# find the records in the hitters and pitchers dataframes that don't have a matching IDFANGRAPHS value
available_hitters = hitters_df.loc[~hitters_df['PlayerId'].isin(id_list)]
available_pitchers = pitchers_df.loc[~pitchers_df['PlayerId'].isin(id_list)]

# merge the available hitters and pitchers dataframes into one dataframe
available_players = pd.concat([available_hitters, available_pitchers])

# print the available players dataframe
print(available_players)

available_players = available_players.drop(available_players.columns.difference(['Name' , 
    'Team' , 'PA' , 'HR' , 'R' , 'RBI' , 'SO' , 'SB' , 'CS' , 'AVG' , 
    'ADP' , 'W' , 'ERA' , 'SV' , 'HLD' , 'IP' , 'WHIP' , 'FIP' , 'act']), axis=1)
available_players.to_csv(f'available.csv')