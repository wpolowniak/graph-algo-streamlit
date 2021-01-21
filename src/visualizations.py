import altair as alt
from analysis import sizes
from pandas import DataFrame

def perfect_subset_overlap_summary(df: DataFrame) -> alt.Chart:
    """Summarize the count of instances of parent/child overlap by NLA (parent greater, equal, child greater)
    """
    top_bar = alt.Chart(df).mark_bar().encode(
        x=alt.X('count(parent)', stack='normalize', axis=None, sort=['parent nla greater than child', 'parent and child nla equal', 'parent nla less than child']),
        color=alt.Color('nla_variance', scale=alt.Scale(scheme='greys')),
        order=alt.Order('nla_variance', sort='ascending')
    ).properties(width=600, height=75)
    text = alt.Chart(df).mark_text(dx=-15, dy=0, color='white').encode(
        x=alt.X('count(parent):Q', stack='normalize', axis=None, sort=['parent nla greater than child', 'parent and child nla equal', 'parent nla less than child']),
        detail='nla_variance:N',
        text=alt.Text('count(parent):Q', format='.0f'),
        order=alt.Order('nla_variance', sort='ascending')
    )
    top_chart = top_bar + text

    return top_chart

def parent_child_overlap_scatter(df: DataFrame) -> alt.Chart:
    """Create a scatter plot showing the relationship of parent -> child volume for overlap
    """
    scatter = alt.Chart(df).mark_point(size=70, filled=True).encode(
        alt.X('child_volume', title='Volume of Child'),
        alt.Y('parent_volume', title='Volume of Parent'),
        color=alt.Color('parent_size', legend=alt.Legend(title='Panel Size')),
        shape=alt.Shape('parent or child contains 81479'),
        tooltip=['parent:N', 'parent_name:N', 'parent_genes:N', 'parent_nla:N', 'parent_cpt:N', 'child:N', 'child_name:N', 'child_genes:N', 'child_nla:N', 'child_cpt:N'],
        column=alt.Row('nla_variance')
    ).properties(width=200, height=300).interactive()

    return scatter

def total_panels_by_size_bar(df: DataFrame, small_slider: int, medium_slider: int) -> alt.Chart:
    """Visualize total panels by size
    """
    # take only relevant information
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

    return panel_chart

def perfect_subset_summary_stats(df: DataFrame) -> alt.Chart:
    """Horizontal bar chart summarizing how many total cases of overlap in perfect subset vs how many 
    total cases of perfect subsets
    """
    # first create data
    d = {
        'Total Cases of Perfect Subsets':len(df),
        'Cases of Overlap':len(df.loc[df['overlap'] == 'yes'])
    }
    # make it into a dataframe
    summary_df = DataFrame().from_dict(d, orient='index', columns=['count']).reset_index()

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

    return summary_chart

def count_of_overlap_by_panel_size(df: DataFrame) -> alt.Chart:
    """Vertical bar chart showing count of overlap by panel size
    """
    # Vertical Overlap Bar Chart
    bars = alt.Chart(df).mark_bar().encode(
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
    return chart

