DELETE FROM Pass WHERE id_station = (
    SELECT p1.id_station 
    FROM Pass p1
    JOIN Station s ON s.id_station = p1.id_station
    WHERE s.name = "?"
);

DELETE FROM Departure WHERE id_depature IN (
    SELECT d.id_depature FROM Departure d
    JOIN Station s1 ON s1.id_station = d.id_src
    JOIN Station s2 ON s2.id_station = d.id_dest
    WHERE s1.name = "?" OR s2.name = "?"
);

DELETE FROM Station WHERE name = "?";