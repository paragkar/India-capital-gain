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


#main grogram begins
df = loadcgmap()

# Get unique years from the 'Property Purchase FY' column
years = df['Property Purchase FY'].unique()

# Create a dropdown menu
selected_year = st.sidebar.selectbox('Select a Year of Purchase:', years)

# Create a numeric input for purchase price
purchase_price = st.sidebar.number_input('Enter Purchase Price in Rs Lakhs:', 
                                 min_value=0.0, 
                                 value=0.0, 
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
                                 value=purchase_price, 
                                 step=selling_price_increment_steps, 
                                 format="%.2f")


# Generate range of selling prices from the purchase price to the selected selling price
selling_prices = np.arange(purchase_price, selling_price + 1, 1.0)

# Calculate profits with and without indexation for each selling price
cgtax_with_indexation = (selling_prices - indexed_puchased_cost)*0.2
cgtax_without_indexation = (selling_prices - purchase_price)*0.125

#Difference between cgtax_with_indexation & cgtax_without_indexation

tax_gains_with_indexation = cgtax_without_indexation - cgtax_with_indexation


# Find intersection point
intersection_idx = np.argmin(np.abs(cgtax_with_indexation - cgtax_without_indexation))
intersection_selling_price = selling_prices[intersection_idx]

# Create a scatter plot
fig = go.Figure()
fig.add_trace(go.Scatter(x=selling_prices, y=cgtax_with_indexation, mode='lines+markers', name='CapitalGain Tax With Indexation', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=selling_prices, y=cgtax_without_indexation, mode='lines+markers', name='CapitalGain Tax Without Indexation', line=dict(color='red')))
fig.add_trace(go.Scatter(x=selling_prices, y=tax_gains_with_indexation, mode='lines+markers', name='CapitalGain Tax Gains With Indexation', line=dict(color='green')))

# Add a vertical line at the intersection point
fig.add_vline(x=intersection_selling_price, line_width=2, line_dash="dash", line_color="black")

# Add a horizontal line at the x axis
fig.add_hline(y=0.0, line_width=2, line_dash="dash", line_color="black")


# Set plot layout
fig.update_layout(title='Capital Gain Tax Analysis', xaxis_title='Selling Price (Rs Lakhs)', yaxis_title='Capital Gain Tax (Rs Lakhs)', legend_title='Profit Type')

fig.update_layout(height=700, width=1200, margin=dict(l=0, r=10, t=30, b=0, pad=0))

# Display the plot
st.plotly_chart(fig)

# Display the selected year (you can replace this with other functionality based on the selection)
st.write(f'You selected: {selected_year}')

# Display the entered purchase price
st.write(f'Purchase Price: Rs {purchase_price} Lakhs')

# Display the entered selling price
st.write(f'Selling Price: Rs {selling_price} Lakhs')

# Display taxes payable
st.write(f'Tax Payable with Indexation: Rs {round(cgtax_with_indexation[-1],2)} Lakhs')
st.write(f'Tax Payable without Indexation: Rs {round(cgtax_without_indexation[-1],2)} Lakhs')

