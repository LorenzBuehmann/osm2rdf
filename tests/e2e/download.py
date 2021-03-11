#!/usr/bin/env python3

import collections
import requests
import sys
import xml.dom.minidom
import xml.sax

url_template = 'https://www.openstreetmap.org/api/0.6/{kind}/{identifier}'
OsmObject = collections.namedtuple('OsmObject', ['kind', 'identifier'])

class OsmHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.obj = OsmObject(kind='', identifier='')
        self.children = []
        self.cnt = 0

    def startElement(self, name, attributes):
        if self.cnt == 0:
          self.obj = OsmObject(kind=name, identifier=attributes['id'])
        else:
          if name == 'nd':
            self.children.append(OsmObject(kind='node', identifier=attributes['ref']))
        self.cnt += 1

def get_objects_from_file(filename):
    osm_handler = OsmHandler()
    parser = xml.sax.make_parser()
    parser.setContentHandler(osm_handler)
    parser.parse(filename)
    return osm_handler.obj, osm_handler.children

def get_filename_for_kind_and_identifiert(osm_object):
  return '{kind}{identifier:0>12d}.xml'.format(kind=osm_object.kind,identifier=int(osm_object.identifier))
  

def download(osm_object, recursive=True):
    r = requests.get(url_template.format(kind=osm_object.kind,identifier=osm_object.identifier), allow_redirects=True)
    with open(get_filename_for_kind_and_identifiert(osm_object), 'w') as out:
        out.write(xml.dom.minidom.parseString(''.join([l.strip() for l in r.text.split('\n') if l and l != '<?xml version="1.0" encoding="UTF-8"?>' and not l.startswith('<osm') and  not l == '</osm>'])).toprettyxml(indent='  ')[23:])
    if recursive:
        _, children = get_objects_from_file(get_filename_for_kind_and_identifiert(osm_object))
        for child in children:
            download(child)
  


if __name__ == '__main__':
    download(OsmObject(kind=sys.argv[1], identifier=sys.argv[2]))
