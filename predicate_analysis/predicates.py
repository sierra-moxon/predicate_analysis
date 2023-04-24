import csv
import requests
from biothings_explorer.smartapi_kg.dataload import load_specs
from pprint import pprint
from bmt import Toolkit
import linkml_runtime

tk = Toolkit('https://raw.githubusercontent.com/biolink/biolink-model/3.2.7/biolink-model.yaml')
tsv_file = open("predicates.tsv", "a")
tsv_attributes = open("attributes.tsv", "a")
tsv_writer = csv.writer(tsv_file, delimiter='\t')
tsv_writer_att = csv.writer(tsv_attributes, delimiter='\t')


def sample_predicates():
    team_group = ""
    specs = load_specs()
    kp_titles = []
    for spec in specs:
        if 'x-translator' not in spec['info']:
            continue
        if spec['info']['x-translator']['component'] == 'KP':
            kp_titles.append(spec['info']['title'])
            team_group = spec['info']['x-translator']['team']
        if 'servers' not in spec:
            print("servers param not found, can't query MKG for:+ " + spec.get('info'))
        else:
            url = spec['servers'][0]['url']
            if url.endswith('/'):
                url = url[:-1]
            predicates_url = f'{url}/meta_knowledge_graph'
            trapi, predicates = get_predicates(predicates_url)
            if not predicates:
                continue
            else:
                preds, attribs, url = dump_trapi_predicate_results(predicates, predicates_url, team_group)
                attributes = set(attribs)
                for attrib in attributes:
                    print(attrib)
                    if attrib.startswith('infores'):
                        tsv_writer_att.writerow([url, attrib])


def in_biolink_model(predicate):
    is_predicate = tk.is_predicate(predicate)
    return is_predicate


def dump_trapi_predicate_results(predicates, url, team_group):
    preds = []
    attribs = []
    for edge in predicates.get('edges'):
        predicate = edge.get('predicate')
        subject = edge.get('subject')
        objectt = edge.get('object')
        preds.append(predicate)
        for team in team_group:
            if 'attributes' in edge and edge.get('attributes') is not None:
                for attribute in edge.get('attributes'):
                    attribs.append(attribute.get('attribute_type_id'))
                    tsv_writer.writerow([team,
                                         url,
                                         subject,
                                         predicate,
                                         objectt,
                                         attribute.get('attribute_source'),
                                         attribute.get('attribute_type_id'),
                                         attribute.get('attribute_value')])
            else:
                tsv_writer.writerow([team,
                                     url,
                                     subject,
                                     predicate,
                                     objectt,
                                     "",
                                     ""])
    preds = set(preds)
    attribs = set(attribs)
    return preds, attribs, url


def get_predicates(pr_url):
    try:
        response = requests.get(pr_url)
        print(str(response.status_code) + " " + pr_url)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {}
    except:
        return False, {}


# if __name__ == '__main__':
#     sample_predicates()
