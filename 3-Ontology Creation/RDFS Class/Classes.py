from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS

# Create a new RDF graph
g = Graph()

# Define meaningful namespaces
onto = Namespace("http://gazawarontology.org/ontology/")
onto_res = Namespace("http://gazawarontology.org/resource/")

# Define the classes
classes = {
    "KeyFigures": "Individuals who played significant roles in the Gaza war.",
    "MilitaryOperations": "Major military operations or campaigns during the Gaza war.",
    "HumanitarianAspects": "Humanitarian issues that emerged during the Gaza war.",
    "WarTimeline": "Key events and dates that marked the Gaza war.",
    "Casualties": "Reported casualties from both sides of the conflict.",
    "MilitaryOrganizations": "Main military organizations or groups involved in the Gaza war."
}

# Iterate over classes and define them
for class_name, class_desc in classes.items():
    class_uri = onto[class_name]
    g.add((class_uri, RDF.type, RDFS.Class))
    g.add((class_uri, RDFS.label, URIRef(class_name)))
    g.add((class_uri, RDFS.comment, Literal(class_desc)))

# Serialize the graph to a file
g.serialize(destination='ontology.ttl', format='turtle')

print("done, saved.")
