import pandas as pd
from datetime import datetime
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st
import io
import msoffcrypto
import numpy as np
import re
import time
import colorsys

pd.set_option('future.no_silent_downcasting', True)
pd.set_option('display.max_columns', None)
st.set_page_config(
	layout="wide",
	initial_sidebar_state="expanded"
)

st.markdown("""
<style>
	/* Adjust the position of the markdown text container */
	.reportview-container .markdown-text-container {
		position: relative;
		top: -20px;  /* Adjust this value to move the title up */
	}
	/* Adjust header styling to remove space and lines */
	h1 {
		margin-top: -50px !important;  /* Decrease the space above the title */
		border-bottom: none !important;  /* Ensures no line is under the title */
	}
	/* Hide any horizontal rules that might be appearing */
	hr {
		display: none !important;
	}
	/* Reduce padding on the left and right sides of the main block container */
	.reportview-container .main .block-container{
		padding-left: -20px;
		padding-right: 10px;
	}
</style>
""", unsafe_allow_html=True)

# Hide Streamlit style and buttons
hide_st_style = '''
	<style>
	#MainMenu {visibility: hidden;}
	footer {visibility: hidden;}
	header {visibility: hidden;}
	</style>
'''
st.markdown(hide_st_style, unsafe_allow_html=True)


# Load file function
@st.cache_data
def loadcgmap():
	# Loading data from excel file
	df = pd.read_excel("cgmap.xlsx", sheet_name="Sheet1")
	return df


# Function to determine text position
def determine_text_position(x_value):
    if x_value == intersection_selling_price:
        return "top left"
    elif x_value < midpoint:
        return "middle left"
    else:
        return "middle right"

def split_data_by_zero(x, y):
    segments = []
    current_segment = {'x': [], 'y': [], 'above': y[0] >= 0}
    
    for xi, yi in zip(x, y):
        if (yi >= 0) == current_segment['above']:
            current_segment['x'].append(xi)
            current_segment['y'].append(yi)
        else:
            segments.append(current_segment)
            current_segment = {'x': [xi], 'y': [yi], 'above': yi >= 0}
    
    segments.append(current_segment)
    return segments



title_placeholder = st.empty()
# slider_placeholder = st.sidebar.empty()
# plot_placeholder = st.empty()

#main grogram begins
df = loadcgmap()

# Get unique years from the 'Property Purchase FY' column
years = df['Property Purchase FY'].unique()

# Create a dropdown menu
selected_year = st.sidebar.selectbox('Select a Year of Purchase:', years)

# Create a numeric input for purchase price
purchase_price = st.sidebar.number_input('Enter Purchase Price in Rs Lakhs:', 
                                 min_value=0.0, 
                                 value=100.0, 
                                 step=1.0, 
                                 format="%.2f")

# Get the applicable cost index for the selected year
cost_index = df[df["Property Purchase FY"] == selected_year]["Applicable Cost Index"].iloc[0].round(2)

indexed_puchased_cost = round(purchase_price * cost_index,2)

# Create a numeric input for selling price increment steps
selling_price_increment_steps = st.sidebar.number_input('Enter Selling Price Increments Steps in Rs Lakhs:', 
                                 min_value=1.0, 
                                 value=1.0, 
                                 step=1.0, 
                                 format="%.2f")

#Create a numeric input for selling price
selling_price = st.sidebar.number_input('Enter Selling Price in Rs Lakhs:', 
                                 min_value=purchase_price, 
                                 value=float(purchase_price*2), 
                                 step=selling_price_increment_steps, 
                                 format="%.2f")

tax_gain_with_indexation = round(((selling_price - purchase_price)*0.125)-(selling_price - indexed_puchased_cost)*0.2,2)

# Generate range of selling prices from the purchase price to the selected selling price
selling_prices = np.arange(purchase_price, selling_price+1, 1.0)

# Calculate profits with and without indexation for each selling price
cgtax_with_indexation = (selling_prices - indexed_puchased_cost)*0.2
cgtax_without_indexation = (selling_prices - purchase_price)*0.125

#Difference between cgtax_with_indexation & cgtax_without_indexation

tax_gains_with_indexation = cgtax_without_indexation - cgtax_with_indexation


# Find intersection point
intersection_idx = np.argmin(np.abs(cgtax_with_indexation - cgtax_without_indexation))
intersection_selling_price = selling_prices[intersection_idx]

midpoint = selling_prices[len(selling_prices) // 2]

# Create a scatter plot
fig = go.Figure()
# fig.add_trace(go.Scatter(x=selling_prices, y=cgtax_with_indexation, mode='lines+markers', name='CapitalGain Tax With Indexation', line=dict(color='blue')))
# fig.add_trace(go.Scatter(x=selling_prices, y=cgtax_without_indexation, mode='lines+markers', name='CapitalGain Tax Without Indexation', line=dict(color='red')))
# fig.add_trace(go.Scatter(x=selling_prices, y=tax_gains_with_indexation, mode='lines+markers', name='Savings With Indexation', line=dict(color='green')))

# Create a scatter plot with text annotations at points of interest
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=selling_prices, y=cgtax_with_indexation, mode='lines+markers+text', name='Capital Gain Tax With Indexation',
    line=dict(color='blue'),
    text=[f"{y:.1f} L" if x in [selling_prices[0], selling_prices[-1], intersection_selling_price] else "" for x, y in zip(selling_prices, cgtax_with_indexation)],
    textposition=[determine_text_position(x) for x in selling_prices],
    textfont=dict(size=16, color='blue', family='Arial, bold')
))
fig.add_trace(go.Scatter(
    x=selling_prices, y=cgtax_without_indexation, mode='lines+markers+text', name='Capital Gain Tax Without Indexation',
    line=dict(color='brown'),
    text=[f"{y:.1f} L" if x in [selling_prices[0], selling_prices[-1], intersection_selling_price] else "" for x, y in zip(selling_prices, cgtax_without_indexation)],
    textposition=[determine_text_position(x) for x in selling_prices],
    textfont=dict(size=16, color='brown', family='Arial, bold')
))
# fig.add_trace(go.Scatter(
#     x=selling_prices, y=tax_gains_with_indexation, mode='lines+markers+text', name='Savings With Indexation',
#     line=dict(color='green'),
#     text=[f"{y:.1f} L" if x in [selling_prices[0], selling_prices[-1], intersection_selling_price] else "" for x, y in zip(selling_prices, tax_gains_with_indexation)],
#     textposition=[determine_text_position(x) for x in selling_prices],
#     textfont=dict(size=16, color='green', family='Arial, bold')
# ))

# Plotting each segment with appropriate text annotations
for segment in split_data_by_zero(selling_prices, tax_gains_with_indexation):
    color = 'green' if segment['above'] else 'red'
    text = [f"{y:.1f} L" if i in [0, len(segment['y']) - 1] else "" for i, y in enumerate(segment['y'])]  # Text only at the start and end of each segment

    fig.add_trace(go.Scatter(
        x=segment['x'],
        y=segment['y'],
        mode='lines+markers+text',
        name='Savings With Indexation',
        line=dict(color=color),
        text=text,
        textposition="top center",
        textfont=dict(size=16, color=color, family='Arial, bold')  # Ensure font size and color match the line color
    ))



# Add a vertical line at the intersection point
fig.add_vline(x=intersection_selling_price, line_width=2, line_dash="dash", line_color="black")

# Add a horizontal line at the x axis
fig.add_hline(y=0.0, line_width=2, line_dash="dash", line_color="black")


# # Add annotations
# annotations = [
#     # Start and end annotations for 'With Indexation'
#     dict(x=selling_prices[0], y=cgtax_with_indexation[0], xanchor='left', yanchor='bottom', text='Start', showarrow=True, arrowhead=1, ax=-40, ay=0),
#     dict(x=selling_prices[-1], y=cgtax_with_indexation[-1], xanchor='right', yanchor='top', text='End', showarrow=True, arrowhead=1, ax=40, ay=0),
#     # Start and end annotations for 'Without Indexation'
#     dict(x=selling_prices[0], y=cgtax_without_indexation[0], xanchor='left', yanchor='bottom', text='Start', showarrow=True, arrowhead=1, ax=-40, ay=0),
#     dict(x=selling_prices[-1], y=cgtax_without_indexation[-1], xanchor='right', yanchor='top', text='End', showarrow=True, arrowhead=1, ax=40, ay=0),
#     # Intersection annotation
#     dict(x=intersection_selling_price, y=cgtax_with_indexation[intersection_idx], xanchor='center', yanchor='middle', text='Intersection', showarrow=True, arrowhead=1, ax=0, ay=-40),
# ]

def color():
	if tax_gain_with_indexation >0:
		color = 'green'
	if tax_gain_with_indexation <0:
		color = 'red'
	if tax_gain_with_indexation == 0:
		color = 'black'
	return color

#color index for savings
color = color()

title = f"Capital Gain Tax For Property (Indexation vs NonIndexation)<span style='color:violet;'> - Purchase Year {selected_year}\
</span> - Purchase Price <span style='color:violet;'> Rs {purchase_price} Lakhs</span>\
</span> - Selling Price <span style='color:violet;'> Rs {selling_price} Lakhs</span>\
</span> - Savings with Indexation <span style='color:{color};'> Rs {tax_gain_with_indexation} Lakhs</span>"


# # Title with HTML for automatic line breaks
# title_text = f"Capital Gain Tax Analysis for Property (Indexation vs Non-Indexation) <br>Purchase Year: {selected_year}, Purchase Price: Rs {purchase_price} Lakhs, Selling Price: Rs {selling_price} Lakhs"


# Custom CSS for adjusting title appearance
title_css = """
<style>
    h1 {
        text-align: left; /* Left align the title */
        margin-top: 0px; /* Adjust top margin to reduce gap */
        margin-bottom: 5px; /* Add a bit of margin below the title if needed */
        border-bottom: none !important; /* Ensures no line is under the title */
        font-size: 20px; /* Adjust font size to smaller size */
    }
</style>
"""

# Display the title with custom styling
st.markdown(title_css, unsafe_allow_html=True)
title_placeholder.markdown(f"<h1>{title}</h1>", unsafe_allow_html=True)


# Update layout for the plot, including custom legend positioning
fig.update_layout(
    # title={
    #     'text': title_text,
    #     'y': 1.0,
    #     'x': 0.5,
    #     'xanchor': 'center',
    #     'yanchor': 'top',
    #     'font': dict(
    #         family="Arial",
    #         size=20,  # Double the default size which is generally around 20
    #         color="black"
    #     )
    # },
    xaxis_title='Selling Price (Rs Lakhs)',
    yaxis_title='Capital Gain Tax (Rs Lakhs)',
    legend_title='Profit Type',
    # annotations=annotations,
    legend=dict(
        orientation="h",
        x=0.5,
        y=-0.3,
        xanchor='center',
        yanchor='bottom'
    ),
    height=700, width=1200, margin=dict(l=0, r=0, t=0, b=0, pad=0)
)

 #Update the layout for the combined figure for 1
fig.update_xaxes(tickfont=dict(size=15), fixedrange=True, showline=True, linewidth=1.5, linecolor='grey', mirror=True, showgrid=True, gridcolor='lightgrey')
fig.update_yaxes(tickfont=dict(size=15),fixedrange=True, showline=True, linewidth=1.5, linecolor='grey', mirror=True, showgrid=True, gridcolor='lightgrey')


# Display the plot
st.plotly_chart(fig, use_container_width=True)


