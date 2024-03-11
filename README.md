# 🪽 Exploring Stork Migration Patterns with DBN Analysis
---
*Jana Nikolovska* <br/>
*Master’s Degree in Artificial Intelligence, University of Bologna*
<br/> 📧: jana.nikolovska@studio.unibo.it
<br/> 👤: [Linkedin profile](https://mk.linkedin.com/in/jana-nikolovska-813156181)

The aim of this study is to develop a Dynamic Bayesian
Network (DBN) to understand the migration patterns of
the white stork, leveraging climate and vegetation indicators to uncover the underlying relationships. The
model is constructed using the pgmpy library in Python,
fitting it with time-series data gathered from various
sources after integration and preprocessing. The fundamental concepts are explored, including Markov blanket, Independence, Sampling, and Inference within the
context of the DBN, along with calculated Conditional
Probability Distributions (CPDs) and Discretized Factors

**InitialDataExploration.ipynb** - Exploring the dataset obtained by MoveBank 'Eastern flyway spring migration of adult white storks (data from Rotics et al. 2018).csv'.
* Load full dataset, describe dataset, feature selection based on relevance, transform columns

**gather_data.py** - Enrich the dataset with NDVI indicator calculated by using Google Earth API and climate indicators calculated using Open-Meteo API

**Preprocess_data.ipynb** - Analyse and transform the, now, enriched dataset, transforming it into an input for pgmpy's Dynamic Bayesian Network

**Build_analyse_DBN.ipynb** - Build the Dynamic Bayesian Network, compute CPDs, Discretized factors, Markov blanket, Independencies, Inference, Sampling

**utils\utils.py** - helper functions for gather_data.py

**data\Labels_dictionary_for discretization.txt** - dictionary explaining the categories after discretization of the features

---
For more information about the project read **REPORT.pdf**
