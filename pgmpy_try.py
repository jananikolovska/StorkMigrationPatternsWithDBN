from pgmpy.models import BayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import os
num_bins = 5

# Load your aggregated data
data = pd.read_csv(os.path.join('data','GrouppedByData.csv'))
if 'Unnamed: 0' in data.columns:
    data = data.drop(['Unnamed: 0'],axis=1)
print(data.shape)
print(data.columns)
data = data.dropna()
data = data.rename(columns={'tag-local-identifier': 'Stork-Id',
                            'timestamp': 'Timestamp',
                            'NDVI': 'NDVI',
                            'temperature_2m': 'Temperature',
                            'relative_humidity_2m': 'RelativeHumidity',
                            'rain': 'Rain',
                            'surface_pressure': 'SurfacePressure',
                            'cloud_cover': 'CloudCoverage',
                            'wind_speed_100m': 'Wind',
                            'distance-traveled': 'Migrating',
                            'location-lat': 'LastLat',
                            'location-long': 'LastLong'})


# Perform equal-width binning
for column in ['Temperature','Wind', 'NDVI','RelativeHumidity',
               'Rain','SurfacePressure', 'CloudCoverage','LastLat','LastLong']:
    data[column] = pd.cut(data[column], bins=num_bins, labels=False)
data['Migrating'] = pd.cut(data['Migrating'], bins=3, labels=False)

# Define the structure of the Bayesian network with a hidden variable
model = BayesianNetwork([('Temperature', 'Migrating'),
                         ('Wind', 'Migrating'),
                         ('NDVI', 'Migrating'),
                         ('RelativeHumidity', 'Migrating'),
                         ('Rain', 'Migrating'),
                         ('SurfacePressure', 'Migrating'),
                         ('CloudCoverage', 'Migrating'),
                         ('LastLat', 'Migrating'),
                         ('LastLong', 'Migrating')])

model.fit(data)

graph = nx.DiGraph(model.edges())

# Plot the directed graph
plt.figure(figsize=(10, 6))
pos = nx.spring_layout(graph)  # Define layout for better visualization
nx.draw(graph, pos, with_labels=True, node_size=1500, node_color="skyblue", font_size=12, font_weight="bold", arrows=True)
plt.title("Bayesian Network Visualization")
plt.show()

# Assuming you have already fitted the Bayesian network model and named it 'model'

# Get the CPDs from the model
cpds = model.get_cpds()

# Print the CPDs
for cpd in cpds:
    print(type(cpd))
    print(cpd)

print('done')
