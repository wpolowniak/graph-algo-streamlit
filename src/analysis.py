import pandas as pd

class GraphNode:
    def __init__(self, num_genes, genes_set, test_code):
        self.num_genes = num_genes
        self.genes = genes_set
        self.test_code = test_code
        self.children = []
        
    def __repr__(self):
        return f'{self.test_code} Node'
    
    def __str__(self):
        out_str = f"""
        test_code : {self.test_code}
        num_genes : {self.num_genes}
        genes : {self.genes}
        children : {self.children}"""
        return out_str

# define function to return the key of a dictionary from its value
def get_key(val, my_dict): 
    for key, value in my_dict.items(): 
         if val == value: 
            return key

# define function to map in the sizes of panels from streamlit sidebar
def sizes(value: int, small_slider: int, medium_slider: int) -> str:
    if value == 1:
        return 'single'
    elif value <= small_slider: # max of the range. i.e if 25, then small is from 2 - 25 genes inclusive
        return 'small'
    elif value <= medium_slider: # max of the range. i.e. if 250, then medium is from whatever small is + 1 to 250, inclusive
        return 'medium'
    else:
        return 'large'

def create_graph(genes_df: pd.DataFrame) -> dict:
    root = None
    gene_list = []
    name_dict = {}

    for _, row in genes_df.iterrows():
        # create a name_dict dictionary with structure: {'test_name':[List, Of, All, Genes]} 
        current_genes = set(row['genes'].split())
        name_dict[row['node']] = current_genes

        # add the set of genes for the current row to gene_list, for later sorting
        # also identify root 
        if row['node'] == 'root':
            root = current_genes
        else:
            gene_list.append(current_genes)
    
    # Sort the data from largest to smallest value
    gene_list.sort(key=len, reverse=True)

    # instantiate the graph
    graph = {'root': GraphNode(len(root), root, 'root')}

    # cycle through all genes in gene_list to populate graph
    for genes in gene_list:
        name_of_test = get_key(genes, name_dict)
        num_genes = len(genes)
    
        # add children to node of parent if perfect subset
        for key in graph:
            if genes.issubset(graph[key].genes):
                graph[key].children.append(name_of_test)

        # add node to the graph
        graph[name_of_test] = GraphNode(num_genes, genes, name_of_test)

    return graph

def run_analysis(graph, genes_df: pd.DataFrame, small_slider: int, medium_slider: int) -> pd.DataFrame:
    """This function takes a graph as an input and returns the required analysis
    """
    # Create dict of panels with children (perfect subsets)
    non_empty_dict = {}
    for key, value in graph.items():

        if (value.children) and (key != 'root'):
            non_empty_dict[key] = value.children

    # create df out of non_empty_dict
    parent_child_df = (
        pd.DataFrame()
        .from_dict(non_empty_dict, orient='index')
        .stack()
        .reset_index()
        .drop(columns=['level_1'])
        .rename(columns={'level_0':'parent',0:'child'})
    )
 
    # merge all required data from genes_df into the final output
    final_df = (
        parent_child_df
        # merge in test name of parent
        .merge(genes_df[['node', 'name']], how='left', left_on='parent', right_on='node')
        .drop(columns=['node'])
        .rename(columns={'name':'parent_name'})
        # merge in test name of child
        .merge(genes_df[['node', 'name']], how='left', left_on='child', right_on='node')
        .drop(columns=['node'])
        .rename(columns={'name':'child_name'})
        # merge in number of genes for parent
        .merge(genes_df[['node', 'num_genes']], how='left', left_on='parent', right_on='node')
        .drop(columns=['node'])
        .rename(columns={'num_genes':'parent_genes'})
        # merge in number of genes for child
        .merge(genes_df[['node', 'num_genes']], how='left', left_on='child', right_on='node')
        .drop(columns=['node'])
        .rename(columns={'num_genes':'child_genes'})
        # merge in volume of parent
        .merge(genes_df[['node', 'volume']], how='left', left_on='parent', right_on='node')
        .drop(columns=['node'])
        .rename(columns={'volume':'parent_volume'})
        # merge in volume of child
        .merge(genes_df[['node', 'volume']], how='left', left_on='child', right_on='node')
        .drop(columns=['node'])
        .rename(columns={'volume':'child_volume'})
        # merge in NLA of parent
        .merge(genes_df[['node', 'nla']], how='left', left_on='parent', right_on='node')
        .drop(columns=['node'])
        .rename(columns={'nla':'parent_nla'})
        # merge in NLA of child
        .merge(genes_df[['node', 'nla']], how='left', left_on='child', right_on='node')
        .drop(columns=['node'])
        .rename(columns={'nla':'child_nla'})
    )

    # map in the sizes of panels
    final_df['parent_size'] = final_df['parent_genes'].apply(sizes, args=(small_slider, medium_slider))
    final_df['child_size'] = final_df['child_genes'].apply(sizes, args=(small_slider, medium_slider))

    # Identify panels that have overlap
    final_df['overlap'] = ''
    final_df.loc[final_df['parent_size'] == final_df['child_size'], 'overlap'] = 'yes'

    # flag where parent NLA is greater than child NLA
    final_df['nla_variance'] = ''
    final_df.loc[final_df['parent_nla'] == final_df['child_nla'], 'nla_variance'] = 'parent and child nla equal'
    final_df.loc[final_df['parent_nla'] > final_df['child_nla'], 'nla_variance'] = 'parent nla greater than child'
    final_df.loc[final_df['parent_nla'] < final_df['child_nla'], 'nla_variance'] = 'parent nla less than child'

    return final_df