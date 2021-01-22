# graph-algo-streamlit
Graph Algorithm and Visualization to Identify Perfect Subsets

## The Problem Statement
The goal of this exercise was to create a pricing structure for genetic lab tests, categorizing the tests into buckets based on the number of genes in each panel. 
As an illustrative example:
* 1-2 genes is a small panel, with a price of $10
* 3-5 genes is a medium panel, with a price of $15
* 5+ genes is a large panel, with a price of $20

At a high level this strategy works, but there is a potential issue. You can have a genetic test, _PANEL1_, with genes [A, B, C], and a second test, _PANEL2_, with genes [A, B, C, D]. Both of these would be considered a medium panel according to the above construct because they each contain 3-5 genes, so they would both be priced at $15 for the ordering physician.

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

See it in action at https://share.streamlit.io/wpolowniak/graph-algo-streamlit/main/src/dashboard.py