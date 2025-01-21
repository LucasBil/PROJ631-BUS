from flask import Flask
from utils.networks.graph import Graph
from utils.networks.node import Node
from utils.networks.edge import Edge
from entity.stop import Stop
import json
from utils.encoder import CustomEncoder
from datetime import datetime

app = Flask(__name__)

def getData(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
    except OSError:
        print("File not found")

    def dates2dic(dates):
        dic = {}
        splitted_dates = dates.split("\n")
        for stop_dates in splitted_dates:
            tmp = stop_dates.split(" ")
            dic[tmp[0]] = tmp[1:]
        return dic

    slited_content = content.split("\n\n")
    regular_path = slited_content[0]
    regular_date_go = dates2dic(slited_content[1])
    regular_date_back = dates2dic(slited_content[2])
    we_holidays_path = slited_content[3]
    we_holidays_date_go = dates2dic(slited_content[4])
    we_holidays_date_back = dates2dic(slited_content[5])

    return {
        'regular' : {
            'path': regular_path.split(" N "),
            'go': regular_date_go,
            'back': regular_date_back
        },
        'we_holidays': {
            'path': we_holidays_path.split(" N "),
            'go': we_holidays_date_go,
            'back': we_holidays_date_back
        }
    }

def createNodes(lineraw):
    nodes = []
    for name in lineraw['path']:
        stop = Stop(name)
        node = Node(stop)
        nodes.append(node)
    return nodes

def createEdges(lineraw, nodes):
    edges = []
    paths = [
        { 'stops' : lineraw['path'], 'hours' : lineraw['go'] },
        { 'stops' : lineraw['path'][::-1], 'hours' : lineraw['back'] }
    ]
    for node in nodes:
        for path in paths:
            if node.data.name not in path['stops']:
                continue # Node is not in the path, so no edge to create

            stopIndex = path['stops'].index(node.data.name)
            if (stopIndex == len(path['stops'])-1):
                continue # Stop is the last stop of the travel, so no edge to create
            
            for t_hour in range(len(path['hours'][node.data.name])):
                if (path['hours'][node.data.name][t_hour] == '-'):
                    continue # No bus at this hour

                nextStopName = getNextStopName(node, t_hour , path['hours'])
                if nextStopName == None:
                    continue # No next stop
                
                nextNode = list(filter(lambda node: node.data.name == nextStopName, nodes))[0]
                src = datetime.strptime(path['hours'][node.data.name][t_hour], '%H:%M')
                dest = datetime.strptime(path['hours'][nextNode.data.name][t_hour], '%H:%M')

                edge = Edge(node, nextNode, weight=(src, dest))
                edges.append(edge)
    return edges

def getNextStopName(node, hour_index, dataRaw):
    passed = False
    for (stopName, hours) in dataRaw.items():
        if len(hours) == 0:
            break

        if not passed:
            passed = stopName == node.data.name
        elif hours[hour_index] != '-':
            return stopName
    return None

def _getTravel(dataRaw):
    travels = []
    travels.append(dataRaw['regular']['path']) # regular go path
    travels.append(dataRaw['regular']['path'][::-1]) # regular back path
    travels.append(dataRaw['we_holidays']['path']) # we_holiday go path
    travels.append(dataRaw['we_holidays']['path'][::-1]) # we_holiday back path
    return travels

def _getAllTravels(dataRaw:list):
    travels = []
    for data in dataRaw:
        travels += _getTravel(data)
    return travels


DATASET_PATH = "./data/"
DATA_FILES_NAMES = [
    "1_Poisy-ParcDesGlaisins.txt",
    "2_Piscine-Patinoire_Campus.txt",
    "4_Seynod_Neigeos-Campus.txt",
]
DATAS_RAW = []
for file in DATA_FILES_NAMES:
    DATAS_RAW.append(getData(DATASET_PATH + file))

GRAPHS = {
    'regular' : Graph(),
    'we_holidays' : Graph()
}

for lines in DATAS_RAW:
    for (key, line) in lines.items():
        GRAPHS[key].nodes = list(set(GRAPHS[key].nodes).union(createNodes(line)))
        GRAPHS[key].edges += createEdges(line, GRAPHS[key].nodes)

@app.route("/stops")
def getAllStop():
    nodes = list(set(GRAPHS['regular'].nodes).union(GRAPHS['we_holidays'].nodes))
    stops = list(map(lambda node: node.data, nodes)) # nodes
    return json.dumps(stops, cls=CustomEncoder, ensure_ascii=False).encode('utf-8')

@app.route("/map/<type>")
def show(type):
    GRAPHS[type].show()
    return "<p>OK</p>"

@app.route("/travels")
def getAllTravels():
    travels = _getAllTravels(DATAS_RAW)
    return json.dumps(travels, ensure_ascii=False).encode('utf-8')