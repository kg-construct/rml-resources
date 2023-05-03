#!/usr/bin/env python3
#
# Generate backwards compatibility of the RML ontology with the old RML
# ontology and R2RML ontology.
# Copyright (c) by Dylan Van Assche (2023)
# IDLab - Ghent University - imec

import os
import sys
import tempfile

import requests
from rdflib import Graph, Namespace

TEMP_DIR = tempfile.gettempdir()
BACKWARDS_COMPATIBILITY_URLS = {
#    'core-bc.ttl':   'https://kg-construct.github.io/rml-core/ontology/rml-core-bc.ttl',
    'io-bc.ttl':   'https://kg-construct.github.io/rml-io/ontology/rml-io-bc.ttl',
}
BACKWARDS_COMPATIBILITY_FILE = '../backwards-compatibility.ttl'
RML = Namespace('http://w3id.org/rml/')
OLDRML = Namespace('http://semweb.mmlab.be/ns/rml#')
R2RML = Namespace('http://www.w3.org/ns/r2rml#')
QL = Namespace('http://semweb.mmlab.be/ns/ql#')


def fetch_backwards_compatibilities():
    """
    Fetch the backwards compatibility of each module and save it.
    """
    for name, url in BACKWARDS_COMPATIBILITY_URLS.items():
        try:
            response = requests.get(url)
            response.raise_for_status()
            path = os.path.join(TEMP_DIR, name)
            with open(path, 'w') as f:
                f.write(response.text)
        except Exception:
            print(f'Unable to fetch backwards compatibility: {url} '
                  f'(HTTP {response.status_code})')
            sys.exit(1)


def combine_backwards_compatibilities():
    """
    Combine the backwards compatibilities into one backwards compatibility
    and save it as 'backwards_compatibilities.ttl'.
    """
    backwards_compatibility = Graph()
    backwards_compatibility.bind('rml', RML)
    backwards_compatibility.bind('oldrml', OLDRML)
    backwards_compatibility.bind('ql', QL)
    backwards_compatibility.bind('rr', R2RML)

    for name in BACKWARDS_COMPATIBILITY_URLS.keys():
        print(f'Reading {name}')
        g = Graph()
        g.bind('rml', RML)
        g.bind('oldrml', OLDRML)
        g.bind('ql', QL)
        g.bind('rr', R2RML)
        try:
            backwards_compatibility += g.parse(os.path.join(TEMP_DIR, name),
                                               format='turtle')
        except Exception:
            print(f'Parsing backwards_compatibility {name} failed')
            sys.exit(2)

    print(f'Writing backwards_compatibility to {BACKWARDS_COMPATIBILITY_FILE}')
    backwards_compatibility.serialize(destination=BACKWARDS_COMPATIBILITY_FILE,
                                      format='turtle')


if __name__ == '__main__':
    backwards_compatibilities = fetch_backwards_compatibilities()
    combine_backwards_compatibilities()
