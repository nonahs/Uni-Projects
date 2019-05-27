
class Drone(object):
    """ Stores details on a drone. """

    def __init__(self, name, class_type=1, rescue=False, operator=None, id=0, map_name=None):
        self.id = id
        self.name = name
        self.class_type = class_type
        self.rescue = rescue
        self.operator = operator
        self.location = None
        self.map_name = map_name


class DroneAction(object):
    """ A pending action on the DroneStore. """

    def __init__(self, drone, operator, commit_action):
        self.drone = drone
        self.operator = operator
        self.messages = []
        self._commit_action = commit_action
        self._committed = False

    def add_message(self, message):
        """ Adds a message to the action. """
        self.messages.append(message)

    def is_valid(self):
        """ Returns True if the action is valid, False otherwise. """
        return len(self.messages) == 0

    def commit(self):
        """ Commits (performs) this action. """
        if self._committed:
            raise Exception("Action has already been committed")

        self._commit_action(self.drone, self.operator)
        self._committed = True


class DroneStore(object):
    """ DroneStore stores all the drones for DALSys. """

    def __init__(self, conn=None):
        self._drones = {}
        self._last_id = 0
        self._conn = conn

    #def add(self, name, class_type = 1, rescue = False):
    def add(self, drone):
        """ Adds a new drone to the store. """
        cursor = self._conn.cursor()
        #base query
        query = 'INSERT INTO Drone (name, class_type, rescue) VALUES (%s, %s, %s)'
        cursor.execute(query, (drone[1], drone[2], drone[3]))
        self._conn.commit()
        drone_id = cursor.lastrowid
        cursor.close()
        return drone_id

    def remove(self, drone):
        """ Removes a drone from the store. """
        cursor = self._conn.cursor()
        query = 'UPDATE Operator SET Droneid = NULL WHERE Droneid = %s'
        cursor.execute(query, (drone, ))
        query = 'DELETE FROM Drone WHERE ID = %s'
        cursor.execute(query, (drone, ))
        self._conn.commit()
        cursor.close()

    def update(self, id, name, class_type, rescue):
        cursor = self._conn.cursor()
        if name is not None:
            query = 'UPDATE Drone SET Name = %s WHERE id = %s'
            cursor.execute(query, (name.title(), id))
        if class_type == 1 or class_type == 2:
            query = 'UPDATE Drone SET class_type = %s WHERE id = %s'
            cursor.execute(query, (class_type, id))
        #query = 'UPDATE Drone SET Name = %s, class_type = %s, rescue = %s WHERE id = %s'
        query = 'UPDATE Drone SET rescue = %s WHERE id = %s'
        cursor.execute(query, (rescue, id))
        self._conn.commit()
        cursor.close()

    def get(self, id):
        """ Retrieves a drone from the store by its ID. """
        cursor = self._conn.cursor()
        query = 'SELECT dr.ID, dr.name, dr.class_type, dr.rescue, dr.operatorid, mp.name FROM Drone dr LEFT JOIN Map mp ON dr.MapID = mp.ID WHERE dr.ID = %s'
        cursor.execute(query, (id, ))
        drone_exists = cursor.fetchone()
        cursor.close()
        if drone_exists is None:
            return False
        return drone_exists

    def get_operator(self, name):
        """ Retrieves a operator from the store by its Name. """
        names = name.split()
        cursor = self._conn.cursor()
        if len(names) == 1:
            query = 'SELECT LOWER(FIRST_NAME), licence, rescue, id FROM Operator WHERE FIRST_NAME = %s AND FAMILY_NAME IS NULL'
            cursor.execute(query, (names[0],))
        else:
            query = 'SELECT LOWER(CONCAT(FIRST_NAME, " ", FAMILY_NAME)), licence, rescue, id FROM Operator WHERE FIRST_NAME = %s AND FAMILY_NAME = %s'
            cursor.execute(query, (names[0], names[1]))
        operator_exists = cursor.fetchone()
        cursor.close()
        return operator_exists

    def get_drone_operator(self, id):
        """ Return a drones operator """
        cursor = self._conn.cursor()
        query = 'SELECT CONCAT(FIRST_NAME, " ", COALESCE(op.FAMILY_NAME, "")), op.ID FROM Drone dr LEFT JOIN Operator op ON dr.Operatorid = op.ID WHERE dr.ID = %s'
        cursor.execute(query, (id, ))
        drone_operator = cursor.fetchone()
        cursor.close()
        return drone_operator

    def remove_drone_operator(self, id, opid):
        cursor = self._conn.cursor()
        query = 'UPDATE Operator SET Droneid = NULL WHERE Droneid = %s'
        cursor.execute(query, (id, ))
        query = 'UPDATE Drone SET Operatorid = NULL WHERE Operatorid = %s'
        cursor.execute(query, (opid, ))
        self._conn.commit()
        cursor.close()
        
    def add_operator(self, name):
        #name = name.title()
        names = name.title().split()
        cursor = self._conn.cursor()
        if len(names) == 1:
            #first name only
            query = 'INSERT INTO Operator (first_name, licence, rescue) VALUES (%s, 1, False)'
            cursor.execute(query, (names[0],))
        else:
            query = 'INSERT INTO Operator (first_name, family_name, licence, rescue) VALUES (%s, %s, 1, False)'
            cursor.execute(query, (names[0], names[1]))
        self._conn.commit()
        cursor.close()
        return

    #def list_all(self, output_class, output_rescue):
    def list_all(self):
        """ Lists all the drones in the system. """
        cursor = self._conn.cursor()
        
        #query = 'SELECT dr.ID, dr.Name, dr.Class_type, dr.Rescue, CONCAT(op.FIRST_NAME, " ", COALESCE(op.FAMILY_NAME, "")), dr.mapID FROM Drone dr LEFT JOIN Operator op ON dr.Operatorid = op.ID ORDER BY dr.Name'
        query = 'SELECT dr.ID, dr.Name, dr.Class_type, dr.Rescue, CONCAT(op.FIRST_NAME, " ", COALESCE(op.FAMILY_NAME, "")), mp.Name FROM Drone dr LEFT JOIN Operator op ON dr.Operatorid = op.ID LEFT JOIN Map mp ON dr.mapID = mp.ID ORDER BY dr.Name'
 
        cursor.execute(query)
        for (id, name, class_type, rescue, operator, map_name) in cursor:
            rescue = 'Yes' if rescue else 'No'
            class_type = 'One' if class_type == 1 else 'Two'
            operator = '<None>' if not operator else operator
            map_name = '<None>' if not map_name else map_name
            drone = Drone(name, class_type, rescue, operator, id, map_name)
            yield drone
        cursor.close()

    def allocate(self, drone, operator):
        """ Starts the allocation of a drone to an operator. """
        cursor = self._conn.cursor()
        #get old operator
        query = 'SELECT operatorID FROM Drone WHERE id = %s'
        cursor.execute(query, (drone, ))
        oldoperator = cursor.fetchone()[0]
        #get old drone
        query = 'SELECT droneID FROM Operator WHERE id = %s'
        cursor.execute(query, (operator, ))
        olddrone = cursor.fetchone()[0]
        #remove old drone
        if olddrone:
            query = 'UPDATE Drone SET OPERATORID = NULL WHERE id = %s'
            cursor.execute(query, (olddrone, ))
        #remove old operator
        if oldoperator:
            query = 'UPDATE Operator SET DRONEID = NULL WHERE id = %s'
            cursor.execute(query, (oldoperator, ))
        #allocate drone and operator
        query = 'UPDATE Drone SET OPERATORID = %s WHERE id = %s'
        cursor.execute(query, (operator, drone))
        query = 'UPDATE Operator SET DRONEID = %s WHERE id = %s'
        cursor.execute(query, (drone, operator))
        
        self._conn.commit()
        cursor.close()

    def _allocate(self, drone, operator):
        """ Performs the actual allocation of the operator to the drone. """
        if operator.drone is not None:
            # If the operator had a drone previously, we need to clean it so it does not
            # hold an incorrect reference
            operator.drone = None
        operator.drone = drone
        drone.operator = operator
        self.save(drone)

    def save(self, drone):
        """ Saves the drone to the database. """
        cursor = self._conn.cursor()
        query = 'UPDATE Drone SET Name = %s, Class_type = %s, Rescue = %s WHERE id = %s'
        cursor.execute(query, (drone[1], drone[2], drone[3], drone[0]))
        self._conn.commit()
        cursor.close()