
from datetime import date

class Operator(object):
    """ Stores details on an operator. """

    def __init__(self, first_name, family_name, licence, rescue, operations, droneid, drone_name, id):
        self.id = id
        self.first_name = first_name
        self.family_name = family_name
        self.date_of_birth = None
        self.drone_license = licence
        self.rescue_endorsement = rescue
        self.operations = operations
        self.drone = droneid
        self.drone_name = drone_name


class OperatorAction(object):
    """ A pending action on the OperatorStore. """

    def __init__(self, operator, commit_action):
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

        self._commit_action(self.operator)
        self._committed = True


class OperatorStore(object):
    """ Stores the operators. """

    def __init__(self, conn=None):
        self._operators = {}
        self._last_id = 0
        self._conn = conn

    def add(self, operator):
        """ Starts adding a new operator to the store. """
        cursor = self._conn.cursor()
        query = 'INSERT INTO Operator (first_name, family_name, licence, rescue, operations) VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(query, (operator[0], operator[1], operator[2], operator[3], operator[4]))
        self._conn.commit()
        cursor.close()

    def _add(self, operator):
        """ Adds a new operator to the store. """
        if operator.id in self._operators:
            raise Exception('Operator already exists in store')
        else:
            self._last_id += 1
            operator.id = self._last_id
            self._operators[operator.id] = operator

    def remove(self, operator):
        """ Removes a operator from the store. """
        if not operator.id in self._operators:
            raise Exception('Operator does not exist in store')
        else:
            del self._operators[operator.id]

    def get(self, id):
        """ Retrieves a operator from the store by its ID or name. """
        cursor = self._conn.cursor()
        query = 'SELECT first_name, family_name, licence, rescue, operations, id FROM Operator WHERE ID = %s'
        cursor.execute(query, (id, ))
        drone_operator = cursor.fetchone()
        cursor.close()
        return drone_operator

    def list_all(self):
        """ Lists all the drones in the system. """
        cursor = self._conn.cursor()
        
        query = 'SELECT op.FIRST_NAME, op.FAMILY_NAME, op.licence, op.rescue, op.operations, op.droneid, dr.name, op.ID FROM Operator op LEFT JOIN Drone dr ON op.droneid = dr.ID ORDER BY op.first_name'
 
        cursor.execute(query)
        for (first_name, family_name, class_type, rescue, operations, drone, drone_name, id) in cursor:
            rescue = 'Yes' if rescue else 'No'
            class_type = 'One' if class_type == 1 else 'Two'
            operations = 0 if not operations else operations
            drone = None if not drone else drone
            drone_name = '<None>' if not drone else drone_name
            operator = Operator(first_name, family_name, class_type, rescue, operations, drone, drone_name, id)
            yield operator
        cursor.close()

    def save(self, operator):
        """ Saves the store to the database. """
        cursor = self._conn.cursor()
        query = 'UPDATE Operator SET First_Name = %s, Family_name = %s, licence = %s, Rescue = %s, Operations = %s WHERE id = %s'
        cursor.execute(query, (operator[0], operator[1], operator[2], operator[3], operator[4], operator[5]))
        self._conn.commit()
        cursor.close()
