#!/usr/bin/env python3
#
# Generate SHACL shape of the RML ontology
# Copyright (c) by Dylan Van Assche (2023)
# IDLab - Ghent University - imec

import os
import sys
import tempfile

import requests
from rdflib import Graph, Namespace

TEMP_DIR = tempfile.gettempdir()
SHAPE_URLS = {
    'core.ttl': 'https://kg-construct.github.io/rml-core/shapes/core.ttl',
    'io.ttl':   'https://kg-construct.github.io/rml-io/shapes/io.ttl',
    'cc.ttl':   'https://kg-construct.github.io/rml-cc/shapes/cc.ttl',
    'fnml.ttl': 'https://kg-construct.github.io/rml-fnml/shapes/fnml.ttl',
    'star.ttl': 'https://kg-construct.github.io/rml-star/shapes/star.ttl',
}
SHAPE_FILE = '../shapes.ttl'
SHACL = Namespace('http://www.w3.org/ns/shacl#')
RML = Namespace('http://w3id.org/rml/')


def fetch_shapes():
    """
    Fetch the SHACL shape of each module and save it.
    """
    for name, url in SHAPE_URLS.items():
        try:
            response = requests.get(url)
            response.raise_for_status()
            path = os.path.join(TEMP_DIR, name)
            with open(path, 'w') as f:
                f.write(response.text)
        except Exception:
            print(f'Unable to fetch SHACL shape: {url} '
                  f'(HTTP {response.status_code})')
            sys.exit(1)


def combine_shapes():
    """
    Combine the SHACL shapes into one SHACL shape and save it as 'shapes.ttl'.
    """
    shape = Graph()
    shape.bind('rml', RML)

    for name in SHAPE_URLS.keys():
        print(f'Reading {name}')
        g = Graph()
        g.bind('sh', SHACL)
        g.bind('rml', RML)
        try:
            shape += g.parse(os.path.join(TEMP_DIR, name), format='turtle')
        except Exception:
            print(f'Parsing SHACL shape {name} failed')
            sys.exit(2)

    print(f'Writing shape to {SHAPE_FILE}')
    shape.serialize(destination=SHAPE_FILE, format='turtle')


if __name__ == '__main__':
    shapes = fetch_shapes()
    combine_shapes()
