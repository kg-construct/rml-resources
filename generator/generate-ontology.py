#!/usr/bin/env python3
#
# Generate RML ontology from all its modules
# Copyright (c) by Dylan Van Assche (2023)
# IDLab - Ghent University - imec

import os
import sys
import tempfile

import requests
from rdflib import Graph, Namespace

TEMP_DIR = tempfile.gettempdir()
ONTOLOGY_URLS = {
    'core.owl': 'https://kg-construct.github.io/rml-core/ontology/rml-core.owl',
    'io.owl':   'https://kg-construct.github.io/rml-io/ontology/rml-io.owl',
    'cc.owl':   'https://kg-construct.github.io/rml-cc/ontology/rml-cc.owl',
    'fnml.owl': 'https://kg-construct.github.io/rml-fnml/ontology/rml-fnml.owl',
    'star.owl': 'https://kg-construct.github.io/rml-star/ontology/rml-star.owl',
    'lv.owl': 'https://kg-construct.github.io/rml-lv/ontology/rml-lv.owl',
}
ONTOLOGY_TTL = '../ontology.ttl'
ONTOLOGY_RDF = '../ontology.rdf'
ONTOLOGY_JSONLD = '../ontology.jsonld'
ONTOLOGY_NT = '../ontology.nt'
RML = Namespace('http://w3id.org/rml/')


def fetch_ontologies():
    """
    Fetch the ontology of each module and save it.
    """
    for name, url in ONTOLOGY_URLS.items():
        try:
            response = requests.get(url)
            response.raise_for_status()
            path = os.path.join(TEMP_DIR, name)
            with open(path, 'w') as f:
                f.write(response.text)
        except Exception:
            print(f'Unable to fetch ontology: {url} '
                  f'(HTTP {response.status_code})')
            sys.exit(1)


def combine_ontologies():
    """
    Combine the ontologies into one ontology and save it as 'ontologies.ttl'.
    """
    ontology = Graph()
    ontology.bind('rml', RML)

    for name in ONTOLOGY_URLS.keys():
        print(f'Reading {name}')
        g = Graph()
        g.bind('rml', RML)
        try:
            ontology += g.parse(os.path.join(TEMP_DIR, name), format='turtle')
        except Exception:
            print(f'Parsing ontology {name} failed')
            sys.exit(2)

    print('Writing ontology...')
    ontology.serialize(destination=ONTOLOGY_TTL, format='turtle',
                       encoding='utf-8')
    ontology.serialize(destination=ONTOLOGY_RDF, format='xml',
                       encoding='utf-8')
    ontology.serialize(destination=ONTOLOGY_JSONLD, format='json-ld',
                       encoding='utf-8')
    ontology.serialize(destination=ONTOLOGY_NT, format='ntriples',
                       encoding='utf-8')


if __name__ == '__main__':
    ontologies = fetch_ontologies()
    combine_ontologies()
