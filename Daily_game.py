import pandas as pd
import os
import urllib.request
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import panel as pn
import nfl_data_py as nfl
from IPython.display import Image, display

pn.extension('tabulator', css_files=["https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css"])

#Retreived the data from the website but I've stored it in a csv so this code is not needed. I'm not deleting it though, just in case
#html_url = "https://www.fantasypros.com/nfl/reports/leaders/ppr.php?year=2023"
#ppr_2023 = pd.read_html(html_url)[0]
#ppr_2023.to_csv('fantasypros_ppr_2023.csv', index=False)

ppr_2023 = pd.read_csv('fantasypros_ppr_2023.csv')
ppr_2023.head()

positions = ppr_2023.Pos.unique()

qb_ppr_2023 = ppr_2023.query('Pos == "QB"')
rb_ppr_2023 = ppr_2023.query('Pos == "RB"')
wr_ppr_2023 = ppr_2023.query('Pos == "WR"')
te_ppr_2023 = ppr_2023.query('Pos == "TE"')
k_ppr_2023 = ppr_2023.query('Pos == "K"')
dst_ppr_2023 = ppr_2023.query('Pos == "DST"')

qb_ppr_2023 = qb_ppr_2023.reset_index(drop=True)
rb_ppr_2023 = rb_ppr_2023.reset_index(drop=True)
wr_ppr_2023 = wr_ppr_2023.reset_index(drop=True)
te_ppr_2023 = te_ppr_2023.reset_index(drop=True)
k_ppr_2023 = k_ppr_2023.reset_index(drop=True)
dst_ppr_2023 = dst_ppr_2023.reset_index(drop=True)


qb_ppr_2023 = qb_ppr_2023.replace(['-', 'BYE'], 0)
rb_ppr_2023 = rb_ppr_2023.replace(['-', 'BYE'], 0)
wr_ppr_2023 = wr_ppr_2023.replace(['-', 'BYE'], 0)
te_ppr_2023 = te_ppr_2023.replace(['-', 'BYE'], 0)
k_ppr_2023 = k_ppr_2023.replace(['-', 'BYE'], 0)
dst_ppr_2023 = dst_ppr_2023.replace(['-', 'BYE'], 0)

'''
qb_ppr_2023['1'] = qb_ppr_2023['1'].astype(float)
rb_ppr_2023['1'] = rb_ppr_2023['1'].astype(float)
wr_ppr_2023['1'] = wr_ppr_2023['1'].astype(float)
te_ppr_2023['1'] = te_ppr_2023['1'].astype(float)
k_ppr_2023['1'] = k_ppr_2023['1'].astype(float)
dst_ppr_2023['1'] = dst_ppr_2023['1'].astype(float)
'''

dataframes = [qb_ppr_2023, rb_ppr_2023, wr_ppr_2023, te_ppr_2023, k_ppr_2023, dst_ppr_2023]

for df in dataframes:
    for col in df.columns:
        if col.isdigit() and int(col) >= 1 and int(col) <= 18:
            df[col] = df[col].astype(float)
            
index_dict = {}
for df in [qb_ppr_2023, rb_ppr_2023, wr_ppr_2023, te_ppr_2023, k_ppr_2023, dst_ppr_2023]:
    for col in range(1, 19):
        col_name = str(col)
        if col_name not in index_dict:
            index_dict[col_name] = []
        top_3_indices = df[col_name].nlargest(3).index
        index_dict[col_name].extend(top_3_indices)

index_dict_players = {}
for df in [qb_ppr_2023, rb_ppr_2023, wr_ppr_2023, te_ppr_2023, k_ppr_2023, dst_ppr_2023]:
    for col in range(1, 19):
        col_name = str(col)
        if col_name not in index_dict_players:
            index_dict_players[col_name] = []
        top_3_indices = df[col_name].nlargest(3).index
        top_3_players = df.loc[top_3_indices, 'Player'].tolist()
        index_dict_players[col_name].extend(top_3_players)

# Assuming you have the index_dict and dataframes available from the previous code

# Create a dropdown widget for selecting the column number
column_dropdown = pn.widgets.IntSlider(name='Select Week', start=1, end=18, value=1)

# Define a function to update the displayed information based on the selected column
def update_info(column_number):
    selected_info = {}
    for position, df in zip(['QB', 'RB', 'WR', 'TE', 'K', 'DST'], [qb_ppr_2023, rb_ppr_2023, wr_ppr_2023, te_ppr_2023, k_ppr_2023, dst_ppr_2023]):
        selected_player = index_dict[str(column_number)]
        selected_info[position] = df.loc[df['Player'].isin(selected_player), ['Player', 'Pos', 'Team', str(column_number)]]

    return pn.pane.DataFrame(selected_info['QB'], width=300), pn.pane.DataFrame(selected_info['RB'], width=300), pn.pane.DataFrame(selected_info['WR'], width=300), pn.pane.DataFrame(selected_info['TE'], width=300), pn.pane.DataFrame(selected_info['K'], width=300), pn.pane.DataFrame(selected_info['DST'], width=300)

# Create a function to update the displayed information when the dropdown value changes
def on_column_change(event):
    qb_pane, rb_pane, wr_pane, te_pane, k_pane, dst_pane = update_info(event.obj.value)
    app[1][0] = qb_pane
    app[1][1] = rb_pane
    app[1][2] = wr_pane
    app[1][3] = te_pane
    app[1][4] = k_pane
    app[1][5] = dst_pane

# Create the initial display based on the default value of the dropdown
qb_pane, rb_pane, wr_pane, te_pane, k_pane, dst_pane = update_info(column_dropdown.value)

# Create the app layout
app = pn.Column(
    column_dropdown,
    pn.FlexBox(qb_pane, rb_pane, wr_pane, te_pane, k_pane, dst_pane)
)

# Attach the event handler to the dropdown widget
column_dropdown.param.watch(on_column_change, 'value')

# Display the app
app.servable()
