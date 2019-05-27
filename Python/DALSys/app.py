

import mysql.connector
import Tkinter as tk
import ttk

from drones import Drone, DroneStore
from operators import Operator, OperatorStore
from maps import Map, MapStore
from trackingsystem import TrackingSystem


class Application(object):
    """ Main application view - displays the menu. """

    def __init__(self, conn):
        # Initialise the stores
        self.drones = DroneStore(conn)
        self.operators = OperatorStore(conn)
        self.maps = MapStore(conn)
        self.tracking = TrackingSystem

        # Initialise the GUI window
        self.root = tk.Tk()
        self.root.title('Drone Allocation and Localisation')
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        # Add in the buttons
        drone_button = tk.Button(
            frame, text="View Drones", command=self.view_drones, width=40, padx=5, pady=5)
        drone_button.pack(side=tk.TOP)
        operator_button = tk.Button(
            frame, text="View Operators", command=self.view_operators, width=40, padx=5, pady=5)
        operator_button.pack(side=tk.TOP)
        map_button = tk.Button(
            frame, text="View Map", command=self.view_map, width=40, padx=5, pady=5)
        map_button.pack(side=tk.TOP)
        allocate_button = tk.Button(
            frame, text="Allocate Drone", command=self.allocate_drone, width=40, padx=5, pady=5)
        allocate_button.pack(side=tk.TOP)
        exit_button = tk.Button(frame, text="Exit System",
                                command=quit, width=40, padx=5, pady=5)
        exit_button.pack(side=tk.TOP)

    def main_loop(self):
        """ Main execution loop - start Tkinter. """
        self.root.mainloop()

    def allocate_drone(self):
        wnd = AllocateWindow(self, self.drones, self.operators)
        self.root.wait_window(wnd.root)

    def view_operators(self):
        """ Display the operators. """
        # Instantiate the operators window
        # Display the window and wait
        wnd = OperatorListWindow(self)
        self.root.wait_window(wnd.root)

    def view_drones(self):
        """ Display the drones. """
        wnd = DroneListWindow(self)
        self.root.wait_window(wnd.root)

    def view_map(self):
        """ Display the maps. """
        wnd = MapListWindow(self)
        self.root.wait_window(wnd.root)


class MapListWindow(object):
    """ Base list window. """

    def __init__(self, parent):
        # Add a variable to hold the stores
        self.drones = parent.drones
        self.operators = parent.operators
        self.maps = parent.maps
        self.tracking = parent.tracking

        # Initialise the new top-level window (modal dialog)
        self._parent = parent.root
        self.root = tk.Toplevel(parent.root)
        self.root.title("Map Viewer")
        self.root.transient(parent.root)
        self.root.grab_set()

        # Initialise the top level frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH,
                        expand=tk.Y, padx=10, pady=10)

        #Maps
        tk.Label(self.frame, text='Map:', width=5, anchor="w").grid(row=0, column=0)
        self.maps_box = ttk.Combobox(self.frame, state = "readonly", width=100)
        self.maps_box.grid(row = 0, column = 1, pady=10)
        self.populate_data()
        self.maps_box.current(0)
        self.current_map = self.maps.get(self.maps_box.get())
        self.maps_box.bind("<<ComboboxSelected>>", self.update_map)

        self.canvas = tk.Canvas(master=self.frame, width = 1000, height = 500)
        #self.photo = tk.PhotoImage(file="map_abel_tasman_3.gif")
        self.photo = tk.PhotoImage(file=self.current_map[2])
        self.map_width = self.photo.width()
        self.map_height = self.photo.height()
        self.map_image = self.canvas.create_image(0,0, anchor="nw", image=self.photo)
        self.get_drones()

        self.xscrollbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.xscrollbar.config(command=self.canvas.xview)
        self.yscrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.yscrollbar.config(command=self.canvas.yview)
        self.xscrollbar.grid(row=2, columnspan = 2, sticky="EW")
        self.yscrollbar.grid(row=1, column = 2, sticky="NS")

        self.canvas.config(xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)
        self.canvas.grid(row = 1, columnspan = 2, padx = 10, pady = 10)

        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        add_button = tk.Button(self.frame, text="Update",
                               command=self.get_drones, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=3, column=1, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=4, column=1, sticky=tk.E)

    def populate_data(self):
        values = []
        for maps in self.maps.list_all():
            values.append(maps.name)
        self.maps_box['values'] = values

    def update_map(self, event):
        self.current_map = self.maps.get(self.maps_box.get())
        #print self.current_map
        self.photo = tk.PhotoImage(file=self.current_map[2])
        self.map_width = self.photo.width()
        self.map_height = self.photo.height()
        self.canvas.itemconfigure(self.map_image, image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.get_drones()

    def get_drones(self):
        drone_list = []
        self.canvas.delete("drone")
        map_x = self.map_width // 100
        map_y = self.map_height // 100
        #self.map_width = photo.width()
        #self.map_height = photo.height()
        for drone in self.drones.list_all():
            drone_list.append(drone)
        for drone in drone_list:
            if drone.map_name == self.current_map[1]:
                location = self.tracking().retrieve(drone.map_name, drone.id)
                if location.is_valid():
                    loc = location.position()
                    #print loc
                    drone_type = 'blue' if drone.rescue == 'Yes' else 'red'
                    self.canvas.create_oval((loc[0] * map_x), (loc[1] * map_y), (loc[0] * map_x)+20, (loc[1] * map_y)+20, fill=drone_type, tag='drone')

    def close(self):
        """ Closes the list window. """
        self.root.destroy()

class ListWindow(object):
    """ Base list window. """

    def __init__(self, parent, title):
        # Add a variable to hold the stores
        self.drones = parent.drones
        self.operators = parent.operators
        self.tracking = parent.tracking

        # Initialise the new top-level window (modal dialog)
        self._parent = parent.root
        self.root = tk.Toplevel(parent.root)
        self.root.title(title)
        self.root.transient(parent.root)
        self.root.grab_set()

        # Initialise the top level frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH,
                        expand=tk.Y, padx=10, pady=10)

    def add_list(self, columns, edit_action):
        # Add the list
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col.title())
        ysb = ttk.Scrollbar(self.frame, orient=tk.VERTICAL,
                            command=self.tree.yview)
        xsb = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL,
                            command=self.tree.xview)
        self.tree['yscroll'] = ysb.set
        self.tree['xscroll'] = xsb.set
        self.tree.bind("<Double-1>", edit_action)

        # Add tree and scrollbars to frame
        self.tree.grid(in_=self.frame, row=0, column=0, sticky=tk.NSEW)
        ysb.grid(in_=self.frame, row=0, column=1, sticky=tk.NS)
        xsb.grid(in_=self.frame, row=1, column=0, sticky=tk.EW)

        # Set frame resize priorities
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

    def close(self):
        """ Closes the list window. """
        self.root.destroy()


class DroneListWindow(ListWindow):
    """ Window to display a list of drones. """

    def __init__(self, parent):
        super(DroneListWindow, self).__init__(parent, 'Drones')

        # Add the list and fill it with data
        columns = ('id', 'name', 'class', 'rescue', 'operator')
        self.add_list(columns, self.edit_drone)
        self.populate_data()

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Add Drone",
                               command=self.add_drone, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=2, column=0, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=3, column=0, sticky=tk.E)

    def populate_data(self):
        """ Populates the data in the view. """
        # The following is a dummy record - need to remove and replace with data from the store
        self.tree.delete(*self.tree.get_children())
        for drone in self.drones.list_all():
            self.tree.insert('', 'end', values=(drone.id, drone.name, drone.class_type, drone.rescue, drone.operator))

    def add_drone(self):
        """ Starts a new drone and displays it in the list. """
        # Start a new drone instance
        drone = None

        # Display the drone
        self.view_drone(drone, self._save_new_drone)

    def _save_new_drone(self, drone):
        """ Saves the drone in the store and updates the list. """
        self.drones.add(drone)
        self.populate_data()

    def edit_drone(self, event):
        """ Retrieves the drone and shows it in the editor. """
        # Retrieve the identifer of the drone
        item = self.tree.item(self.tree.focus())
        item_id = item['values'][0]

        # Load the drone from the store
        #print 'TODO: Load drone with ID %04d' % (item_id)
        drone = self.drones.get(item_id)
        location = self.tracking().retrieve(drone[5], drone[0])
        #print location

        # Display the drone
        self.view_drone(drone, self._update_drone, location)

    def _update_drone(self, drone):
        """ Saves the new details of the drone. """
        self.drones.save(drone)
        self.populate_data()

    def view_drone(self, drone, save_action, location=None):
        """ Displays the drone editor. """
        wnd = DroneEditorWindow(self, drone, save_action, location)
        self.root.wait_window(wnd.root)

class OperatorListWindow(ListWindow):
    """ Window to display a list of operators. """

    def __init__(self, parent):
        super(OperatorListWindow, self).__init__(parent, 'Operators')

        # Add the list and fill it with data
        columns = ('Name', 'Class', 'Rescue', 'Operations', 'Drone')
        self.add_list(columns, self.edit_operator)
        self.populate_data()

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Add Operator",
                               command=self.add_operator, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=2, column=0, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=3, column=0, sticky=tk.E)

    def populate_data(self):
        """ Populates the data in the view. """
        self.tree.delete(*self.tree.get_children())
        for operator in self.operators.list_all():
            name = operator.first_name + ' ' + operator.family_name if operator.family_name else operator.first_name
            drone = str(operator.drone) + ': ' + operator.drone_name if operator.drone else operator.drone_name
            self.tree.insert('', 'end', values=(name, operator.drone_license, operator.rescue_endorsement, operator.operations, drone, operator.id))

    def add_operator(self):
        """ Starts a new operator and displays it in the list. """
        # Start a new operator instance
        operator = None

        # Display the operator
        self.view_operator(operator, self._save_new_operator)

    def _save_new_operator(self, operator):
        """ Saves the drone in the store and updates the list. """
        self.operators.add(operator)
        self.populate_data()

    def edit_operator(self, event):
        """ Retrieves the operator and shows it in the editor. """
        # Retrieve the identifer of the operator
        item = self.tree.item(self.tree.focus())
        item_id = item['values'][5]

        # Load the operator from the store
        #print 'TODO: Load operator with ID %04d' % (item_id)
        operator = self.operators.get(item_id)

        # Display the drone
        self.view_operator(operator, self._update_operator)

    def _update_operator(self, operator):
        """ Saves the new details of the operator. """
        self.operators.save(operator)
        self.populate_data()

    def view_operator(self, operator, save_action):
        """ Displays the drone editor. """
        wnd = OperatorEditorWindow(self, operator, save_action)
        self.root.wait_window(wnd.root)


class EditorWindow(object):
    """ Base editor window. """

    def __init__(self, parent, title, save_action, drone=None, operator=None):
        # Initialise the new top-level window (modal dialog)
        self._drone_1 = drone
        self._operator_1 = operator
        self._parent = parent.root
        self.root = tk.Toplevel(parent.root)
        self.root.title(title)
        self.root.transient(parent.root)
        self.root.grab_set()

        #Drone variables
        self.name_text = tk.StringVar()
        self.class_value = tk.StringVar()
        self.rescue_value = tk.StringVar()
        self.location_value = tk.StringVar()
        
        #Operator variables
        self.first_name_text = tk.StringVar()
        self.family_name_text = tk.StringVar()
        self.operator_rescue_value = tk.StringVar()
        self.operator_licence_value = tk.StringVar()
        self.operator_operations_value = tk.StringVar()

        # Initialise the top level frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH,
                        expand=tk.Y, padx=10, pady=10)

        # Add the editor widgets
        last_row = self.add_editor_widgets()

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Save",
                               command=save_action, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=last_row + 1, column=1, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=last_row + 2, column=1, sticky=tk.E)

    def add_editor_widgets(self):
        """ Adds the editor widgets to the frame - this needs to be overriden in inherited classes. 
        This function should return the row number of the last row added - EditorWindow uses this
        to correctly display the buttons. """
        return -1

    def class_selected(self, event):
        print self.class_value.get()

    def rescue_selected(self, event):
        print self.rescue_value.get()

    def close(self):
        """ Closes the editor window. """
        self.root.destroy()

class AllocateWindow(EditorWindow):
    """ Editor window for drones. """

    def __init__(self, parent, dronestore, operatorstore):
        self.root = tk.Toplevel(parent.root)
        self.root.title('Allocate Drone')
        self.root.transient(parent.root)
        self.root.grab_set()

        self.drone_store = dronestore
        self.operator_store = operatorstore
        self.drone_value = tk.StringVar()
        self.operator_value = tk.StringVar()
        self.drone_list = []
        self.operator_list = []
        self.checked = False
        #super(AllocateWindow, self).__init__(parent, 'Allocate Drone', None)
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH,
                        expand=tk.Y, padx=10, pady=10)

        self.add_editor_widgets()

    def add_editor_widgets(self):
        #Drones
        tk.Label(self.frame, text='Drone:', width=15, anchor="w", pady=10).grid(row=0, column=0, sticky='w')
        self.drone_box = ttk.Combobox(self.frame, state = "readonly", width=75, textvariable=self.drone_value)
        self.drone_box.grid(row = 0, column = 0, columnspan = 2, sticky = "e", pady=10)
        self.drone_box.bind("<<ComboboxSelected>>", self.uncheck)
        #Operator
        tk.Label(self.frame, text='Operator:', width=15, anchor="w", pady=10).grid(row=1, column=0, sticky='w')
        self.operator_box = ttk.Combobox(self.frame, state = "readonly", width=75, textvariable=self.operator_value)
        self.operator_box.grid(row = 1, column = 0, columnspan=2, sticky = "e", pady=10)
        self.operator_box.bind("<<ComboboxSelected>>", self.uncheck)
        #Check Area
        self.check_box = tk.Text(self.frame, height=6, width=50, wrap=tk.WORD)
        self.check_box.grid(row = 2, rowspan = 3, column = 0, sticky = 'w', padx=5, pady=10)
        self.check_box.insert('1.0', "Error Messages\n")
        #Check button
        check_button = tk.Button(self.frame, text="Check",
                               command=self.check_allocation, width=20, padx=5, pady=5)
        check_button.grid(in_=self.frame, row=2, column=1, sticky=tk.E)
        #Allocate button
        allocate_button = tk.Button(self.frame, text="Allocate",
                               command=self.allocate_drone_operator, width=20, padx=5, pady=5)
        allocate_button.grid(in_=self.frame, row=3, column=1, sticky=tk.E)
        #Cancel Button
        cancel_button = tk.Button(self.frame, text="Cancel",
                               command=self.allocate_cancel, width=20, padx=5, pady=5)
        cancel_button.grid(in_=self.frame, row=4, column=1, sticky=tk.E)

        drone_name_values = []
        self.drone_list = self.populate_drones()
        for drone_name in self.drone_list:
            drone_name_values.append(drone_name.name)
        self.drone_box['values'] = drone_name_values    
        self.drone_box.current(0)

        op_name_values = []
        self.operator_list = self.populate_operators()
        for operator_name in self.operator_list:
            op_name_values.append(operator_name.first_name + " " + operator_name.family_name)
        self.operator_box['values'] = op_name_values
        self.operator_box.current(0)

    def check_allocation(self):
        self.checked = True
        self.check_box.delete('1.0', tk.END)
        error_messages = ["Error Messages\n"]
        operator = self.operator_list[self.operator_box.current()]
        op_name = operator.first_name + " " + operator.family_name
        drone = self.drone_store.get(self.drone_list[self.drone_box.current()].id)
        if operator.drone and operator.drone != drone[0]:
            error_messages.append("%s already operates another drone\n" % (op_name))
        if operator.drone_license == 'One' and drone[2] == 2:
            error_messages.append("%s does not have high enough licence to operate %s\n" % (op_name, drone[1]))
        if operator.rescue_endorsement != 'Yes' and drone[3] == 1:
            error_messages.append("%s does not have rescue endorsement\n" % (op_name))
        if drone[4]:
            if drone[4] == operator.id:
                error_messages = ["Error Messages\n", ("%s already operates %s\n" % (op_name, drone[1]))]
            else:
                error_messages.append("%s already allocated to another operator\n" % (drone[1]))
        msg_line = 2.0
        for message in error_messages:
            #print msg_line
            self.check_box.insert(msg_line, message)
            msg_line += 1.0

    def uncheck(self, event):
        self.checked = False

    def allocate_drone_operator(self):
        if self.checked:
            operator = self.operator_list[self.operator_box.current()]
            drone = self.drone_store.get(self.drone_list[self.drone_box.current()].id)
            #update drone first then op
            self.drone_store.allocate(drone[0], operator.id)
            self.check_box.delete('1.0', tk.END)
            self.check_box.insert(1.0, "Allocation Successful\n")
        else:
            self.check_box.delete('1.0', tk.END)
            self.check_box.insert(1.0, "Error Messages\n")
            self.check_box.insert(2.0, "Check Allocation before Allocating!\n")

    def allocate_cancel(self):
        """ Closes the editor window. """
        self.root.destroy()

    def populate_drones(self):
        drone_list = []
        for drone in self.drone_store.list_all():
            drone_list.append(drone)
        return drone_list

    def populate_operators(self):
        op_list = []
        for op in self.operator_store.list_all():
            op_list.append(op)
        return op_list
        
       
class DroneEditorWindow(EditorWindow):
    """ Editor window for drones. """

    def __init__(self, parent, drone, save_action, location=None):
        # TODO: Add either the drone name or <new> in the window title, depending on whether this is a new
        # drone or not
        self._location = location
        super(DroneEditorWindow, self).__init__(parent, 'Drone: <new>', self.save_drone, drone)
        self._drone = drone
        self._save_action = save_action

    def add_editor_widgets(self):
        """ Adds the widgets dor editing a drone. """
        #Name
        tk.Label(self.frame, text='Name:', width=15, anchor="w", pady=10).grid(row=0, column=0)
        name = tk.Entry(self.frame, width=30, textvariable=self.name_text)
        name.grid(row = 0, column = 1)
        #Class
        tk.Label(self.frame, text='Drone Class:', width=15, anchor="w").grid(row=1, column=0)
        class_box = ttk.Combobox(self.frame, values = ('One', 'Two'), state = "readonly", width=7, textvariable=self.class_value)
        class_box.grid(row = 1, column = 1, sticky = "w", pady=10)
        class_box.current(0)
        #Rescue
        tk.Label(self.frame, text='Rescue Drone:', width=15, anchor="w").grid(row=2, column=0)
        rescue_box = ttk.Combobox(self.frame, values = ('Yes', 'No'), state = "readonly", width=7, textvariable=self.rescue_value)
        rescue_box.grid(row = 2, column = 1, sticky = "w", pady=10)
        rescue_box.current(1)
        #Location
        tk.Label(self.frame, text='Location:', width=15, anchor="w").grid(row=3, column=0)
        location = tk.Entry(self.frame, width=30, textvariable=self.location_value, state= "readonly")
        location.grid(row = 3, column = 1, sticky = "w", pady=10)
        self.location_value.set("n/a")
        
        #Check is new or editing drone
        if self._drone_1 != None:
            if self._location.is_valid():
                coords = self._location.position()
                xy_coords =  "(%s, %s)" % (coords[0], coords[1])
                self.location_value.set(xy_coords)
            else:
                self.location_value.set("n/a")

            self.root.title("Drone: " + self._drone_1[1])
            #name.insert(0, self._drone_1[1])
            self.name_text.set(self._drone_1[1])
            class_box.current(1) if self._drone_1[2] == 2 else class_box.current(0)
            rescue_box.current(0) if self._drone_1[3] == 1 else rescue_box.current(1)

        return 4

    def save_drone(self):
        """ Updates the drone details and calls the save action. """
        self.root.title("Drone: " + self.name_text.get())
        class_num = 1 if self.class_value.get() == 'One' else 2
        rescue_num = 0 if self.rescue_value.get() == "No" else 1
        #If editing drone
        if self._drone != None:
            self._drone = self._drone[0], self.name_text.get(), class_num, rescue_num, self._drone[4]
        else:
            self._drone = 0, self.name_text.get(), class_num, rescue_num, 0
            self.close()
        self._save_action(self._drone)

class OperatorEditorWindow(EditorWindow):
    """ Editor window for drones. """

    def __init__(self, parent, operator, save_action):
        # TODO: Add either the operator name or <new> in the window title, depending on whether this is a new
        # operator or not
        super(OperatorEditorWindow, self).__init__(parent, 'Operator: <new>', self.save_operator, None, operator)
        self._operator = operator
        self._save_action = save_action

    def add_editor_widgets(self):
        """ Adds the widgets dor editing a operator. """
        #First Name
        tk.Label(self.frame, text='First Name:', width=20, anchor="w", pady=10).grid(row=0, column=0)
        name = tk.Entry(self.frame, width=30, textvariable=self.first_name_text)
        name.grid(row = 0, column = 1)
        #Last Name
        tk.Label(self.frame, text='Family Name:', width=20, anchor="w", pady=10).grid(row=1, column=0)
        name = tk.Entry(self.frame, width=30, textvariable=self.family_name_text)
        name.grid(row = 1, column = 1)
        #Licence
        tk.Label(self.frame, text='Drone Licence:', width=20, anchor="w").grid(row=2, column=0)
        class_box = ttk.Combobox(self.frame, values = ('One', 'Two'), state = "readonly", width=7, textvariable=self.operator_licence_value)
        class_box.grid(row = 2, column = 1, pady=10)
        class_box.current(0)
        #Rescue
        tk.Label(self.frame, text='Rescue Endorsement:', width=20, anchor="w", pady=10).grid(row=3, column=0)
        name = tk.Entry(self.frame, width=10, textvariable=self.operator_rescue_value, state= "readonly")
        name.grid(row = 3, column = 1)
        self.operator_rescue_value.set("No")
        #Operations max of 99999
        tk.Label(self.frame, text='Number of Operations:', width=20, anchor="w").grid(row=4, column=0)
        operations_box = tk.Spinbox(self.frame, from_=0, to=99999, width=7, textvariable=self.operator_operations_value)
        operations_box.grid(row = 4, column = 1, pady=10)

        #If editing operator
        if self._operator_1 != None:
            #print self._operator_1
            name = self._operator_1[0] + ' ' + self._operator_1[1] if self._operator_1[1] else self._operator_1[0]
            self.root.title("Operator: " + name)
            self.first_name_text.set(self._operator_1[0])
            self.family_name_text.set(self._operator_1[1])
            class_box.current(1) if self._operator_1[2] == 2 else class_box.current(0)
            self.operator_rescue_value.set("Yes") if self._operator_1[3] == 1 else self.operator_rescue_value.set("No")
            self.operator_operations_value.set(0) if not self._operator_1[4] else self.operator_operations_value.set(self._operator_1[4])
       
        return 4

    def save_operator(self):
        """ Updates the operator details and calls the save action. """
        op_name = self.first_name_text.get() + ' ' + self.family_name_text.get()
        self.root.title("Operator: " + op_name)
        class_num = 1 if self.operator_licence_value.get() == 'One' else 2
        #rescue_num = 0 if self.operator_rescue_value.get() == "No" else 1
        rescue_num = 1 if int(self.operator_operations_value.get()) >= 5 else 0
        self.operator_rescue_value.set("Yes") if rescue_num else self.operator_rescue_value.set("No")
        if int(self.operator_operations_value.get()) < 0:
            self.operator_operations_value.set(0)
        #operations = 0 if int(self.operator_operations_value.get()) < 0 else self.operator_operations_value.get()
        #first_name = self.first_name_text.get()
        #family_name = self.family_name_text.get()

        #If editing operator
        if self._operator != None:
            self._operator = self.first_name_text.get(), self.family_name_text.get(), class_num, rescue_num, self.operator_operations_value.get(), self._operator[5]
        else:
            self._operator = self.first_name_text.get(), self.family_name_text.get(), class_num, rescue_num, self.operator_operations_value.get(), 0
            self.close()
        self._save_action(self._operator)


if __name__ == '__main__':
    conn = mysql.connector.connect(user='user',
                                   password='password',
                                   host='127.0.0.1',
                                   database='dalsys')
    app = Application(conn)
    app.main_loop()
    conn.close()
