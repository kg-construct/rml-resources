#!/usr/bin/env python3
#
# Generate .htaccess file of redirections for the RML ontology
# Copyright (c) by Dylan Van Assche (2023)
# IDLab - Ghent University - imec
#

import csv
import requests

HTACCESS_HEADER = """# RML ontology
Header set Access-Control-Allow-Origin *
Header set Access-Control-Allow-Headers DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified$
Options +FollowSymLinks
Options -MultiViews

AddType application/rdf+xml .rdf
AddType application/rdf+xml .owl
AddType text/turtle .ttl
AddType application/n-triples .n3
AddType application/ld+json .jsonld

RewriteEngine on

"""


def template_html(resource: str, url: str):
    return \
        'RewriteCond %{HTTP_ACCEPT} !application/rdf\\+xml.*(text/html|application/xhtml\\+xml)\n' \
        'RewriteCond %{HTTP_ACCEPT} text/html [OR]\n' \
        'RewriteCond %{HTTP_ACCEPT} application/xhtml\\+xml [OR]\n' \
        'RewriteCond %{HTTP_USER_AGENT} ^Mozilla/.*\n' \
        f'RewriteRule ^{resource}/?$ {url} [NE,L,R=301]\n'


def template_jsonld(resource: str, url: str, replace_from: str, replace_to: str):
    return \
        'RewriteCond %{HTTP_ACCEPT} application/ld\\+json\n' \
        f'RewriteRule ^{resource}/?$ {url.replace(replace_from, replace_to)} [NE,L,R=301]\n'


def template_rdfxml(resource: str, url: str, replace_from: str, replace_to: str):
    return \
        'RewriteCond %{HTTP_ACCEPT} \\*/\\* [OR]\n' \
        'RewriteCond %{HTTP_ACCEPT} application/rdf\\+xml\n' \
        f'RewriteRule ^{resource}/?$ {url.replace(replace_from, replace_to)} [NE,L,R=301]\n'


def template_ntriples(resource: str, url: str, replace_from: str, replace_to: str):
    return \
        'RewriteCond %{HTTP_ACCEPT} application/n-triples\n' \
        f'RewriteRule ^{resource}/?$ {url.replace(replace_from, replace_to)} [NE,L,R=301]\n'


def template_turtle(resource: str, url: str, replace_from: str, replace_to: str):
    return \
        'RewriteCond %{HTTP_ACCEPT} text/turtle [OR]\n' \
        'RewriteCond %{HTTP_ACCEPT} text/\\* [OR]\n' \
        'RewriteCond %{HTTP_ACCEPT} \\*/turtle\n' \
        f'RewriteRule ^{resource}/?$ {url.replace(replace_from, replace_to)} [NE,L,R=301]\n'


def template_notacceptable(resource: str, url: str, replace_from: str, replace_to: str):
    return \
        'RewriteCond %{HTTP_ACCEPT} .+\n' \
        f'RewriteRule ^{resource}/?$ {url.replace(replace_from, replace_to)} [NE,L,R=406]\n'


def template_redirect(resource: str, url: str):
    return f'RewriteRule ^{resource}/?$ {url} [NE,L,R=301]\n'


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
    rules: dict = {}
    header = 'ROOT'

    print('=== Generating .htaccess file ===')

    for r in rows:
        # Header
        if 'w3id.org/rml' not in r[0]:
            header = r[0]
            continue

        # Redirect
        if r[0] == 'w3id.org/rml':
            resource = ''
        else:
            resource = r[0].replace('w3id.org/rml/', '').strip()
        url = r[1].strip()
        if header not in rules:
            rules[header] = []

        rules[header].append(f'\n# {resource} ==> {url}')

        if 'index-en.html' in url:
            rules[header].append(template_html(resource, url))
            rules[header].append(template_jsonld(resource, url,
                                                 'index-en.html',
                                                 'ontology.jsonld'))
            rules[header].append(template_rdfxml(resource, url,
                                                 'index-en.html',
                                                 'ontology.rdf'))
            rules[header].append(template_ntriples(resource, url,
                                                   'index-en.html',
                                                   'ontology.nt'))
            rules[header].append(template_turtle(resource, url,
                                                 'index-en.html',
                                                 'ontology.ttl'))
            rules[header].append(template_notacceptable(resource, url,
                                                        'index-en.html',
                                                        '406.html'))
        elif '/shapes/' in url:
            rules[header].append(template_jsonld(resource, url,
                                                 '.ttl',
                                                 '.jsonld'))
            rules[header].append(template_rdfxml(resource, url,
                                                 '.ttl',
                                                 '.rdf'))
            rules[header].append(template_ntriples(resource, url,
                                                   '.ttl',
                                                   '.nt'))
            rules[header].append(template_turtle(resource, url,
                                                 '.ttl',
                                                 '.ttl'))
            if 'core.ttl' in url:
                rules[header].append(template_notacceptable(resource, url,
                                                            'core.ttl',
                                                            '406.html'))
            elif 'io.ttl' in url:
                rules[header].append(template_notacceptable(resource, url,
                                                            'io.ttl',
                                                            '406.html'))
            elif 'star.ttl' in url:
                rules[header].append(template_notacceptable(resource, url,
                                                            'star.ttl',
                                                            '406.html'))
            elif 'cc.ttl' in url:
                rules[header].append(template_notacceptable(resource, url,
                                                            'cc.ttl',
                                                            '406.html'))
            elif 'fnml.ttl' in url:
                rules[header].append(template_notacceptable(resource, url,
                                                            'fnml.ttl',
                                                            '406.html'))
            else:
                raise NotImplementedError(f'No shape rule for {url}!')
        elif '/spec/docs' in url:
            rules[header].append(template_redirect(resource, url))
        elif 'rml-resources/ontology.ttl' in url:
            rules[header].append(template_jsonld(resource, url,
                                                 'ontology.ttl',
                                                 'ontology.jsonld'))
            rules[header].append(template_rdfxml(resource, url,
                                                 'ontology.ttl',
                                                 'ontology.rdf'))
            rules[header].append(template_ntriples(resource, url,
                                                   'ontology.ttl',
                                                   'ontology.nt'))
            rules[header].append(template_turtle(resource, url,
                                                 'ontology.ttl',
                                                 'ontology.ttl'))
            rules[header].append(template_notacceptable(resource, url,
                                                        'ontology.ttl',
                                                        '406.html'))
        elif 'rml-resources/backwards-compatibility.ttl' in url:
            rules[header].append(template_jsonld(resource, url,
                                                 'backwards-compatibility.ttl',
                                                 'backwards-compatibility.jsonld'))
            rules[header].append(template_rdfxml(resource, url,
                                                 'backwards-compatibility.ttl',
                                                 'backwards-compatibility.rdf'))
            rules[header].append(template_ntriples(resource, url,
                                                   'backwards-compatibility.ttl',
                                                   'backwards-compatibility.nt'))
            rules[header].append(template_turtle(resource, url,
                                                 'backwards-compatibility.ttl',
                                                 'backwards-compatibility.ttl'))
            rules[header].append(template_notacceptable(resource, url,
                                                        'backwards-compatibility.ttl',
                                                        '406.html'))
        elif 'rml-resources/shapes.ttl' in url:
            rules[header].append(template_jsonld(resource, url,
                                                 'shapes.ttl',
                                                 'shapes.jsonld'))
            rules[header].append(template_rdfxml(resource, url,
                                                 'shapes.ttl',
                                                 'shapes.rdf'))
            rules[header].append(template_ntriples(resource, url,
                                                   'shapes.ttl',
                                                   'shapes.nt'))
            rules[header].append(template_turtle(resource, url,
                                                 'shapes.ttl',
                                                 'shapes.ttl'))
            rules[header].append(template_notacceptable(resource, url,
                                                        'shapes.ttl',
                                                        '406.html'))
        elif 'rml-resources/resources' in url:
            rules[header].append(template_redirect(resource, url))
        elif 'rml-resources/portal' in url:
            rules[header].append(template_redirect(resource, url))
        elif '-bc.ttl' in url:
            rules[header].append(template_jsonld(resource, url,
                                                 '-bc.ttl',
                                                 '-bc.jsonld'))
            rules[header].append(template_rdfxml(resource, url,
                                                 '-bc.ttl',
                                                 '-bc.rdf'))
            rules[header].append(template_ntriples(resource, url,
                                                   '-bc.ttl',
                                                   '-bc.nt'))
            rules[header].append(template_turtle(resource, url,
                                                 '-bc.ttl',
                                                 '-bc.ttl'))
            if 'rml-core' in url:
                rules[header].append(template_notacceptable(resource, url,
                                                            'rml-core-bc.ttl',
                                                            '406.html'))
            elif 'rml-io' in url:
                rules[header].append(template_notacceptable(resource, url,
                                                            'rml-io-bc.ttl',
                                                            '406.html'))
            else:
                raise NotImplementedError(f'No bc rule for {url}!')
        elif 'eval17' in url:
            rules[header].append(template_redirect(resource, url))
        else:
            raise NotImplementedError(f'No rules for {url}!')


    with open('redirections.htaccess', 'w') as f:
        f.write(HTACCESS_HEADER)
        for header in rules.keys():
            f.write(f'# === RML {header} ===\n')
            for r in rules[header]:
                f.write(r + '\n')
            f.write('\n')
        f.flush()


if __name__ == '__main__':
    rows = read_csv()
    #verify_redirections(rows)
    generate_htaccess(rows)
