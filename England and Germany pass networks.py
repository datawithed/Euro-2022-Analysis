#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 20:30:54 2022

@author: edmorris
"""

##### Euro 2022 Final: Pass Networks #####

# Import modules
import pandas as pd
from mplsoccer import Sbopen, VerticalPitch, add_image
from matplotlib import rcParams
import matplotlib.pyplot as plt
from PIL import Image

# Change font and plot resolutions
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Tahoma']
rcParams['figure.dpi'] = 750

# Team badges
eng_badge = Image.open('England_badge.png')
ger_badge = Image.open('Germany_badge.png')

# Set StatsBomb API IDs
comp_id = 53 # Women's Euro 2022
season_id = 106 # 2022

# Define parser to extract match data
parser = Sbopen()

# Use API IDs to extract match ids
df_match = parser.match(competition_id=comp_id,season_id=season_id)

# Filter for final matchid
final_matchid = df_match.loc[df_match.competition_stage_name == 'Final'].reset_index(drop=True)

# Extract data for matchid
events, df_related, df_freeze, df_tactics = parser.event(final_matchid.match_id[0])

# Create variable for minute of first subs
eng_first_sub_min = 56
ger_first_sub_min = 45

# Filter datasets for each team
eng_events = events.copy().loc[events.team_name == "England Women's"]
ger_events = events.copy().loc[events.team_name == "Germany Women's"]

# Filter each team df for events before first sub made
eng_events = eng_events.loc[eng_events.minute < eng_first_sub_min]
ger_events = ger_events.loc[ger_events.minute < ger_first_sub_min]

# Filter for passes
eng_passes = eng_events.copy().loc[(eng_events.type_name == 'Pass') & (eng_events.outcome_name.isna())]
ger_passes = ger_events.copy().loc[(ger_events.type_name == 'Pass') & (ger_events.outcome_name.isna())]

# Find average locations
avg_eng_locs = eng_passes.groupby('player_name').agg({'x':['mean'],'y':['mean','count']}).reset_index()
avg_eng_locs.columns = ['player_name','x','y','count']
avg_eng_locs['squad_no'] = [7,9,14,10,4,11,8,2,1,6,3]
avg_ger_locs = ger_passes.groupby('player_name').agg({'x':['mean'],'y':['mean','count']}).reset_index()
avg_ger_locs.columns = ['player_name','x','y','count']
avg_ger_locs['squad_no'] = [17,15,22,3,7,6,20,5,1,13,9]

# Find passes between each player
eng_pass_between = eng_passes.groupby(['player_name','pass_recipient_name']).id.count().reset_index()
eng_pass_between = eng_pass_between.rename(columns={'id':'pass_count'})
ger_pass_between = ger_passes.groupby(['player_name','pass_recipient_name']).id.count().reset_index()
ger_pass_between = ger_pass_between.rename(columns={'id':'pass_count'})

# Change col types for merge
eng_pass_between['player_name'] = eng_pass_between.player_name.astype(str)
avg_eng_locs['player_name'] = avg_eng_locs.player_name.astype(str)
ger_pass_between['player_name'] = ger_pass_between.player_name.astype(str)
avg_ger_locs['player_name'] = avg_ger_locs.player_name.astype(str)

# Merge to get passer and recipient avg coords
eng_pass_between = eng_pass_between.merge(avg_eng_locs[['player_name','x','y']],how='left',on='player_name')
eng_pass_between = eng_pass_between.merge(avg_eng_locs[['player_name','x','y']],left_on='pass_recipient_name',right_on='player_name',suffixes=['','_end'])
ger_pass_between = ger_pass_between.merge(avg_ger_locs[['player_name','x','y']],how='left',on='player_name')
ger_pass_between = ger_pass_between.merge(avg_ger_locs[['player_name','x','y']],left_on='pass_recipient_name',right_on='player_name',suffixes=['','_end'])

# Rename columns
eng_pass_between.columns = ['passer','recipient','pass_count','x','y','recipient1','x_end','y_end']
ger_pass_between.columns = ['passer','recipient','pass_count','x','y','recipient1','x_end','y_end']

# Set widths of pass lines to count of passes
max_linewidth = 15
eng_pass_between['width'] = ((eng_pass_between.pass_count / eng_pass_between.pass_count.max()) * max_linewidth)
ger_pass_between['width'] = ((ger_pass_between.pass_count / ger_pass_between.pass_count.max()) * max_linewidth)

# Plot 2x1 pitches for ENG and GER pass networks
pitch = VerticalPitch(pitch_type='statsbomb',pitch_color='#1E4966',line_color='#c7d5cc')
fig, ax = pitch.grid(ncols=2,axis=False,title_space=0.05,endnote_space=0,endnote_height=0.05)
fig.set_facecolor('#1E4966')
# England pass lines
eng_lines = pitch.lines(eng_pass_between.x,eng_pass_between.y,
                      eng_pass_between.x_end,eng_pass_between.y_end,
                      ax=ax['pitch'][0],
                      lw = eng_pass_between.width,
                      color='white',
                      edgecolors='black',
                      zorder=1,alpha=0.6)
# England player nodes
eng_nodes = pitch.scatter(avg_eng_locs.x,avg_eng_locs.y,
                      s=400,
                      color='white',
                      edgecolors='red',
                      linewidth=1.5,
                      alpha=1,
                      zorder=1,
                      ax=ax['pitch'][0])
# Plot England player squad numbers
for index, row in avg_eng_locs.iterrows():
    pitch.annotate(row.squad_no,xy=(row.x,row.y),ax=ax['pitch'][0],va='center',ha='center',weight='bold',size=10)
    
# Germany pass lines
ger_lines = pitch.lines(ger_pass_between.x,ger_pass_between.y,
                      ger_pass_between.x_end,ger_pass_between.y_end,
                      ax=ax['pitch'][1],
                      lw = ger_pass_between.width,
                      color='white',
                      edgecolors='black',
                      zorder=1,alpha=0.6)
# Germany player nodes
ger_nodes = pitch.scatter(avg_ger_locs.x,avg_ger_locs.y,
                      s=400,
                      color='white',
                      edgecolors='black',
                      linewidth=1.5,
                      alpha=1,
                      zorder=1,
                      ax=ax['pitch'][1])
# Plot Germany player squad numbers
for index, row in avg_ger_locs.iterrows():
    pitch.annotate(row.squad_no,xy=(row.x,row.y),ax=ax['pitch'][1],va='center',ha='center',weight='bold',size=10)

# Set title
TITLE = 'Euro 2022 Final: Pass Networks'
title = ax['title'].text(0.5,0.9,TITLE,ha='center',va='center',fontsize=19,color='white',weight='bold')

# Squad key
eng_text = ax['title'].text(0.125,-0.22,'1: Mary Earps\n2: Lucy Bronze\n3: Rachel Daly\n4: Keira Walsh\n6: Millie Bright\n7: Beth Mead',color='white')
eng_text2 = ax['title'].text(0.275,-0.115,'8: Leah Williamson\n9: Ellen White\n10: Georgia Stanway\n11: Lauren Hemp\n14: Fran Kirby',color='white')
ger_text = ax['title'].text(0.68,-0.3,'1: Merle Frohms\n3: Kathrin Hendrich\n5: Marina Hegering\n6: Lena Oberdorf\n7: Lea Schüller\n9: Svenja Huth',color='white')
ger_text2 = ax['title'].text(0.84,-0.195,'13: Sara Däbritz\n15: Giulia Gwinn\n17: Felicitas Rauch\n20: Lina Magull\n22: Jule Brand',color='white')
pitch.annotate('@datawithed', xy=(116,32),ax=ax['pitch'][0],color='white')
pitch.annotate('@datawithed', xy=(116,32),ax=ax['pitch'][1],color='white')
end_test = ax['endnote'].text(0,0.4,'Data: StatsBomb',color='white',weight='bold')
eng_valid = ax['endnote'].text(0,0.9,f"Pass network for starting XI up to: {eng_first_sub_min}'",color='white',weight='bold')
ger_valid = ax['endnote'].text(0.54,0.9,f"Pass network for starting XI up to: {ger_first_sub_min}'",color='white',weight='bold')
eng_logo = add_image(eng_badge, fig=fig, left=ax['title'].get_position().x0, bottom=0.8,height=0.1)
ger_logo = eng_logo = add_image(ger_badge, fig=fig, left=0.54, bottom=0.79,height=0.12)

# Save the figure
plt.savefig('Euro 2022 Pass Network - Final.png')













