#!/usr/bin/env python3
#
# Generate .htaccess file of redirections for the RML ontology
# Copyright (c) by Dylan Van Assche (2023)
# IDLab - Ghent University - imec
#

import csv

HTACCESS_HEADER = """# RML ontology
Header set Access-Control-Allow-Origin *
Header set Access-Control-Allow-Headers DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified$
Options +FollowSymLinks
RewriteEngine on

"""


def read_csv():
    rows = []
    with open('redirections.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for r in reader:
            rows.append(r)
    return rows


def generate_htaccess(rows: list):
    rules: dict = {}
    header = 'ROOT'

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
        rules[header].append(f'RewriteRule ^{resource}/?$ {url} [NE,L,R=301]')

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
    generate_htaccess(rows)
