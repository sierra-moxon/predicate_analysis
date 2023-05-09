import csv
from typing import Dict, List

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
            triple = counts[1].split(",")
            triple.append(counts[0].strip())  # add count to triple
            triples.append(triple)  # add triple to list
    return triples


def download_and_parse_umls_types_file(filename):
    # download file from URL
    umls = {}
    name_map = {}
    downloads_dir = os.path.expanduser("~/Downloads")  # get path to downloads directory
    filepath = os.path.join(downloads_dir, filename)  # combine directory path and file name
    with open(filepath, 'r') as file:
        for line in file:
            items = line.strip().split("|")
            if len(items) > 2:
                umls[items[0]] = items[1]
                name_map[items[1]] = items[2]
    return umls, name_map


def get_biolink_categories(umls_dict: Dict[str, str]):
    categories = {}
    for key, value in umls_dict.items():
        categories[key] = tk.get_element_by_mapping("STY:"+value, formatted=True, most_specific=True)
    return categories


def add_full_names_back_in(triples: List[List[str]], umls_dict: Dict[str, str], name_map: Dict[str, str]):
    new_triples = []
    final_triples = []
    for triple in triples:
        if triple[1] in umls_dict:
            triple.append(umls_dict[triple[1]])
        else:
            triple.append("unmappped")
        if triple[2] in umls_dict:
            triple.append(umls_dict[triple[2]])
        else:
            triple.append("unmappped")
        new_triples.append(triple)
    for triplen in new_triples:
        # this length stuff is to hack around the fact that the SEMMEDDB mapping file is missing values like 'invt'
        if triplen[4] in name_map:
            triplen.append(name_map[triplen[4]])
        else:
            triplen.append("unmappped")
        if triplen[5] in name_map:
            triplen.append(name_map[triplen[5]])
        else:
            triplen.append("unmappped")
        final_triples.append(triplen)
        # print(triplen)
    return final_triples


def match_semmed_predicates_to_biolink(triples: List[List[str]]) -> Dict[str, str]:
    semmed_to_biolink_map = {}
    for triple in triples:
        predicate = triple[0]
        bl_predicate = tk.get_element_by_mapping("SEMMEDDB:"+predicate, formatted=True, most_specific=True)
        semmed_to_biolink_map[predicate] = bl_predicate
    return semmed_to_biolink_map


def main():
    semmeddb_triples = parse_downloads_file("semmeddb.txt")
    umls_lookup, name_map = download_and_parse_umls_types_file("SemanticTypes_2018AB.txt.1")
    category_map = get_biolink_categories(umls_lookup)
    output = open("./semmeddb_biolink_triples.tsv", "w")
    header = ("AssociationCount", "SEMMEDDBSubject", "SEMMEDBSubjectName",
              "SEMMEDDBPredicate", "SEMMEDDBObject",
              "SEMMEDDBObjectName", "BiolinkSubject", "BiolinkPredicate",
              "BiolinkObject", "ComponentMissing", "ValidEdge?")

    csv_writer = csv.writer(output, delimiter='\t')
    csv_writer.writerow(header),
    bl_predicate_map = match_semmed_predicates_to_biolink(semmeddb_triples)
    add_full_names_back_in(semmeddb_triples, umls_lookup, name_map)
    for triple in semmeddb_triples:
        subject = category_map.get(triple[1])
        p_object = category_map.get(triple[2])
        predicate = bl_predicate_map.get(triple[0])
        if predicate and subject and p_object:
            if tk.validate_edge(subject, predicate, p_object):
                # print("valid edge", subject, predicate, p_object)
                output = (triple[3], triple[1], triple[6], triple[0], triple[2], triple[7], subject,
                          predicate, p_object, "", "True")
                csv_writer.writerow(output)
            else:
                # print("invalid edge", subject, predicate, p_object)
                output = (triple[3], triple[1], triple[6], triple[0], triple[2], triple[7], subject,
                          predicate, p_object, "", "False")
                csv_writer.writerow(output)
        else:
            # print("subject or object or predicate not found")
            # print(triple, "subject", subject, "object", p_object, "predicate", predicate)
            if not subject:
                output = (triple[3], triple[1], triple[6], triple[0], triple[2], triple[7], subject,
                          predicate, p_object, triple[1], "False")
            if not p_object:
                output = (triple[3], triple[1], triple[6], triple[0], triple[2], triple[7], subject,
                          predicate, p_object, triple[2], "False")
            if not predicate:
                output = (triple[3], triple[1], triple[6], triple[0], triple[2], triple[7], subject,
                          predicate, p_object, triple[0], "False")
            csv_writer.writerow(output)


if __name__ == '__main__':
    main()
