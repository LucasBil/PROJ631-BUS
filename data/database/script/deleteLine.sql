DELETE FROM Pass WHERE id_line = (
    SELECT l.id_line 
    FROM Line l
    WHERE l.name = "?"
);

DELETE FROM Departure WHERE id_depature IN (
    SELECT d.id_depature FROM Departure d
    JOIN Line l ON l.id_line = d.id_line
    WHERE l.name = "?"
);

DELETE FROM Line WHERE name = "?";