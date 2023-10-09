#!/usr/bin/env python3
#
# Generate .htaccess file of redirections for the RML ontology
# Copyright (c) by Dylan Van Assche (2023)
# IDLab - Ghent University - imec
#

import csv
import requests
from typing import List

HEADER = """# RML Ontology
RewriteEngine on
DirectorySlash Off

## RML Ontology content negotation
RewriteCond %{HTTP_ACCEPT} application/ld\\+json
RewriteRule ^(.*)\\.resource.conneg$ https://kg-construct.github.io/rml-resources/$1.json [NE,R,L]
RewriteCond %{HTTP_ACCEPT} application/n-triples
RewriteRule ^(.*)\\.resource.conneg$ https://kg-construct.github.io/rml-resources/$1.nt [NE,R,L]
RewriteCond %{HTTP_ACCEPT} application/rdf\\+xml
RewriteRule ^(.*)\\.resource.conneg$ https://kg-construct.github.io/rml-resources/$1.rdf [NE,R,L]
RewriteCond %{HTTP_ACCEPT} text/turtle
RewriteRule ^(.*)\\.resource.conneg$ https://kg-construct.github.io/rml-resources/$1.ttl [NE,R,L]
RewriteCond %{HTTP_ACCEPT} .+\n

## RML Ontology content negotiation resources
RewriteCond %{HTTP_ACCEPT} text/html
RewriteRule ^(.*)\\.(core|io|cc|fnml|star).conneg$ https://kg-construct.github.io/rml-$2/ontology/documentation/index-en.html#http://w3id.org/$1 [NE,R,L]
RewriteCond %{HTTP_ACCEPT} application/ld\\+json
RewriteRule ^(.*)\\.(core|io|cc|fnml|star).conneg$ https://kg-construct.github.io/rml-$2/ontology/documentation/ontology.jsonld#http://w3id.org/$1 [NE,R,L]
RewriteCond %{HTTP_ACCEPT} application/n-triples
RewriteRule ^(.*)\\.(core|io|cc|fnml|star).conneg$ https://kg-construct.github.io/rml-$2/ontology/documentation/ontology.nt#http://w3id.org/$1 [NE,R,L]
RewriteCond %{HTTP_ACCEPT} application/rdf\\+xml
RewriteRule ^(.*)\\.(core|io|cc|fnml|star).conneg$ https://kg-construct.github.io/rml-$2/ontology/documentation/ontology.rdf#http://w3id.org/$1 [NE,R,L]
RewriteCond %{HTTP_ACCEPT} text/turtle
RewriteRule ^(.*)\\.(core|io|cc|fnml|star).conneg$ https://kg-construct.github.io/rml-$2/ontology/documentation/ontology.ttl#http://w3id.org/$1 [NE,R,L]
RewriteCond %{HTTP_ACCEPT} .+\n
RewriteRule (.*)\\.(core|io|cc|fnml|star|resource).conneg$ https://kg-construct.github.io/rml-resources/406.html [NE,L,R=406]
"""


def extract_spec(url: str):
    spec = None
    if 'rml-core' in url:
        spec = 'core'
    elif 'rml-cc' in url:
        spec = 'cc'
    elif 'rml-io' in url:
        spec = 'io'
    elif 'rml-fnml' in url:
        spec = 'fnml'
    elif 'rml-star' in url:
        spec = 'star'
    else:
        raise NotImplementedError(f'No spec matches this URL: {url}')

    return spec


def template_resources(resources: List[str], spec: str):
    return \
        'RewriteCond %{REQUEST_URI} (' + '|'.join(resources) + ')$\n' \
        'RewriteRule ^(.*)$ https://%{SERVER_NAME}/$1.' + spec + '.conneg [NE,R,L]\n'

def template_ontology(spec: str):
    return \
        'RewriteCond %{REQUEST_URI} ' + spec + '\n' \
        'RewriteRule ' + spec + \
        '/?$ https://kg-construct.github.io/rml-' + spec + \
        '/ontology/documentation/index-en.html [NE,R,L]'


def template_shapes(spec: str):
    return \
        'RewriteCond %{REQUEST_URI} ' + spec + '/shapes\n' \
        'RewriteRule ' + spec + \
        '/shapes/?$ https://kg-construct.github.io/rml-' + spec + \
        '/shapes/' + spec + '.ttl [NE,R,L]'


def template_spec(spec: str):
    return \
        'RewriteCond %{REQUEST_URI} ' + spec + '/spec\n' \
        'RewriteRule ' + spec + \
        '/spec/?$ https://kg-construct.github.io/rml-' + spec + \
        '/spec/docs [NE,R,L]'


def template_bc(spec: str):
    return \
        'RewriteCond %{REQUEST_URI} ' + spec + '/bc\n' \
        'RewriteRule ' + spec + \
        '/bc/?$ https://kg-construct.github.io/rml-' + spec + \
        '/ontology/rml-' + spec + '-bc.ttl [NE,R,L]'


def template_notacceptable(resource: str, url: str, replace_from: str,
                           replace_to: str):
    return \
        'RewriteCond %{HTTP_ACCEPT} .+\n' \
        f'RewriteRule {resource}/?$ {url.replace(replace_from, replace_to)}' \
        ' [NE,L,R=406]\n'


def template_redirect(resource: str, url: str):
    return f'RewriteRule {resource}/?$ {url} [NE,L,R=301]\n'


def template_redirect_negotiate(resource: str, name: str, root: bool):
    if root:
        return \
            'RewriteRule ^$ https://%{SERVER_NAME}/' + name + '.resource.conneg [NE,R,L]\n'
    else:
        return \
            'RewriteCond %{REQUEST_URI} ' + resource + '$\n' \
            'RewriteRule (.*)$ https://%{SERVER_NAME}/' + name + '.resource.conneg [NE,R,L]\n'


def read_csv():
    rows = []
    with open('redirections.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for r in reader:
            rows.append(r)
    return rows


def verify_redirections(rows: list):
    print('=== Verifying redirections ===')

    for r in rows:
        url = r[1].strip().replace('$1', '')
        if url == '':
            continue

        r = requests.head(url)
        print(f'{url}: HTTP {r.status_code}')
        r.raise_for_status()


def generate_htaccess(rows: list):
    print('=== Generating .htaccess file ===')

    resources: dict = {
        'core': [],
        'io': [],
        'cc': [],
        'fnml': [],
        'star': []
    }
    rules: dict = {
        'eval17': [],
        'core': [],
        'io': [],
        'cc': [],
        'fnml': [],
        'star': [],
        'resources': []
    }

    for r in rows:
        # Header
        if 'w3id.org/rml' not in r[0]:
            continue

        # Redirect
        if r[0] == 'w3id.org/rml':
            resource = ''
        else:
            resource = r[0].replace('w3id.org/rml/', '').strip()
        url = r[1].strip()

        if resource not in ['core', 'io', 'cc', 'fnml', 'star'] \
                and 'index-en.html' in url:
            spec = extract_spec(url)
            resources[spec].append(resource)
        elif 'index-en.html' in url:
            spec = extract_spec(url)
            rules[spec].append(template_ontology(spec))
            rules[spec].append(template_spec(spec))
            rules[spec].append(template_shapes(spec))
        elif 'rml-resources/ontology.ttl' in url or \
             'rml-resources/backwards-compatibility.ttl' in url or \
             'rml-resources/shapes.ttl' in url:
            name = url.split('/')[-1].replace('.ttl', '')
            root = False
            if 'rml-resources/ontology.ttl' in url:
                root = True
            rules['resources'].append(template_redirect_negotiate(resource,
                                                                  name, root))
        elif 'rml-resources' in url:
            rules['resources'].append(template_redirect(resource, url))
        elif '-bc.ttl' in url:
            spec = extract_spec(url)
            rules[spec].append(template_bc(spec))
        elif 'eval17' in url:
            rules['eval17'].append(template_redirect(resource, url))

    for spec in ['core', 'io', 'cc', 'fnml', 'star']:
        rules[spec].append(template_resources(resources[spec], spec))

    with open('redirections.htaccess', 'w') as f:
        f.write(HEADER)
        for key in sorted(rules.keys()):
            f.write(f'# === RML {key} ===\n')
            for r in rules[key]:
                f.write(r + '\n')
            f.write('\n')
        f.write('RewriteRule ^(.*)$' +
                ' https://kg-construct.github.io/rml-resources/404.html' +
                ' [NE,L,R=404]\n')
        f.flush()


if __name__ == '__main__':
    rows = read_csv()
    # verify_redirections(rows)
    generate_htaccess(rows)
