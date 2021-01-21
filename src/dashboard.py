import streamlit as st
import pandas as pd
import altair as alt
import base64
from io import BytesIO
from analysis import *

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="extract.xlsx">Download xlsx file</a>' # decode b'abc' => abc

st.title("BpG Gene Based Pricing Panel Overlap Analysis")
st.write("Analysis to identify cases where one panel is a perfect subset of another based on genes, and where there is overlap in size category.")
st.write("""* **Perfect Subset** - when *all* of a panel's genes are contained in a bigger panel.
* **Overlap** - when a panel and its perfect subset both fall into the same panel size category (small, medium, large).""")

# Instantiate the sidebar
uploaded_file = st.sidebar.file_uploader('Choose an xlsx file', type='xlsx')
# sliders
small_slider = st.sidebar.slider('Select Max Number of Genes for Small Category', value=20)
medium_slider = st.sidebar.slider('Select Max Number of Genes for Medium Category', value=125, min_value=100, max_value=400)
# Radio button to select volume
vol_radio = st.sidebar.radio('Select which Payor volume to analyze:', ['US Institutional Clients', 'US Third Party', 'Both'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    # map in a column with sizes of panels based on slider selections
    df_with_sizes = df.copy()
    df_with_sizes['Panel_Size'] = df_with_sizes['num_genes_whitepaper'].apply(sizes, args=(small_slider, medium_slider))

    graph_obj = create_graph(df)
    # total output file
    output_df = run_analysis(graph_obj, df, vol_radio, small_slider, medium_slider)
    # overlap only file
    overlap_df = output_df.loc[output_df['overlap'] == 'yes']
    # ---------------------------------------------------------------------
    # Display outputs

    # Display Graphs
    

    # Create Scatter showing relationship of parent - child volume
    top_bar = alt.Chart(overlap_df).mark_bar().encode(
        x=alt.X('count(parent)', stack='normalize', axis=None, sort=['parent nla greater than child', 'parent and child nla equal', 'parent nla less than child']),
        color=alt.Color('nla_variance', scale=alt.Scale(scheme='greys')),
        order=alt.Order('nla_variance', sort='ascending')
    ).properties(width=600, height=75)
    text = alt.Chart(overlap_df).mark_text(dx=-15, dy=0, color='white').encode(
        x=alt.X('count(parent):Q', stack='normalize', axis=None, sort=['parent nla greater than child', 'parent and child nla equal', 'parent nla less than child']),
        detail='nla_variance:N',
        text=alt.Text('count(parent):Q', format='.0f'),
        order=alt.Order('nla_variance', sort='ascending')
    )
    top_chart = top_bar + text

    scatter = alt.Chart(overlap_df).mark_point(size=70, filled=True).encode(
        alt.X('child_volume', title='Volume of Child'),
        alt.Y('parent_volume', title='Volume of Parent'),
        color=alt.Color('parent_size', legend=alt.Legend(title='Panel Size')),
        shape=alt.Shape('parent or child contains 81479'),
        tooltip=['parent:N', 'parent_name:N', 'parent_genes:N', 'parent_nla:N', 'parent_cpt:N', 'child:N', 'child_name:N', 'child_genes:N', 'child_nla:N', 'child_cpt:N'],
        column=alt.Row('nla_variance')
    ).properties(width=200, height=300).interactive()
    st.header(f"Volume Relationships of {len(output_df.loc[output_df['overlap'] == 'yes'])} Panels with Perfect Subsets and Overlap")
    st.write(top_chart)
    st.write(scatter)

    # Visualize total panels by size
    total_panels = df[['node', 'num_genes']].copy()
    # add size categories
    total_panels['panel_size'] = total_panels['num_genes'].apply(sizes, args=(small_slider, medium_slider))
    # create chart
    panel_bars = alt.Chart(total_panels).mark_bar().encode(
        alt.X('panel_size:N', title='Panel Size', sort=['single', 'small', 'medium', 'large']),
        alt.Y('count(panel_size):Q', title='Count')
    )
    panel_text = panel_bars.mark_text(
        align='center',
        baseline='middle',
        dy=-4  # Nudges text to right so it doesn't appear on top of the bar
    ).encode(
        text='count(panel_size):Q'
    )

    panel_chart = (panel_bars + panel_text).properties(width=500, height=300)
    st.header('Number of Panels in Each Bucket')
    st.write(panel_chart)

    # Horizontal Summary Chart
    # first create data
    d = {
        'Total Cases of Perfect Subsets':len(output_df),
        'Cases of Overlap':len(output_df.loc[output_df['overlap'] == 'yes'])
    }

    summary_df = pd.DataFrame().from_dict(d, orient='index', columns=['count']).reset_index()

    # then visualize it
    summary_bars = alt.Chart(summary_df).mark_bar().encode(
        x=alt.X('count:Q', axis=None),
        y=alt.Y('index:N')
    )

    summary_text = summary_bars.mark_text(
        align='left',
        baseline='middle',
        dx = -25
    ).encode(
        text='sum(count):Q'
    )

    summary_chart = (summary_bars + summary_text).properties(width=500, height=100)
    st.header('Summary Stats')
    st.write(summary_chart)

    # Vertical Overlap Bar Chart
    bars = alt.Chart(overlap_df).mark_bar().encode(
        alt.X('parent_size:N', title='Panel Size', sort=alt.EncodingSortField(field="parent_size", order='descending')),
        alt.Y('count(parent_size):Q', title='Count of Overlap'), 
    )
    text = bars.mark_text(
        align='center',
        baseline='middle',
        dy=-8  # Nudges text up so it doesn't appear on top of the bar
    ).encode(
        text='count(parent_size):Q'
    )
    # combine bars with text and adjust size
    chart = (bars + text).properties(width=500, height=300)
    # display in dashboard
    st.header('Count of Overlap by Panel Size')
    st.write(chart)
    
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
