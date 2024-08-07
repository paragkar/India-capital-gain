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




df = loadcgmap()

st.write(df)

# Get unique years from the 'Property Purchase FY' column
years = df['Property Purchase FY'].unique()

# Create a dropdown menu
selected_year = st.sidebar.selectbox('Select a Year of Purchase:', years)

# Display the selected year (you can replace this with other functionality based on the selection)
st.write(f'You selected: {selected_year}')

# Create a numeric input for purchase price
purchase_price = st.sidebar.number_input('Enter Purchase Price in Rs Lakhs:', 
                                 min_value=0.0, 
                                 value=0.0, 
                                 step=1.0, 
                                 format="%.2f")

# Display the entered purchase price
st.write(f'Purchase Price: Rs {purchase_price} Lakhs')

idx = df[df["Property Purchase FY"] == selected_year].index

cost_index = df.loc[idx, "Applicable Cost Index"]

st.write(cost_index)

