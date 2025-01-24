import sqlite3
import os
from datetime import datetime

class DB:
    def __init__(self, folder="", database=None):
        self.folder = folder
        self.file = database

    def reconnect(self):
        self.close()
        self.connect()

    def connect(self):
        self.conn = sqlite3.connect(self.folder + self.file)
        self.cursor = self.conn.cursor()

    def executeFile(self, sqlFile, args=()):
        self.connect()
        with open(sqlFile, 'r') as sql:
            request = sql.read()
            for arg in args:
                request = request.replace('?', arg, 1)
            self.cursor.executescript(request)
        self.conn.commit()
        self.close()

    def execute(self, query, args=(), type="all"):
        self.cursor.execute(query, args)
        if type == "one":
            return self.cursor.fetchone()
        else :
            return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

    def __getData(self, filename):
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

    def insertTxtFolder(self):
        self.connect()
        DATASET_PATH = self.folder + "txt/"
        DATA_FILES_NAMES = [f for f in os.listdir(DATASET_PATH) if os.path.isfile(os.path.join(DATASET_PATH, f))]

        DATAS_RAW = {}
        for file in DATA_FILES_NAMES:
            lineNumber = file.split("_")[0]
            DATAS_RAW[lineNumber] = self.__getData(f"{DATASET_PATH}{file}")

        for (lineName, raw_lines) in DATAS_RAW.items():
            self.__insertLine(lineName)
            for (key, raw_line) in raw_lines.items():
                self.__insertStations(raw_line)
                self.__insertPass(raw_line, lineName)
                self.__insertDeparture(raw_line, lineName, key == "we_holidays")
        self.close()

    def __formatStationName(name):
        return name.replace("_", " ").replace("-", " ").lower()

    def __insertLine(self, lineName):
        REQUEST_LINE = "INSERT OR IGNORE INTO Line (name) VALUES (?);"
        self.execute(REQUEST_LINE, (lineName,))
        self.conn.commit()

    def __insertStations(self, raw_line):
        REQUEST_STATION = "INSERT OR IGNORE INTO Station (name) VALUES (?);"
        for name in raw_line['path']:
            self.execute(REQUEST_STATION, (DB.__formatStationName(name),))
        self.conn.commit()

    def __insertPass(self, raw_line, lineName):
        REQUEST_PASS = """
            INSERT OR IGNORE INTO Pass (id_station, id_line, number)
            VALUES (
                (SELECT id_station FROM Station WHERE name LIKE ?),
                (SELECT id_line FROM Line WHERE name LIKE ?),
                ?
            );
        """
        for name in raw_line['path']:
            self.execute(REQUEST_PASS, (DB.__formatStationName(name), lineName, raw_line['path'].index(name)))
        self.conn.commit()

    def __insertDeparture(self, raw_line, lineName, isWeHoliday):
        REQUEST_DEPARTURE = """
            INSERT OR IGNORE INTO Departure (id_src, id_dest, id_line, src_datetime, dest_datetime, is_we_holidays)
            VALUES (
                (SELECT id_station FROM Station WHERE name LIKE ?),
                (SELECT id_station FROM Station WHERE name LIKE ?),
                (SELECT id_line FROM Line WHERE name LIKE ?),
                ?, ?, ?
            );
        """
        for direction in ["go", "back"]:
            for (station, hours) in raw_line[direction].items():
                path = [key for key in raw_line[direction].keys()]
                stationIndex = path.index(station)

                if (stationIndex == len(path)-1):
                    continue # Stop is the last stop of the travel, so no edge to create

                for t_hour in range(len(hours)):
                    s_hour = hours[t_hour]
                    if (s_hour == '-'):
                        continue # No bus at this hour

                    nextStation = None
                    for _id_st in range(stationIndex+1, len(path)):
                        _station = path[_id_st]
                        e_hour = raw_line[direction][_station][t_hour]
                        if e_hour == '-':
                            continue
                        nextStation = _station
                        break

                    if (nextStation == None):
                        continue

                    #print(f"Ligne {lineName} : {station} ({s_hour}) -> {nextStation} ({e_hour}) [{isWeHoliday}]")
                    src = datetime.strptime(s_hour, '%H:%M')
                    dest = datetime.strptime(e_hour, '%H:%M')
                    formatted_station_s = DB.__formatStationName(station)
                    formatted_station_e = DB.__formatStationName(nextStation)
                    self.execute(REQUEST_DEPARTURE, (formatted_station_s, formatted_station_e, lineName, src, dest, isWeHoliday,))
        self.conn.commit()