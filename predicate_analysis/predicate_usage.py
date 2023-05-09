import csv
import requests
from bmt import Toolkit
from pprint import pprint
import json

tk = Toolkit('https://raw.githubusercontent.com/biolink/biolink-model/v3.2.8/biolink-model.yaml')
tsv_report = open("report.tsv", "a")
tsv_writer_att = csv.writer(tsv_report, delimiter='\t')
predicates_to_test = ["biolink:ameliorates", "biolink:treats", "biolink:prevents", "biolink:affects_risk_for",
                      "biolink:predisposes", "biolink:contraindicated_for", "biolink:exacerbates"]


def main():
    try:
        smartapi_docs = requests.get(
            "https://smart-api.info/api/query?q=tags.name:translator OR tags.name:translator1&size=200").json()
    except ConnectionError:
        print("unable to fetch from smartapi")
        return {}
    collected_edges = []
    for hit in smartapi_docs.get('hits'):
        # print(hit.get('info').get('x-translator').get('team'))
        url = hit.get('servers')[0].get('url')
        if url.endswith('/'):
            url = url[:-1]
        metakg_url = f'{url}/meta_knowledge_graph'
        if metakg_url == 'https://cam-kp-api.transltr.io/1.3.0/meta_knowledge_graph' or \
           metakg_url == 'https://cam-kp-api.ci.transltr.io/1.3.0/meta_knowledge_graph' or \
           metakg_url == 'https://cam-kp-api-dev.transltr.io/1.3.0/meta_knowledge_graph':
            continue
        else:
            try:
                response = requests.get(metakg_url)
                if response.status_code == 200:
                    print(hit.get('info').get('title') + ": " + metakg_url)
                    for id in predicates_to_test:
                        retrieved_edge = {}
                        for edge in response.json().get("edges"):
                            if edge.get("predicate") == id:
                                retrieved_edge[metakg_url] = edge
                                collected_edges.append(retrieved_edge)
            except Exception as e:
                continue
    # print(info)
    with open("edges_using_predicates.json", 'w') as f:
        json.dump(collected_edges, f)
    return smartapi_docs


if __name__ == '__main__':
    main()