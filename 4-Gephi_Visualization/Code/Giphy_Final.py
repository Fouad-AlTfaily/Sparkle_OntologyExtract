import csv
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF

g = Graph()

g.parse("C:/Users/Fouad/Desktop/Gaza_Ontology/3-Ontology Creation/Triple_Extraction/Triples/Gaza_Triples_Final.ttl", format="turtle")

ex = Namespace("http://example.com/gaza-ontology#")

nodes_csv_path = 'nodes.csv'
edges_csv_path = 'edges.csv'

nodes = set()
edges = []
node_attributes = {}  # Dictionary to store node attributes
edge_attributes = {}  # Dictionary to store edge attributes

for subj, pred, obj in g:
    nodes.add(subj)
    if isinstance(obj, URIRef):  
        nodes.add(obj)
    edges.append((subj, pred, obj))

    # Extract node attributes (if any)
    if isinstance(obj, URIRef):
        attribute_key = str(pred).split('/')[-1]  # Extract attribute key from the predicate
        if attribute_key not in node_attributes:
            node_attributes[attribute_key] = {}  # Initialize attribute dictionary if not already present
        node_attributes[attribute_key][obj] = subj
    elif isinstance(obj, Literal):
        attribute_key = str(pred).split('/')[-1]  # Extract attribute key from the predicate
        if attribute_key not in node_attributes:
            node_attributes[attribute_key] = {}  # Initialize attribute dictionary if not already present
        node_attributes[attribute_key][subj] = obj

    # Extract edge attributes (if any)
    if isinstance(subj, URIRef) and isinstance(obj, URIRef):
        attribute_key = str(pred).split('/')[-1]  # Extract attribute key from the predicate
        if attribute_key not in edge_attributes:
            edge_attributes[attribute_key] = {}  # Initialize attribute dictionary if not already present
        edge_attributes[attribute_key][(subj, obj)] = pred

    # Use verbs as predicates
    if isinstance(subj, URIRef) and isinstance(obj, URIRef):
        subj_node_type = next((str(obj_type).split('/')[-1] for obj_type in g.objects(subj, RDF.type)), None)
        obj_node_type = next((str(obj_type).split('/')[-1] for obj_type in g.objects(obj, RDF.type)), None)
        if subj_node_type == "Verb" and obj_node_type != "Verb":
            verb_uri = subj
            verb_label = str(subj).split('/')[-1]
            edges.append((obj, ex[verb_label], verb_uri))

with open(nodes_csv_path, 'w', encoding='utf-8-sig', newline='') as file:
    writer = csv.writer(file)
    # Write node attributes as header row
    attribute_keys = list(node_attributes.keys())
    writer.writerow(['Id', 'Label', 'Type'] + attribute_keys)
    for node in nodes:
        label = str(node).split('/')[-1]
        node_type = next((str(obj_type).split('/')[-1] for obj_type in g.objects(node, RDF.type)), None)
        attribute_values = [node_attributes.get(key, {}).get(node, '') for key in attribute_keys]
        writer.writerow([node, label, node_type] + attribute_values)

with open(edges_csv_path, 'w', encoding='utf-8-sig', newline='') as file:
    writer = csv.writer(file)
    # Write edge attributes as header row
    attribute_keys = list(edge_attributes.keys())
    writer.writerow(['Source', 'Target', 'Type'] + attribute_keys)
    for subj, pred, obj in edges:
        if isinstance(subj, URIRef) and isinstance(obj, URIRef):
            attribute_values = [edge_attributes.get(key, {}).get((subj, obj), '') for key in attribute_keys]
            edge_type = str(pred).split('/')[-1]
            writer.writerow([subj, obj, edge_type] + attribute_values)