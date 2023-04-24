import csv
import requests
from bmt import Toolkit
from pprint import pprint

tk = Toolkit('https://raw.githubusercontent.com/biolink/biolink-model/v3.2.8/biolink-model.yaml')
tsv_report = open("report.tsv", "a")
tsv_writer_att = csv.writer(tsv_report, delimiter='\t')


def main():
    try:
        smartapi_docs = requests.get(
            "https://smart-api.info/api/query?q=tags.name:translator OR tags.name:translator1&size=200").json()
    except ConnectionError:
        print("unable to fetch from smartapi")
        return {}
    for hit in smartapi_docs.get('hits'):
        # print(hit.get('info').get('x-translator').get('team'))
        url = hit.get('servers')[0].get('url')
        if url.endswith('/'):
            url = url[:-1]
        metakg_url = f'{url}/meta_knowledge_graph'
        try:
            response = requests.get(metakg_url)
            if response.status_code == 200:
                print(hit.get('info').get('title') + ": " + metakg_url)
                for edge in response.json().get("edges"):
                    for attribute in edge.get("attributes"):
                        if attribute.get("attribute_type_id").endswith("knowledge_source"):
                            if attribute.get("attribute_source").startswith("infores:semmeddb"):
                                print("found semmeddb", attribute.get("attribute_type_id"))
            else:
                print(hit.get('info').get('title'))
        except:
            continue
    # print(info)
    return smartapi_docs


if __name__ == '__main__':
    main()
