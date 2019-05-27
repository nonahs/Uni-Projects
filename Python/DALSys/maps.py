
class Map(object):
    """ Stores details on a map. """

    def __init__(self, id, name, filepath):
        self.id = id
        self.name = name
        self.filepath = filepath


class MapStore(object):
    """ MapStore stores all the maps for DALSys. """

    def __init__(self, conn=None):
        self._maps = {}
        self._conn = conn

    def add(self, map):
        """ Adds a new map to the store. """
        if map.name in self._maps:
            raise Exception('Map already exists in store')
        else:
            self._maps[map.name] = map

    def remove(self, map):
        """ Removes a map from the store. """
        if not map.name in self._maps:
            raise Exception('Map does not exist in store')
        else:
            del self._maps[map.name]

    def get(self, name):
        """ Retrieves a map from the store by its name. """
        cursor = self._conn.cursor()
        query = 'SELECT ID, Name, Filename FROM Map WHERE Name = %s'
        cursor.execute(query, (name, ))
        map_exists = cursor.fetchone()
        cursor.close()
        if map_exists is None:
            return False
        return map_exists

    def list_all(self):
        """ Lists all the maps in the store. """
        cursor = self._conn.cursor()
        query = 'SELECT ID, Name, Filename FROM Map'
        cursor.execute(query)
        for (id, name, filename) in cursor:
            map_object = Map(id, name, filename)
            yield map_object
        cursor.close()

    def save(self):
        """ Saves the store to the database. """
        pass    # TODO: we don't have a database yet
