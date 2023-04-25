import csv
from typing import Dict

import requests
from bmt import Toolkit
from pprint import pprint
import os

tk = Toolkit('https://raw.githubusercontent.com/biolink/biolink-model/v3.2.8/biolink-model.yaml')
tsv_report = open("report.tsv", "a")
tsv_writer_att = csv.writer(tsv_report, delimiter='\t')


def parse_downloads_file(filename):
    downloads_dir = os.path.expanduser("~/Downloads")  # get path to downloads directory
    filepath = os.path.join(downloads_dir, filename)  # combine directory path and file name
    triples = []
    with open(filepath, 'r') as file:
        for line in file:
            counts = line.strip().split(" ")
            triples.append(counts[1].split(","))  # add triple to list
    return triples


def download_and_parse_umls_types_file(filename):
    # download file from URL
    umls = {}
    downloads_dir = os.path.expanduser("~/Downloads")  # get path to downloads directory
    filepath = os.path.join(downloads_dir, filename)  # combine directory path and file name
    with open(filepath, 'r') as file:
        for line in file:
            items = line.strip().split("|")
            if len(items) > 2:
                umls[items[0]] = items[1]
    return umls


def get_biolink_categories(umls_dict: Dict[str, str]):
    categories = {}
    for key, value in umls_dict.items():
        categories[key] = tk.get_element_by_mapping("STY:"+value, formatted=True, most_specific=True)
    return categories


def main():
    semmeddb_triples = parse_downloads_file("semmeddb.txt")
    umls_lookup = download_and_parse_umls_types_file("SemanticTypes_2018AB.txt.1")
    category_map = get_biolink_categories(umls_lookup)
    output = open("semmeddb_biolink_triples.tsv", "w")
    tsv_writer = csv.writer(output, delimiter='\t')
    for triple in semmeddb_triples:
        print(triple)
        subject = category_map.get(triple[1])
        p_object = category_map.get(triple[2])
        predicate_name = tk.get_element("biolink:"+triple[0])
        if predicate_name is not None:
            if tk.validate_edge(subject, predicate_name, p_object):
                print("valid edge", subject, predicate_name, p_object)
            else:
                print("invalid edge", subject, predicate_name, p_object)
        else:
            print("predicate not found", triple[0])


if __name__ == '__main__':
    main()
