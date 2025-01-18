import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD
from datetime import datetime
import re
from urllib.parse import quote_plus

# Create a new RDF graph
g = Graph()

# Define the namespace for the ontology
ex = Namespace("http://example.com/gaza-ontology#")

# Load the ontology from the gaza4.owl file
g.parse("OwlClassYouCreated.owl", format="turtle")

# Dictionary to store entity URIs
entity_uris = {}

# Function to create a URIRef for an entity
def create_entity_uri(entity_name):
    if entity_name in entity_uris:
        return entity_uris[entity_name]
    else:
        entity_uri = URIRef(ex + entity_name.replace(' ', '_'))
        entity_uris[entity_name] = entity_uri
        return entity_uri

# Create RDF triples for news articles
def create_article_triples(article_uri, date, title, text, entities, article_url, image_url, sentiment):
    g.add((article_uri, RDF.type, ex.NewsArticle))
    g.add((article_uri, ex.hasDate, Literal(date, datatype=XSD.date)))
    g.add((article_uri, ex.hasTitle, Literal(quote_plus(title), lang="ar")))
    g.add((article_uri, ex.hasText, Literal(quote_plus(text), lang="ar")))
    g.add((article_uri, ex.hasArticleURL, Literal(quote_plus(article_url), datatype=XSD.anyURI)))
    g.add((article_uri, ex.hasImageURL, Literal(quote_plus(image_url), datatype=XSD.anyURI)))
    g.add((article_uri, ex.hasSentiment, ex[sentiment]))
    for entity_name, entity_type in entities:
        entity_uri = create_entity_uri(entity_name)
        g.add((entity_uri, ex.hasName, Literal(entity_name, datatype=XSD.string)))
        g.add((entity_uri, RDF.type, ex[entity_type]))
        if entity_type == "Location":
            g.add((article_uri, ex.hasLocation, entity_uri))
        elif entity_type == "Person":
            g.add((article_uri, ex.hasPerson, entity_uri))
        elif entity_type == "Organization":
            g.add((article_uri, ex.hasOrganization, entity_uri))
        elif entity_type == "Misc":
            g.add((article_uri, ex.hasMisc, entity_uri))

# Process the segmented_text_preprocessed column and create RDF triples
def process_segmented_text(segmented_text, article_uri, date, title, text, article_url, image_url, sentiment):
    entities = set()

    # Extract entities from the segmented text
    named_entities = []
    for token in segmented_text.split():
        if token.endswith("-B-PERS") or token.endswith("-I-PERS"):
            entity_name = token.split("-")[0]
            named_entities.append((entity_name, "Person"))
        elif token.endswith("-B-ORG") or token.endswith("-I-ORG"):
            entity_name = token.split("-")[0]
            named_entities.append((entity_name, "Organization"))
        elif token.endswith("-B-LOC") or token.endswith("-I-LOC"):
            entity_name = token.split("-")[0]
            named_entities.append((entity_name, "Location"))
        elif token.endswith("-B-MISC") or token.endswith("-I-MISC"):
            entity_name = token.split("-")[0]
            named_entities.append((entity_name, "Misc"))

    # Merge consecutive named entities of the same type (except for Location)
    merged_entities = []
    i = 0
    while i < len(named_entities):
        current_entity = named_entities[i]
        if current_entity[1] != "Location":
            j = i + 1
            while j < len(named_entities) and named_entities[j][1] == current_entity[1]:
                current_entity = (current_entity[0] + " " + named_entities[j][0], current_entity[1])
                j += 1
            i = j
        else:
            i += 1
        merged_entities.append(current_entity)

    entities.update(merged_entities)

    # Perform entity linking and type refinement
    refined_entities = set()
    for entity_name, entity_type in entities:
        # Normalize entity name by removing special characters and extra spaces
        normalized_entity_name = re.sub(r'[^\w\s]', '', entity_name).strip().replace(" ", "_")
        refined_entities.add((normalized_entity_name, entity_type))

    create_article_triples(article_uri, date, title, text, refined_entities, article_url, image_url, sentiment)

# Read data from the Excel file
excel_file = "C:/Users/Fouad/Desktop/Gaza_Ontology/Data/All_Data_URL_Sentiment.xlsx"
df = pd.read_excel(excel_file)

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    article_id = str(row["ID"])
    date_str = row["Date"]
    date = datetime.strptime(date_str, "%d/%m/%Y").date().isoformat()
    title = row["Title"]
    text = row["Text"]
    article_url = row["Article_URL"]
    image_url = row["Image_URL"]
    segmented_text = row["segmented_text_preprocessed"]
    sentiment = row["Sentiment"].capitalize()

    article_uri = URIRef(ex + f"NewsArticle_{article_id}")

    process_segmented_text(segmented_text, article_uri, date, title, text, article_url, image_url, sentiment)

# Serialize the RDF graph to a file (e.g., gaza_triples_sentiment.ttl)
g.serialize(destination="Gaza_Triples.ttl", format="turtle")
