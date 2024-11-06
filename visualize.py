import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

graphs = []
colors = ['#FF9999', '#66B2FF', '#99FF99', '#76b7b2']
col_map = {'registered_agent': {}, 'commercial_registered_agent': {}, 'owner_name': {}}
df = pd.read_csv('company_data.json')

for i in range(len(df)):
  row = df.loc[i]
  for col in col_map.keys():
    if not pd.isna(row[col]):
      if row[col] not in col_map[col]:
        col_map[col][row[col]] = []
      col_map[col][row[col]].append(row['name'])

for i, (col, data) in enumerate(col_map.items()):
  for name, companies in data.items():
    if len(companies) < 2:
      continue
    G = nx.Graph()
    G.add_node(name, color=colors[i], label=name)

    for comp in companies:
      G.add_node(comp, color=colors[3], label=comp)
      G.add_edge(name, comp)
    graphs.append(G)

plt.figure(1, figsize=(20, 16))

G = nx.Graph()
for U in graphs:
  if nx.number_connected_components(U) == 1:
    G = nx.disjoint_union(G, U)

C = (G.subgraph(c) for c in nx.connected_components(G))
pos = nx.nx_agraph.graphviz_layout(G, prog='neato')

for g in C:
  labels = nx.get_node_attributes(g, 'label')
  clrs = [nx.get_node_attributes(g, 'color').get(n) for n in g]

  nx.draw(g, pos, labels=labels, width=1, font_size=6, node_size=1000, node_color=clrs, with_labels=True)

legends = [(colors[i], legend.replace('_', ' ')) for i, legend in enumerate(col_map.keys())]
legends += [(colors[3], 'company name')]
legend_elements = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=c, markersize=10, label=l) for c, l in legends]
plt.legend(handles=legend_elements, loc='lower right')
plt.savefig('figure.png', dpi=300, bbox_inches='tight', pad_inches=0.5, format='png')
