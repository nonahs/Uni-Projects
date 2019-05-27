
CREATE TABLE MapStore (
    ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    NAME VARCHAR(255)
);

CREATE TABLE Map (
    ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    NAME VARCHAR(255),
    FILENAME VARCHAR(255),
    MAP_STOREID INT,
    FOREIGN KEY (MAP_STOREID) REFERENCES MapStore(ID)
);

CREATE TABLE OperatorStore (
    ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    NAME VARCHAR(255)
);

CREATE TABLE Operator (
    ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    FIRST_NAME VARCHAR(255),
    FAMILY_NAME VARCHAR(255),
    DOB DATE,
    LICENCE INT,
    RESCUE BOOL,
    OPERATIONS INT,
    OPERATOR_STOREID INT,
    DRONEID INT,
    FOREIGN KEY (OPERATOR_STOREID) REFERENCES OperatorStore(ID)
);

CREATE TABLE DroneStore (
    ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    NAME VARCHAR(255)
);

CREATE TABLE Drone (
    ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    NAME VARCHAR(255),
    CLASS_TYPE INT,
    RESCUE BOOL,
    DRONE_STOREID INT,
    OPERATORID INT,
    MAPID INT,
    FOREIGN KEY (DRONE_STOREID) REFERENCES DroneStore(ID),
    FOREIGN KEY (OPERATORID) REFERENCES Operator(ID),
    FOREIGN KEY (MAPID) REFERENCES Map(ID)
);

ALTER TABLE Operator ADD FOREIGN KEY (DRONEID) REFERENCES DRONE(ID);

INSERT INTO Operator (FIRST_NAME, FAMILY_NAME, DOB, LICENCE, RESCUE, OPERATIONS)
    VALUES ("Bruce", "Franks", "1995-8-5", 1, False, 1),
           ("Fred", "Stephens", "1996-5-14", 1, False, 3),
           ("Anne", "Belle", "1986-5-14", 2, False, 4),
           ("Miranda", "Daria", "1991-1-14", 1, False, 4),
           ("Big", "Bob", "1970-5-1", 2, True, 22),
           ("Sarah", "Smith", "1997-1-12", 2, True, 5),
		   ("Ron", "Howard", "1990-7-20", 2, True, 17),
           ("Rob", "White", "1985-12-10", 1, False, 1);

INSERT INTO Map (NAME, FILENAME)
    VALUES ("Abel Tasman", "map_abel_tasman_3.gif"),
           ("Ruatiti", "map_ruatiti.gif");

INSERT INTO Drone (NAME, CLASS_TYPE, RESCUE, OPERATORID, MAPID)
    VALUES ("Drone1", 2, FALSE,
        (SELECT ID FROM Operator WHERE FIRST_NAME = "Anne" AND FAMILY_NAME = "Belle"), 
        (SELECT ID FROM Map WHERE NAME = "Ruatiti"));
UPDATE Operator
    SET DRONEID = (SELECT ID FROM Drone WHERE NAME = "Drone1")
    WHERE FIRST_NAME = "Anne" AND FAMILY_NAME = "Belle";

INSERT INTO Drone (NAME, CLASS_TYPE, RESCUE, OPERATORID, MAPID)
    VALUES ("Drone2", 1, TRUE,
        (SELECT ID FROM Operator WHERE FIRST_NAME = "Sarah" AND FAMILY_NAME = "Smith"), 
        (SELECT ID FROM Map WHERE NAME = "Ruatiti"));
UPDATE Operator
    SET DRONEID = (SELECT ID FROM Drone WHERE NAME = "Drone2")
    WHERE FIRST_NAME = "Sarah" AND FAMILY_NAME = "Smith";

INSERT INTO Drone (NAME, CLASS_TYPE, RESCUE, OPERATORID, MAPID)
    VALUES ("Drone3", 1, FALSE,
        (SELECT ID FROM Operator WHERE FIRST_NAME = "Ron" AND FAMILY_NAME = "Howard"), 
        (SELECT ID FROM Map WHERE NAME = "Abel Tasman"));
UPDATE Operator
    SET DRONEID = (SELECT ID FROM Drone WHERE NAME = "Drone3")
    WHERE FIRST_NAME = "Ron" AND FAMILY_NAME = "Howard";

INSERT INTO Drone (NAME, CLASS_TYPE, RESCUE, OPERATORID, MAPID)
    VALUES ("Drone4", 1, FALSE,
        (SELECT ID FROM Operator WHERE FIRST_NAME = "Bruce" AND FAMILY_NAME = "Franks"), 
        (SELECT ID FROM Map WHERE NAME = "Ruatiti"));
UPDATE Operator
    SET DRONEID = (SELECT ID FROM Drone WHERE NAME = "Drone4")
    WHERE FIRST_NAME = "Bruce" AND FAMILY_NAME = "Franks";

INSERT INTO Drone (NAME, CLASS_TYPE, RESCUE, OPERATORID, MAPID)
    VALUES ("Drone5", 2, FALSE,
        (SELECT ID FROM Operator WHERE FIRST_NAME = "Fred" AND FAMILY_NAME = "Stephens"), 
        (SELECT ID FROM Map WHERE NAME = "Abel Tasman"));
UPDATE Operator
    SET DRONEID = (SELECT ID FROM Drone WHERE NAME = "Drone5")
    WHERE FIRST_NAME = "Fred" AND FAMILY_NAME = "Stephens";

INSERT INTO Drone (NAME, CLASS_TYPE, RESCUE, OPERATORID, MAPID)
    VALUES ("AVA Color Camera", 2, TRUE,
        (SELECT ID FROM Operator WHERE FIRST_NAME = "Big" AND FAMILY_NAME = "Bob"), 
        (SELECT ID FROM Map WHERE NAME = "Abel Tasman"));
UPDATE Operator
    SET DRONEID = (SELECT ID FROM Drone WHERE NAME = "AVA Color Camera")
    WHERE FIRST_NAME = "Big" AND FAMILY_NAME = "Bob";

INSERT INTO Drone (NAME, CLASS_TYPE, RESCUE, OPERATORID, MAPID)
    VALUES ("AVA BW Camera", 2, TRUE,
        (SELECT ID FROM Operator WHERE FIRST_NAME = "Miranda" AND FAMILY_NAME = "Daria"), 
        (SELECT ID FROM Map WHERE NAME = "Abel Tasman"));
UPDATE Operator
    SET DRONEID = (SELECT ID FROM Drone WHERE NAME = "AVA BW Camera")
    WHERE FIRST_NAME = "Miranda" AND FAMILY_NAME = "Daria";

INSERT INTO Drone (NAME, CLASS_TYPE, RESCUE)
    VALUES("AVA BW Camera #2", 2, FALSE)