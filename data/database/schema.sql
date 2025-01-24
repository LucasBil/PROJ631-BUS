DROP TABLE IF EXISTS Pass;
DROP TABLE IF EXISTS Departure;
DROP TABLE IF EXISTS Line;
DROP TABLE IF EXISTS Station;

CREATE TABLE Station (
  id_station INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE
);

CREATE TABLE Line (
  id_line INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE
);

CREATE TABLE Pass (
  id_station INTEGER,
  id_line INTEGER,
  number INTEGER,
  PRIMARY KEY (id_station, id_line, number),
  FOREIGN KEY (id_station) REFERENCES Station(id_station) ON DELETE CASCADE,
  FOREIGN KEY (id_line) REFERENCES Line(id_line) ON DELETE CASCADE
);

CREATE TABLE Departure (
  id_depature INTEGER PRIMARY KEY AUTOINCREMENT,
  id_src INTEGER,
  id_dest INTEGER,
  id_line INTEGER,
  src_datetime DATETIME,
  dest_datetime DATETIME,
  is_we_holidays BOOLEAN,
  FOREIGN KEY (id_src) REFERENCES Station(id_station) ON DELETE CASCADE,
  FOREIGN KEY (id_dest) REFERENCES Station(id_station) ON DELETE CASCADE
  FOREIGN KEY (id_line) REFERENCES Line(id_line) ON DELETE CASCADE
  CHECK (src_datetime < dest_datetime)
);