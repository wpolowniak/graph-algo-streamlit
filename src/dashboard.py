import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from analysis import *
from visualizations import *
from pathlib import Path

def to_excel(df: pd.DataFrame):
    output = BytesIO()
    writer = pd.ExcelWriter(output)
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df: pd.DataFrame):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="extract.xlsx">Download xlsx file</a>' # decode b'abc' => abc

st.title("Gene Based Pricing Panel Overlap Analysis")
st.write("Analysis to identify cases where one panel is a perfect subset of another based on genes, and where there is overlap in size category.")
st.write("""* **Perfect Subset** - when *all* of a panel's genes are contained in a bigger panel.
* **Overlap** - when a panel and its perfect subset both fall into the same panel size category (small, medium, large).""")

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
