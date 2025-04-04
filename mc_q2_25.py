# =================================== IMPORTS ================================= #
import csv, sqlite3
import numpy as np 
import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt 
import plotly.figure_factory as ff
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from folium.plugins import MousePosition
import plotly.express as px
import datetime
import folium
import os
import sys
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.development.base_component import Component
# 'data/~$bmhc_data_2024_cleaned.xlsx'
# print('System Version:', sys.version)
# -------------------------------------- DATA ------------------------------------------- #

current_dir = os.getcwd()
current_file = os.path.basename(__file__)
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = 'data/MarCom_Responses.xlsx'
file_path = os.path.join(script_dir, data_path)
data = pd.read_excel(file_path)
df = data.copy()

# Trim leading and trailing whitespaces from column names
df.columns = df.columns.str.strip()

# Define a discrete color sequence
color_sequence = px.colors.qualitative.Plotly

# Filtered df where 'Date of Activity:' is between Ocotber to December:
df['Date of Activity'] = pd.to_datetime(df['Date of Activity:'], errors='coerce')
df = df[(df['Date of Activity:'] >= '2024-10-01') & (df['Date of Activity:'] <= '2024-12-31')]
df['Month'] = df['Date of Activity'].dt.month_name()

df_oct = df[df['Month'] == 'October']
df_nov = df[df['Month'] == 'November']
df_dec = df[df['Month'] == 'December']

# print(df_m.head())
# print('Total Marketing Events: ', len(df))
# print('Column Names: \n', df.columns)
# print('DF Shape:', df.shape)
# print('Dtypes: \n', df.dtypes)
# print('Info:', df.info())
# print("Amount of duplicate rows:", df.duplicated().sum())

# print('Current Directory:', current_dir)
# print('Script Directory:', script_dir)
# print('Path to data:',file_path)

# ================================= Columns ================================= #

# Column Names: 
#  Index([
#        'Timestamp',
#        'Which MarCom activity category are you submitting an entry for?',
#        'Person completing this form:', 
#        'Activity duration:',
#        'Purpose of the activity (please only list one):',
#        'Please select the type of product(s):',
#        'Please provide public information:', 
#        'Please explain event-oriented:',
#        'Date of Activity:', 
#        'Brief activity description:', 
#        'Activity Status'],
#  dtype='object')

# =============================== Missing Values ============================ #

# missing = df.isnull().sum()
# print('Columns with missing values before fillna: \n', missing[missing > 0])

#  Please provide public information:    137
# Please explain event-oriented:        13

# ============================== Data Preprocessing ========================== #

# Check for duplicate columns
# duplicate_columns = df.columns[df.columns.duplicated()].tolist()
# print(f"Duplicate columns found: {duplicate_columns}")
# if duplicate_columns:
#     print(f"Duplicate columns found: {duplicate_columns}")

# Rename columns
df.rename(columns={"Which MarCom activity category are you submitting an entry for?": "MarCom Activity"}, inplace=True)

# Rename Purpose of the activity (please only list one): to Purpose
df.rename(columns={"Purpose of the activity (please only list one):": "Purpose"}, inplace=True)

# Rename 'Please select the type of product(s):' to 'Product Type'
df.rename(columns={"Please select the type of product(s):": "Product Type"}, inplace=True)

# Rename 'Please select the type of product(s):' to 'Product Type'
df.rename(columns={"Activity duration (hours):": "Activity duration"}, inplace=True)

# Fill Missing Values
df['Please provide public information:'] = df['Please provide public information:'].fillna('N/A')
df['Please explain event-oriented:'] = df['Please explain event-oriented:'].fillna('N/A')

# print(df.dtypes)

# ------------------------------- MarCom Events DF ---------------------------------- #

marcom_events = len(df)

# --------------------------------- MarCom Hours DF --------------------------------- #

# Remove the word 'hours' from the 'Activity duration:' column
df['Activity duration'] = df['Activity duration'].str.replace(' hours', '')
df['Activity duration'] = df['Activity duration'].str.replace(' hour', '')
df['Activity duration'] = pd.to_numeric(df['Activity duration'], errors='coerce')

marcom_hours = df.groupby('Activity duration').size().reset_index(name='Count')
marcom_hours = df['Activity duration'].sum()
# print('Total Activity Duration:', sum_activity_duration, 'hours')

# Calculate total hours for each month
hours_oct = df[df['Month'] == 'October']['Activity duration'].sum()
hours_oct = round(hours_oct) 
hours_nov = df[df['Month'] == 'November']['Activity duration'].sum()
hours_nov = round(hours_nov)
hours_dec = df[df['Month'] == 'December']['Activity duration'].sum()
hours_dec = round(hours_dec)

# Create df for MarCom Hours
df_hours = pd.DataFrame({
    'Month': ['October', 'November', 'December'],
    'Hours': [hours_oct, hours_nov, hours_dec]
})

# Bar chart for MarCom Hours
hours_fig = px.bar(
    df_hours,
    x='Month',
    y='Hours',
    color="Month",
    text='Hours',
    title='Q1 MarCom Hours by Month',
    labels={
        'Hours': 'Number of Hours',
        'Month': 'Month'
    },
).update_layout(
    title_x=0.5,
    xaxis_title='Month',
    yaxis_title='Hours',
    height=900,  # Adjust graph height
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    ),
    xaxis=dict(
        tickfont=dict(size=18),  # Adjust font size for the month labels
        tickangle=-25,  # Rotate x-axis labels for better readability
        title=dict(
            text=None,
            font=dict(size=20),  # Font size for the title
        ),
    ),
    yaxis=dict(
        title=dict(
            text='Number of Hours',
            font=dict(size=22),  # Font size for the title
        ),
    ),
    bargap=0.08,  # Reduce the space between bars
).update_traces(
    texttemplate='%{text}',  # Display the count value above bars
    textfont=dict(size=20),  # Increase text size in each bar
    textposition='auto',  # Automatically position text above bars
    textangle=0, # Ensure text labels are horizontal
    hovertemplate=(  # Custom hover template
        '<b>Hours</b>: %{y}<extra></extra>'  
    ),
).add_annotation(
    x='October',  # Specify the x-axis value
    y=df_hours.loc[df_hours['Month'] == 'October', 'Hours'].values[0] + 100,  # Position slightly above the bar
    text='No data',  # Annotation text
    showarrow=False,  # Hide the arrow
    font=dict(size=30, color='red'),  # Customize font size and color
    align='center',  # Center-align the text
)

# Pie Chart MarCom Hours
hours_pie = px.pie(
    df_hours,
    names='Month',
    values='Hours',
    color='Month',
    height=800
).update_layout(
    title=dict(
        x=0.5,
        text='Q1 MarCom Hours by Month',  # Title text
        font=dict(
            size=35,  # Increase this value to make the title bigger
            family='Calibri',  # Optional: specify font family
            color='black'  # Optional: specify font color
        ),
    )  # Center-align the title
).update_traces(
    rotation=0,  # Rotate pie chart 90 degrees counterclockwise
    textfont=dict(size=19),  # Increase text size in each bar
    textinfo='value+percent',
    texttemplate='<br>%{percent:.0%}',  # Format percentage as whole numbers
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# ------------------------------ MarCom Activity DF ------------------------------- #

# Extracting "MarCom Activity" and "Date of activity:"
df_activities = df[['MarCom Activity', 'Date of Activity:']]
# print(df_activities.head())

# Ensure "Date of activity:" is in datetime format
df_activities['Date of activity:'] = pd.to_datetime(df_activities['Date of Activity:'], errors='coerce')

# Extract the month from the "Date of activity:" column
df_activities['Month'] = df_activities['Date of Activity:'].dt.month_name()

# Filter data for October, November, and December
df_activities_q = df_activities[df_activities['Month'].isin(['October', 'November', 'December'])]

# Group the data by "Month" and "MarCom Activity" to count occurrences
df_activity_counts = (
    df_activities_q.groupby(['Month', 'MarCom Activity'], sort=True)
    .size()
    .reset_index(name='Count')
)

# Sort months in the desired order
month_order = ['October', 'November', 'December']
df_activity_counts['Month'] = pd.Categorical(
    df_activity_counts['Month'],
    categories=month_order,
    ordered=True
)

df_activity_counts = df_activity_counts.sort_values(by=['Month', 'MarCom Activity'])


# Create a grouped bar chart
activity_fig = px.bar(
    df_activity_counts,
    x='Month',
    y='Count',
    color='MarCom Activity',
    barmode='group',
    text='Count',
    title='MarCom Activities by Month',
    labels={
        'Count': 'Number of Activities',
        'Month': 'Month',
        'MarCom Activity': 'Activity Category'
    },
).update_layout(
    title_x=0.5,
    xaxis_title='Month',
    yaxis_title='Count',
    height=900,  # Adjust graph height
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    ),
    xaxis=dict(
        tickmode='array',
        tickvals=df_activity_counts['Month'].unique(),
        tickangle=-35  # Rotate x-axis labels for better readability
    ),
    legend=dict(
        title='Activity Category',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        xanchor="left",  # Anchor legend to the left
        y=1,  # Position legend at the top
        yanchor="top"  # Anchor legend at the top
    ),
    hovermode='x unified',  # Unified hover display
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='auto',  # Place count values outside bars
        textfont=dict(size=30),  # Increase text size in each bar
    hovertemplate=(
         '<br>'
        '<b>Count: </b>%{y}<br>'  # Count
    ),
    customdata=df_activity_counts['MarCom Activity'].values.tolist()  # Custom data for hover display
).add_vline(
    x=0.5,  # Adjust the position of the line
    line_dash="dash",
    line_color="gray",
    line_width=2
).add_vline(
    x=1.5,  # Position of the second line
    line_dash="dash",
    line_color="gray",
    line_width=2
)

# Group by "MarCom Activity" to count occurrences
df_mc_activity = df_activities.groupby('MarCom Activity').size().reset_index(name='Count')

# Bar chart for  Totals:
activity_totals_fig = px.bar(
    df_mc_activity,
    x='MarCom Activity',
    y='Count',
    color='MarCom Activity',
    text='Count',
).update_layout(
    height=850,  # Adjust graph height
    title=dict(
        x=0.5,
        text='Total Q1 MarCom Activities',  # Title text
        font=dict(
            size=35,  # Increase this value to make the title bigger
            family='Calibri',  # Optional: specify font family
            color='black'  # Optional: specify font color
        )
    ),
    xaxis=dict(
        tickfont=dict(size=18),  # Adjust font size for the month labels
        tickangle=-25,  # Rotate x-axis labels for better readability
        title=dict(
            text=None,
            font=dict(size=20),  # Font size for the title
        ),
    ),
    yaxis=dict(
        title=dict(
            text='Number of Activities',
            font=dict(size=22),  # Font size for the title
        ),
    ),
    bargap=0.08,  # Reduce the space between bars
).update_traces(
    texttemplate='%{text}',  # Display the count value above bars
    textfont=dict(size=20),  # Increase text size in each bar
    textposition='auto',  # Automatically position text above bars
    textangle=0, # Ensure text labels are horizontal
    hovertemplate=(  # Custom hover template
        '<b>Activity</b>: %{label}<br><b>Count</b>: %{y}<extra></extra>'  
    ),
)

#  Pie chart:
activity_pie = px.pie(
    df_mc_activity,
    names='MarCom Activity',
    values='Count',
    color='MarCom Activity',
    height=800
).update_layout(
    title=dict(
        x=0.5,
        text='Q1 MarCom Activities',  # Title text
        font=dict(
            size=35,  # Increase this value to make the title bigger
            family='Calibri',  # Optional: specify font family
            color='black'  # Optional: specify font color
        ),
    )  # Center-align the title
).update_traces(
    rotation=0,  # Rotate pie chart 90 degrees counterclockwise
    textfont=dict(size=19),  # Increase text size in each bar
    textinfo='value+percent',
    texttemplate='%{value}<br>%{percent:.0%}',  # Format percentage as whole numbers
    insidetextorientation='horizontal',  # Horizontal text orientation
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# ---------------------------- MarCom Person Completing DF ------------------------ #

# Extracting "Person completing this form:" and "Date of activity:"
df_person = df[['Person completing this form:', 'Date of Activity:']]

# Create a dictionary for replacements
replacements_person = {
    'Felicia Chanlder': 'Felicia Chandler',
    'Felicia Banks': 'Felicia Chandler'
}

# Remove leading and trailing whitespaces and perform the replacements
df_person['Person completing this form:'] = (
    df_person['Person completing this form:']
    .str.strip()
    .replace(replacements_person)
)

# Ensure "Date of activity:" is in datetime format
df_person['Date of activity:'] = pd.to_datetime(df_person['Date of Activity:'], errors='coerce')

# Extract the month from the "Date of activity:" column
df_person['Month'] = df_person['Date of Activity:'].dt.month_name()

# Filter data for October, November, and December
df_person_q = df_person[df_person['Month'].isin(['October', 'November', 'December'])]

# Group the data by "Month" and "Person completing this form:" to count occurrences
df_person_counts = (
    df_person_q.groupby(['Month', 'Person completing this form:'], 
    sort=True) # Sort the values
    .size()
    .reset_index(name='Count')
)

# Sort months in the desired order
month_order = ['October', 'November', 'December']
df_person_counts['Month'] = pd.Categorical(
    df_person_counts['Month'],
    categories=month_order,
    ordered=True
)

# Sort df
df_person_counts = df_person_counts.sort_values(by=['Month', 'Person completing this form:'])

# Create a grouped bar chart
person_fig = px.bar(
    df_person_counts,
    x='Month',
    y='Count',
    color='Person completing this form:',
    barmode='group',
    text='Count',
    title='Forms Completed by Month',
    labels={
        'Count': 'Number of Forms',
        'Month': 'Month',
        'Person completing this form:': 'Person'
    },
).update_layout(
    title_x=0.5,
    xaxis_title='Month',
    yaxis_title='Count',
    height=900,  # Adjust graph height
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    ),
    xaxis=dict(
        tickmode='array',
        tickvals=df_person_counts['Month'].unique(),
        tickangle=-35  # Rotate x-axis labels for better readability
    ),
    legend=dict(
        title='Person',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        xanchor="left",  # Anchor legend to the left
        y=1,  # Position legend at the top
        yanchor="top"  # Anchor legend at the top
    ),
    hovermode='x unified',  # Unified hover display
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='auto',  # Place count values outside bars
    textfont=dict(size=30),  # Increase text size in each bar
    hovertemplate=(
        '<br>'
        '<b>Count: </b>%{y}<br>'  # Count
    ),
    customdata=df_person_counts['Person completing this form:'].values.tolist()  # Custom data for hover display
).add_vline(
    x=0.5,  # Adjust the position of the line
    line_dash="dash",
    line_color="gray",
    line_width=2
).add_vline(
    x=1.5,  # Position of the second line
    line_dash="dash",
    line_color="gray",
    line_width=2
)

df_pf = df[['Person completing this form:', 'Date of Activity:']]

# Create a dictionary for replacements
replacements_person1 = {
    'Felicia Chanlder': 'Felicia Chandler',
    'Felicia Banks': 'Felicia Chandler'
}

# Remove leading and trailing whitespaces and perform the replacements
df_pf['Person completing this form:'] = (
    df_pf['Person completing this form:']
    .str.strip()
    .replace(replacements_person1)
)

# Group the data by "Person completing this form:" to count occurrences
df_pf = df_pf.groupby('Person completing this form:').size().reset_index(name="Count")

# Bar chart for  Totals:
person_totals_fig = px.bar(
    df_pf,
    x='Person completing this form:',
    y='Count',
    color='Person completing this form:',
    text='Count',
).update_layout(
    height=850,  # Adjust graph height
    title=dict(
        x=0.5,
        text='Total Q1 Form Submissions by Person',  # Title text
        font=dict(
            size=35,  # Increase this value to make the title bigger
            family='Calibri',  # Optional: specify font family
            color='black'  # Optional: specify font color
        )
    ),
    xaxis=dict(
        tickfont=dict(size=18),  # Adjust font size for the month labels
        tickangle=-25,  # Rotate x-axis labels for better readability
        title=dict(
            text=None,
            font=dict(size=20),  # Font size for the title
        ),
    ),
    yaxis=dict(
        title=dict(
            text='Number of Submissions',
            font=dict(size=22),  # Font size for the title
        ),
    ),
    bargap=0.08,  # Reduce the space between bars
).update_traces(
    texttemplate='%{text}',  # Display the count value above bars
    textfont=dict(size=20),  # Increase text size in each bar
    textposition='auto',  # Automatically position text above bars
    textangle=0, # Ensure text labels are horizontal
    hovertemplate=(  # Custom hover template
        '<b>Name</b>: %{label}<br><b>Count</b>: %{y}<extra></extra>'  
    ),
)

pf_pie = px.pie(
    df_pf,
    names='Person completing this form:',
    values='Count',
    color='Person completing this form:',
    height=800
).update_layout(
    title=dict(
        x=0.5,
        text='Q1 People Completing Forms',  # Title text
        font=dict(
            size=35,  # Increase this value to make the title bigger
            family='Calibri',  # Optional: specify font family
            color='black'  # Optional: specify font color
        ),
    ),  # Center-align the title
    margin=dict(
        t=150,  # Adjust the top margin (increase to add more padding)
        l=20,   # Optional: left margin
        r=20,   # Optional: right margin
        b=20    # Optional: bottom margin
    )
).update_traces(
    rotation=0,  # Rotate pie chart 90 degrees counterclockwise
    textfont=dict(size=19),  # Increase text size in each bar
    textinfo='value+percent',
    insidetextorientation='horizontal',  # Horizontal text orientation
    texttemplate='%{value}<br>%{percent:.0%}',  # Format percentage as whole numbers
    hovertemplate='<b>%{label}</b>: %{value}<extra></extra>'
)

# ---------------------------- MarCom Activity Status DF -------------------------- #

# "Activity Status" dataframe:
df_activity_status = df.groupby('Activity Status').size().reset_index(name='Count')

status_fig = px.pie(
        df_activity_status,
        values='Count',
        names='Activity Status',
        color='Activity Status',
    ).update_layout(
        title='Q1 MarCom Activity Status',
        title_x=0.5,
        height=500,
        font=dict(
            family='Calibri',
            size=17,
            color='black'
        )
    ).update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent',
         texttemplate='%{value}<br>%{percent:.0%}',  # Format percentage as whole numbers
        hole=0.2
    )

# # ========================== MarCom DataFrame Table ========================== #

# MarCom Table
marcom_table = go.Figure(data=[go.Table(
    # columnwidth=[50, 50, 50],  # Adjust the width of the columns
    header=dict(
        values=list(df.columns),
        fill_color='paleturquoise',
        align='center',
        height=30,  # Adjust the height of the header cells
        # line=dict(color='black', width=1),  # Add border to header cells
        font=dict(size=12)  # Adjust font size
    ),
    cells=dict(
        values=[df[col] for col in df.columns],
        fill_color='lavender',
        align='left',
        height=25,  # Adjust the height of the cells
        # line=dict(color='black', width=1),  # Add border to cells
        font=dict(size=12)  # Adjust font size
    )
)])

marcom_table.update_layout(
    margin=dict(l=50, r=50, t=30, b=40),  # Remove margins
    height=400,
    # width=1500,  # Set a smaller width to make columns thinner
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)'  # Transparent plot area
)

# ------------------------------- MarCom Products Table ----------------------------#

df_product_type = df.groupby('Product Type').size().reset_index(name='Count')

# Products Table
products_table = go.Figure(data=[go.Table(
    # columnwidth=[50, 50, 50],  # Adjust the width of the columns
    header=dict(
        values=list(df_product_type.columns),
        fill_color='paleturquoise',
        align='center',
        height=30,  # Adjust the height of the header cells
        # line=dict(color='black', width=1),  # Add border to header cells
        font=dict(size=12)  # Adjust font size
    ),
    cells=dict(
        values=[df_product_type[col] for col in df_product_type.columns],
        fill_color='lavender',
        align='left',
        height=25,  # Adjust the height of the cells
        # line=dict(color='black', width=1),  # Add border to cells
        font=dict(size=12)  # Adjust font size
    )
)])

products_table.update_layout(
    margin=dict(l=50, r=50, t=30, b=40),  # Remove margins
    height=900,
    # width=1500,  # Set a smaller width to make columns thinner
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)'  # Transparent plot area
)

# ----------------------------- MarCom Purpose Table ----------------------------#

df_purpose = df.groupby('Purpose').size().reset_index(name='Count')

purpose_table = go.Figure(data=[go.Table(
    # columnwidth=[50, 50, 50],  # Adjust the width of the columns
    header=dict(
        values=list(df_purpose.columns),
        fill_color='paleturquoise',
        align='center',
        height=30,  # Adjust the height of the header cells
        # line=dict(color='black', width=1),  # Add border to header cells
        font=dict(size=12)  # Adjust font size
    ),
    cells=dict(
        values=[df_purpose[col] for col in df_purpose.columns],
        fill_color='lavender',
        align='left',
        height=25,  # Adjust the height of the cells
        # line=dict(color='black', width=1),  # Add border to cells
        font=dict(size=12)  # Adjust font size
    )
)])

purpose_table.update_layout(
    margin=dict(l=50, r=50, t=30, b=40),  # Remove margins
    height=900,
    # width=1500,  # Set a smaller width to make columns thinner
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)'  # Transparent plot area
)

# ============================== Dash Application ========================== #

app = dash.Dash(__name__)
server= app.server

app.layout = html.Div(
    children=[ 
    html.Div(
        className='divv', 
        children=[ 
        html.H1(
            'BMHC MarCom Report Q1 2025', 
            className='title'),
        html.H2(
            '10/01/2024 - 12/31/2024', 
            className='title2'),
        html.Div(
            className='btn-box', 
            children=[
                html.A(
                'Repo',
                href='https://github.com/CxLos/MC_Q1_2025',
                className='btn'),
            ]),
    ]),    

# Data Table
# html.Div(
#     className='row0',
#     children=[
#         html.Div(
#             className='table',
#             children=[
#                 html.H1(
#                     className='table-title',
#                     children='Data Table'
#                 )
#             ]
#         ),
#         html.Div(
#             className='table2', 
#             children=[
#                 dcc.Graph(
#                     className='data',
#                     figure=marcom_table
#                 )
#             ]
#         )
#     ]
# ),

# ROW 1
html.Div(
    className='row0',
    children=[
        html.Div(
            className='graph11',
            children=[
            html.Div(
                className='high1',
                children=['MarCom Events:']
            ),
            html.Div(
                className='circle1',
                children=[
                    html.Div(
                        className='hilite',
                        children=[
                            html.H1(
                            className='high3',
                            children=[marcom_events]
                    ),
                        ]
                    )
 
                ],
            ),
            ]
        ),
        html.Div(
            className='graph22',
            children=[
            html.Div(
                className='high2',
                children=['Total MarCom Hours Q1:']
            ),
            html.Div(
                className='circle2',
                children=[
                    html.Div(
                        className='hilite',
                        children=[
                            html.H1(
                            className='high4',
                            children=[marcom_hours]
                    ),
                        ]
                    )
 
                ],
            ),
            ]
        ),
    ]
),

# ROW 
html.Div(
    className='row3',
    children=[
        html.Div(
            className='graph0',
            children=[
                dcc.Graph(
                    figure=hours_fig
                )
            ]
        )
    ]
),

# ROW 
html.Div(
    className='row3',
    children=[
        html.Div(
            className='graph0',
            children=[
                dcc.Graph(
                    figure=hours_pie
                )
            ]
        )
    ]
),

# ROW 
html.Div(
    className='row3',
    children=[
        html.Div(
            className='graph0',
            children=[
                dcc.Graph(
                    figure=activity_fig
                )
            ]
        )
    ]
),

# ROW 
html.Div(
    className='row3',
    children=[
        html.Div(
            className='graph0',
            children=[
                dcc.Graph(
                    figure=activity_totals_fig
                )
            ]
        )
    ]
),
# ROW 
html.Div(
    className='row3',
    children=[
        html.Div(
            className='graph0',
            children=[
                dcc.Graph(
                    figure=activity_pie
                )
            ]
        )
    ]
),

# ROW 
html.Div(
    className='row3',
    children=[
        html.Div(
            className='graph0',
            children=[
                dcc.Graph(
                    figure=person_fig
                )
            ]
        )
    ]
),
# ROW 
html.Div(
    className='row3',
    children=[
        html.Div(
            className='graph0',
            children=[
                dcc.Graph(
                    figure=person_totals_fig
                )
            ]
        )
    ]
),
# ROW 
html.Div(
    className='row3',
    children=[
        html.Div(
            className='graph0',
            children=[
                dcc.Graph(
                    figure=pf_pie
                )
            ]
        )
    ]
),

# ROW 2
html.Div(
    className='row1',
    children=[
        html.Div(
            className='graph1',
            children=[
                html.Div(
                    className='table',
                    children=[
                        html.H1(
                            className='table-title',
                            children='Products Table'
                        )
                    ]
                ),
                html.Div(
                    className='table2', 
                    children=[
                        dcc.Graph(
                            className='data',
                            figure=products_table
                        )
                    ]
                )
            ]
        ),
        html.Div(
            className='graph2',
            children=[                
              html.Div(
                    className='table',
                    children=[
                        html.H1(
                            className='table-title',
                            children='Purpose Table'
                        )
                    ]
                ),
                html.Div(
                    className='table2', 
                    children=[
                        dcc.Graph(
                            className='data',
                            figure=purpose_table
                        )
                    ]
                )
   
            ]
        )
    ]
),

# ROW 4
html.Div(
    className='row1',
    children=[
        html.Div(
            className='graph1',
            children=[
                # 'Activity Status' pie chart
                dcc.Graph(
                  figure = status_fig
                )
            ]
        ),
        html.Div(
            className='graph2',
            children=[                
                dcc.Graph(
                    style={'height': '800px', 'width': '800px'}  # Set height and width
                )
            ]
        )
    ]
),
])

print(f"Serving Flask app '{current_file}'! 🚀")

if __name__ == '__main__':
    app.run_server(debug=True)
                #    False)
# =================================== Updated Database ================================= #

# updated_path = 'data/bmhc_q4_2024_cleaned.xlsx'
# data_path = os.path.join(script_dir, updated_path)
# df.to_excel(data_path, index=False)
# print(f"DataFrame saved to {data_path}")

# updated_path1 = 'data/service_tracker_q4_2024_cleaned.csv'
# data_path1 = os.path.join(script_dir, updated_path1)
# df.to_csv(data_path1, index=False)
# print(f"DataFrame saved to {data_path1}")

# -------------------------------------------- KILL PORT ---------------------------------------------------

# netstat -ano | findstr :8050
# taskkill /PID 24772 /F
# npx kill-port 8050

# ---------------------------------------------- Host Application -------------------------------------------

# 1. pip freeze > requirements.txt
# 2. add this to procfile: 'web: gunicorn impact_11_2024:server'
# 3. heroku login
# 4. heroku create
# 5. git push heroku main

# Create venv 
# virtualenv venv 
# source venv/bin/activate # uses the virtualenv

# Update PIP Setup Tools:
# pip install --upgrade pip setuptools

# Install all dependencies in the requirements file:
# pip install -r requirements.txt

# Check dependency tree:
# pipdeptree
# pip show package-name

# Remove
# pypiwin32
# pywin32
# jupytercore

# ----------------------------------------------------

# Name must start with a letter, end with a letter or digit and can only contain lowercase letters, digits, and dashes.

# Heroku Setup:
# heroku login
# heroku create mc-impact-11-2024
# heroku git:remote -a mc-impact-11-2024
# git push heroku main

# Clear Heroku Cache:
# heroku plugins:install heroku-repo
# heroku repo:purge_cache -a mc-impact-11-2024

# Set buildpack for heroku
# heroku buildpacks:set heroku/python

# Heatmap Colorscale colors -----------------------------------------------------------------------------

#   ['aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance',
            #  'blackbody', 'bluered', 'blues', 'blugrn', 'bluyl', 'brbg',
            #  'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 'cividis', 'curl',
            #  'darkmint', 'deep', 'delta', 'dense', 'earth', 'edge', 'electric',
            #  'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens', 'greys',
            #  'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno', 'jet',
            #  'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges',
            #  'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl',
            #  'piyg', 'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn',
            #  'puor', 'purd', 'purp', 'purples', 'purpor', 'rainbow', 'rdbu',
            #  'rdgy', 'rdpu', 'rdylbu', 'rdylgn', 'redor', 'reds', 'solar',
            #  'spectral', 'speed', 'sunset', 'sunsetdark', 'teal', 'tealgrn',
            #  'tealrose', 'tempo', 'temps', 'thermal', 'tropic', 'turbid',
            #  'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu', 'ylorbr',
            #  'ylorrd'].

# rm -rf ~$bmhc_data_2024_cleaned.xlsx
# rm -rf ~$bmhc_data_2024.xlsx
# rm -rf ~$bmhc_q4_2024_cleaned2.xlsx