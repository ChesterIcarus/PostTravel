from typing import List, Dict, Tuple
import xml.etree.ElementTree as etree
import numpy as np

from xmlparsing.xmlparse_db_util.py import XMLDatabaseHandle

class EventParser:
    database: XMLDatabaseHandle = None
    filepath: str = None
    encoding: Dict = None

    def __init__(self, database=None):
        self.database = XMLDatabaseHandle(database)

    def parse(self, filepath, bin_size=100000):
        context = etree.iterparse(filepath, events=('start', 'end'))
        context = iter(context)
        event, root = next(context)

        legs = []
        
        count = 0

        for event, elem in context:
            if event == 'start':
                if elem.tag == 'person':
                    agent_id = int(elem.attrib['id'])
            elif event == 'end':
                if elem.tag == 'route':
                    pass
                    
    def parse_events(self, elem: etree.Element):
        events = elem.text.split(" ")
        


