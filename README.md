# graph-algo-streamlit
Graph Algorithm and Visualization to Identify Perfect Subsets

## The Problem Statement
The target was to create a pricing structure where genetic lab tests were categorized into buckets based on the number of genes that the tests contain. 
For example:
* 1-2 genes is a small panel, with a price of $10
* 3-5 genes is a medium panel, with a price of $15
* 5+ genes is a large panel, with a price of $20

The issue is that you can have a genetic test _PANEL1_ with genes [A, B, C], and a second test _PANEL2_ with genes [A, B, C, D]. Both of these would be considered a medium panel according to the above construct because they each contain 3-5 genes, so they would both be pried at $15 for the ordering physician.

In healthcare when a physician performs a service, they submit a claim to be reimbursed by insurance. The reimbursement is set based on the service performed. So you can have a scenario where _PANEL1_ is reimbursed at $30, while _PANEL2_ is reimbursed at $50.

This makes our strategy problematic because you can have cases where a patient needs to have genes [A, B, C], tested. A savvy physician knows that he needs to order _PANEL1_, which costs him $15 and then he would get reimbursed $30 by the insurance company; OR instead he can order _PANEL2_, which tests an additional gene that he doesn't care about but costs him the same, and get him reimbursed $50 (an additional $20, on top of the reimbursement for _PANEL1_).

We needed to determine what is the scope of the above issue for the entire portfolio of genetic tests before we could move forward on this strategy.

## The Challenge
* I needed to compare each test to every other test in the portfolio of 230 test, each containing anywhere from 1-650 genes, and identify all the parent-child relationships
    * e.g. _PANEL2_ with genes [A, B, C, D] is the parent and _PANEL1_ with genes [A, B, C] is the child 
* Categorize each test as a small, medium, or large panel
* Identify cases of overlap where both the parent and the child are in the same size category
* Hone in on overlap cases where the parent is reimbursed higher by insurance than the child
* Communicate the results in a way that all involved parties can understand (both technical and non-technical) 

## The Solution
I created a `GraphNode` class to capture the demographics info of each test including the test code, number of genes it contains, which genes it contains, and which other tests are children (or perfect subsets) of that test.

The `create_graph()` function creates a graph using a `dictionary` object to compare the genes in each panel to every other panel and determine which panels are children of which others.
