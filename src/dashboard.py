import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from analysis import *
from visualizations import *
from pathlib import Path

def to_excel(df: pd.DataFrame):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df: pd.DataFrame):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = df.to_csv(index=False)
    b64 = base64.b64encode(val.encode())  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="extract.csv">Download csv file</a>' # decode b'abc' => abc

st.title("Gene Based Pricing Panel Overlap Analysis")
st.write("""
## The Problem Statement
The goal of this exercise was to create a pricing structure for genetic lab tests, categorizing the tests into buckets based on the number of genes in each panel. 
As an illustrative example:
* 1-2 genes is a small panel, with a price of $10
* 3-5 genes is a medium panel, with a price of $15
* 5+ genes is a large panel, with a price of $20

At a high level this strategy works, but there is a potential issue. You can have a genetic test, _PANEL1_, with genes [A, B, C], and a second test, _PANEL2_, with genes [A, B, C, D]. Both of these would be considered a medium panel according to the above construct because they each contain 3-5 genes, so they would both be pried at $15 for the ordering physician.

In healthcare when a physician performs a service, they submit a claim to be reimbursed by insurance. The reimbursement is determined based on the service performed. So you can have a scenario where _PANEL1_ is reimbursed at $30, while _PANEL2_ is reimbursed at $50.

This makes our strategy problematic because it can potentially incentivize over ordering of medically unnecessary tests in order for the physician to get a higher reimbursement from insurance. To illustrate, consider a patient that is determined to need a genetic test on genes [A, B, C]. A savvy physician knows that he needs to order _PANEL1_, which costs him $15, for which he would get reimbursed $30 by the insurance company; OR instead he can order _PANEL2_, which tests an additional gene that he doesn't care about but costs him the same, and get reimbursed $50 by insurance (an additional $20, on top of the reimbursement for _PANEL1_).

We needed to determine what is the scope of this issue for the entire portfolio of genetic tests before we could move forward with this strategy.

## The Challenge
* I needed to compare each test to every other test in the portfolio of 230 test, each containing anywhere from 1-650 genes, and identify all the parent-child relationships.
    * e.g. _PANEL2_ with genes [A, B, C, D] is the parent and _PANEL1_ with genes [A, B, C] is the child 
* Categorize each test as a small, medium, or large panel
* Identify cases of overlap where both the parent and the child are in the same size category
* Hone in on overlap cases where the parent is reimbursed higher by insurance than the child
* Communicate the results in a way that all involved parties can understand (both technical and non-technical) 

## The Solution
I created a `GraphNode` class using a `dictionary` data structure to map which panels have a parent-child relationship, by checking if the set of genes in a panel is a subset of another panel. I then identified the size category of each panel and found where both parent and child fall in the same category. 

To communicate the data I built a dashboad using `streamlit` to visualize the results, and also to allow for an interactive discovery process to determine what panel size cutoffs are optimal to minimize the cases of parent-child overlap.

## Directions
Use the sliders to the left to select the cutoffs for small, medium and large panels. 
i.e. if the max number of genes in the small category is 20, and the max number of genes for medium category is 125 then:
* small is 1-20 genes
* medium is 21-125 genes
* large is 126+ genes
""")
# st.write("Analysis to identify cases where one panel is a perfect subset of another based on genes, and where there is overlap in size category.")
# st.write("""* **Perfect Subset** - when *all* of a panel's genes are contained in a bigger panel.
# * **Overlap** - when a panel and its perfect subset both fall into the same panel size category (small, medium, large).""")

# Instantiate the sidebar
uploaded_file = st.sidebar.file_uploader('Choose an xlsx file, otherwise using example data.', type='xlsx')
# sliders
small_slider = st.sidebar.slider('Select Max Number of Genes for Small Category', value=20)
medium_slider = st.sidebar.slider('Select Max Number of Genes for Medium Category', value=125, min_value=100, max_value=400)

# can uplodad your own data to analyze, if not use default data
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    loc = Path.cwd() / 'data' / 'default_data.csv'
    df = pd.read_csv(loc)


# Add num_genes
df['num_genes'] = df['genes'].str.split().apply(lambda x: len(x))

# map in a column with sizes of panels based on slider selections
df_with_sizes = df.copy()
df_with_sizes['Panel_Size'] = df_with_sizes['num_genes'].apply(sizes, args=(small_slider, medium_slider))

graph_obj = create_graph(df)
# total output file
output_df = run_analysis(graph_obj, df, small_slider, medium_slider)
# overlap only file
overlap_df = output_df.loc[output_df['overlap'] == 'yes']
# ---------------------------------------------------------------------
# Display outputs

# Display Graphs
st.header(f"Volume Relationships of {len(output_df.loc[output_df['overlap'] == 'yes'])} Panels with Perfect Subsets and Overlap")
st.write(perfect_subset_overlap_summary(overlap_df))
st.write(parent_child_overlap_scatter(overlap_df))
st.write("""
The medium graph shows the problematic instances that could potentially incentivize physicians. 

Using this visualization we can determine how widespread of an issue this is based on the selected category sizes.

Looking at the volume of the parent and child, we can determine whether we want to discontinue offering one of those tests in order to be able to go forward with this strategy.
""")

# Visualize total panels by size
st.header('Number of Panels in Each Bucket')
st.write(total_panels_by_size_bar(df, small_slider, medium_slider))

# Horizontal Summary Chart
st.header('Summary Stats')
st.write(perfect_subset_summary_stats(output_df))

# Vertical Overlap Bar Chart
st.header('Count of Overlap by Panel Size')
st.write(count_of_overlap_by_panel_size(overlap_df))

# Display Output files - Full output
st.header('Outputs')
st.write('Full Output of Perfect Subsets')
output_df
# To download an xlsx file (also need above two functions)
if 'output_df' in locals():  
    st.markdown(get_table_download_link(output_df), unsafe_allow_html=True)

# Overlap file only
st.write('Overlap Only')
overlap_df
# To download an xlsx file (also need above two functions)
if 'overlap_df' in locals():  
    st.markdown(get_table_download_link(overlap_df), unsafe_allow_html=True)

# Original input file, with sizes mapped in
st.write('Original file, with sizes mapped in')
df_with_sizes
# To download an xlsx file (also need above two functions)
if 'df_with_sizes' in locals():  
    st.markdown(get_table_download_link(df_with_sizes), unsafe_allow_html=True)
