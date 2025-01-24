from flask import Flask, request, jsonify
from utils.networks.graph import Graph
from utils.networks.node import Node
from utils.networks.edge import Edge
from entity.station import Station
from entity.db import DB
import json
from utils.encoder import CustomEncoder
from datetime import datetime
import holidays

app = Flask(__name__)

def createNodes(db:DB, isWeHolidays):
    REQUEST_GETALL_STATIONS_BY_WE_HOLIDAYS = """
        SELECT s.* FROM Station s
        JOIN Departure d on d.id_src = d.id_src
        WHERE d.is_we_holidays = ?
        GROUP BY s.id_station;
    """
    db.connect()
    formatted_bool = 1 if isWeHolidays else 0
    datas = db.execute(REQUEST_GETALL_STATIONS_BY_WE_HOLIDAYS, (formatted_bool,))
    db.close()
    return [Node(Station(data[1])) for data in datas]

def createEdges(db:DB, isWeHolidays, nodes):
    REQUEST_GETALL_STATIONS_BY_WE_HOLIDAYS = """
        SELECT s1.name, s2.name, l.name, d.src_datetime, d.dest_datetime FROM Departure d
        JOIN Station s1 on s1.id_station = d.id_src
        JOIN Station s2 on s2.id_station = d.id_dest
        JOIN Line l ON l.id_line = d.id_line
        WHERE d.is_we_holidays = ?;
    """
    db.connect()
    edges = []
    formatted_bool = 1 if isWeHolidays else 0
    datas = db.execute(REQUEST_GETALL_STATIONS_BY_WE_HOLIDAYS, (formatted_bool,))
    for data in datas:
        src = list(filter(lambda node: node.data == data[0] , nodes))[0]
        dest = list(filter(lambda node: node.data == data[1] , nodes))[0]
        s_datetime = datetime.strptime(data[3], "%Y-%m-%d %H:%M:%S")
        d_datetime = datetime.strptime(data[4], "%Y-%m-%d %H:%M:%S")
        edges += [ Edge(src, dest, [s_datetime, d_datetime, None, data[2]]) ]
    db.close()
    return edges

def generateGraphs(db:DB, graphs):
    for (type, graph) in graphs.items():
        graph.nodes = createNodes(db, type)
        graph.edges = createEdges(db, type, graph.nodes)

def isWeHoliday(date):
    fr_holidays = holidays.France()
    return date in fr_holidays or date.weekday() in [5, 6] # Saturday or Sunday

db = DB("./data/", "database/database.db")
if input("Do you want to reset/create the database ? (y/n) ") == 'y':
    db.executeFile("./data/database/schema.sql")
if input("Do you want to insert the data in txt folder ? (y/n) ") == 'y':
    db.insertTxtFolder()

GRAPHS = {
    'regular' : Graph([], []),
    'we_holidays' : Graph([], [])
}

generateGraphs(db, GRAPHS)

@app.route("/map/<type>")
def show(type):
    GRAPHS[type].show()
    return '<img src="static/assets/map.png" />'

# CRUD Station

@app.route("/stations")
def getAllStations():
    REQUEST_GETALL_STATIONS = """
        SELECT * FROM Station;
    """
    db.connect()
    datas = db.execute(REQUEST_GETALL_STATIONS, ())
    db.close()
    return json.dumps([Station(data[1]) for data in datas], cls=CustomEncoder, ensure_ascii=False).encode('utf-8')

@app.route("/station/<name>")
def getStation(name:str):
    REQUEST_GET_STATIONS = """
        SELECT * FROM Station
        WHERE name = ?;
    """
    try:
        db.connect()
        data = db.execute(REQUEST_GET_STATIONS, (name,), type="one")
        if data is None:
            return jsonify({"error": f"Station not found"}), 404
        station = Station(data[1])
        db.conn.commit()
        db.close()
    except KeyError as e:
        return jsonify({"error": f"Missing key : {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500
    return json.dumps(station, cls=CustomEncoder, ensure_ascii=False).encode('utf-8')

@app.route("/station", methods = ['POST'])
def postStation():
    REQUEST_INSERT_STATION = """
        INSERT INTO Station (name) VALUES (?);
    """
    try:
        data = request.get_json()
        db.connect()
        db.execute(REQUEST_INSERT_STATION, (data["name"],))
        db.conn.commit()
        db.close()
        generateGraphs(db, GRAPHS)
    except KeyError as e:
        return jsonify({"error": f"Missing key : {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500
    return jsonify(), 200

@app.route("/station", methods = ['PUT'])
def updateStation():
    REQUEST_INSERT_STATION = """
        UPDATE Station SET name = ? WHERE name = ?;
    """
    try:
        data = request.get_json()
        db.connect()
        db.execute(REQUEST_INSERT_STATION, (data["updated_name"],data["name"],))
        db.conn.commit()
        db.close()
        generateGraphs(db, GRAPHS)
    except KeyError as e:
        return jsonify({"error": f"Missing key : {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500
    return jsonify(), 200

@app.route("/station", methods = ['DELETE'])
def deleteStation():
    try:
        data = request.get_json()
        db.executeFile("./data/database/script/deleteStation.sql", (data["name"],data["name"], data["name"], data["name"]))
        generateGraphs(db, GRAPHS)
    except KeyError as e:
        return jsonify({"error": f"Missing key : {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500
    return jsonify(), 200

# CRUD Line

@app.route("/lines")
def getAllLines():
    REQUEST_GETALL_LINES = """
        SELECT * FROM Line;
    """
    db.connect()
    datas = db.execute(REQUEST_GETALL_LINES, ())
    db.close()
    return json.dumps([{ "name" : data[1] } for data in datas], cls=CustomEncoder, ensure_ascii=False).encode('utf-8')

@app.route("/line/<name>")
def getLine(name:str):
    REQUEST_GET_LINE = """
        SELECT * FROM Line
        WHERE name = ?;
    """
    try:
        db.connect()
        data = db.execute(REQUEST_GET_LINE, (name,), type="one")
        if data is None:
            return jsonify({"error": f"Station not found"}), 404
        line = { "name" : data[1] }
        db.close()
    except KeyError as e:
        return jsonify({"error": f"Missing key : {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500
    return json.dumps(line, cls=CustomEncoder, ensure_ascii=False).encode('utf-8')

@app.route("/line", methods = ['POST'])
def postLine():
    REQUEST_POST_LINE = """
        INSERT INTO Line (name) VALUES (?);
    """
    try:
        data = request.get_json()
        db.connect()
        db.execute(REQUEST_POST_LINE, (data["name"],))
        db.conn.commit()
        db.close()
    except KeyError as e:
        return jsonify({"error": f"Missing key : {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500
    return jsonify(), 200

@app.route("/line", methods = ['PUT'])
def updateLine():
    REQUEST_UPDATE_LINE = """
        UPDATE Line SET name = ? WHERE name = ?;
    """
    try:
        data = request.get_json()
        db.connect()
        db.execute(REQUEST_UPDATE_LINE, (data["updated_name"],data["name"],))
        db.conn.commit()
        db.close()
        generateGraphs(db, GRAPHS)
    except KeyError as e:
        return jsonify({"error": f"Missing key : {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500
    return jsonify(), 200

@app.route("/line", methods = ['DELETE'])
def deleteLine():
    try:
        data = request.get_json()
        db.executeFile("./data/database/script/deleteLine.sql", (data["name"],data["name"], data["name"]))
        generateGraphs(db, GRAPHS)
    except KeyError as e:
        return jsonify({"error": f"Missing key : {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500
    return jsonify(), 200

# CRUD Departure

@app.route("/travels")
def getAllTravels():
    REQUEST_GETALL_TRAVELS = """
        SELECT s.name, l.name, p.number FROM Pass p
        JOIN Station s on s.id_station = p.id_station
        JOIN Line l ON l.id_line = p.id_line;
    """
    db.connect()
    datas = db.execute(REQUEST_GETALL_TRAVELS, ())
    db.close()
    travels = {}
    for data in datas:
        if not travels.get(data[1]):
            travels[data[1]] = [{"name": data[0], "index": data[2]}]
        else:
            travels[data[1]] += [{"name": data[0], "index": data[2]}]
    
    for (line, stations) in travels.items():
        stations.sort(key=lambda _station: _station["index"])
        path = [Station(station["name"]) for station in stations]
        travels[line] = [path, path[::-1]]
    return json.dumps(travels, cls=CustomEncoder, ensure_ascii=False).encode('utf-8')

def AlgoParameters(data):
    start = datetime.strptime(data["datetime"],'%d/%m/%Y %H:%M')
    graphType = 'regular'
    if (isWeHoliday(start)):
        graphType = 'we_holidays'

    srcNode = GRAPHS[graphType].getNode(data["src"])
    destNode = GRAPHS[graphType].getNode(data["dest"])
    time_only = datetime.strptime(start.strftime('%H:%M'), '%H:%M')
    return (srcNode, destNode, time_only, graphType)

@app.route("/shortest", methods = ['POST'])
def getShortest():
    data = request.get_json()
    (srcNode, destNode, time_only, graphType) = AlgoParameters(data)
    if (srcNode == None or destNode == None): # Error wrong parameters
        return jsonify({"error": "Wrong parameters", "message": "Source or destination doesn't exists"}), 400

    (nodes, edges) = GRAPHS[graphType].shortest(srcNode, destNode, time_only)
    return json.dumps({ 'stations': nodes, 'pass': edges }, cls=CustomEncoder, ensure_ascii=False).encode('utf-8')

@app.route("/fastest", methods = ['POST'])
def getFastest():
    data = request.get_json()
    (srcNode, destNode, time_only, graphType) = AlgoParameters(data)
    if (srcNode == None or destNode == None): # Error wrong parameters
        return jsonify({"error": "Wrong parameters", "message": "Source or destination doesn't exists"}), 400

    print(f"Check edge : {GRAPHS[graphType].errorDataEdges()}")
    (nodes, edges) = GRAPHS[graphType].fastest(srcNode, destNode, time_only)
    return json.dumps({ 'stations': nodes, 'pass': edges }, cls=CustomEncoder, ensure_ascii=False).encode('utf-8')