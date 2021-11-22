from tkinter import *
import tkinter as tk
from tkinter import ttk
from datetime import date
import sqlite3
import pendulum
from tkcalendar import DateEntry

pendulum.week_starts_at(pendulum.SUNDAY)
pendulum.week_ends_at(pendulum.SATURDAY)


# checking if value sent is float or not
# returns True or False
def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


class Filter:
    def __init__(self, index, frame):
        self.index = index

        self.image = PhotoImage(file="trash.png")
        self.remove_button = ttk.Button(frame, image=self.image)
        self.remove_button.grid(row=index, column=0, pady=5, padx=5)

        self.selected_attribute = StringVar()
        self.selected_attribute.set('Select Attribute')

        self.menu_btn_attribute = ttk.Menubutton(frame, text=self.selected_attribute.get())
        self.menu_attribute = Menu(self.menu_btn_attribute, tearoff=0)
        self.menu_btn_attribute["menu"] = self.menu_attribute
        self.menu_btn_attribute.grid(row=index, column=2, pady=5)

        self.label_select_attribute = Label(frame, text="Attribute: ")
        self.label_select_attribute.grid(row=index, column=1, pady=5)

        # init menu button for select option by type
        self.selected_filter_type = None
        self.menu_btn_filter = None
        self.menu_filter = None
        self.label_select_filter = None
        self.text_input = None
        self.label_between_to = None
        self.text_input_2 = None
        self.date_entry = None
        self.date_entry_2 = None
        self.init_filter_widgets(frame)
        self.init_text_input(frame)
        self.init_date(frame)

    def init_date(self, frame):
        self.date_entry = DateEntry(frame, selectmode='day', date_pattern='dd/MM/yyyy')
        self.date_entry_2 = DateEntry(frame, selectmode='day', date_pattern='dd/MM/yyyy')

    def init_filter_widgets(self, frame):
        self.selected_filter_type = StringVar()
        self.selected_filter_type.set('Select Filter')

        self.menu_btn_filter = ttk.Menubutton(frame, text=self.selected_filter_type.get())
        self.menu_filter = Menu(self.menu_btn_filter)
        self.menu_btn_filter["menu"] = self.menu_filter

        self.label_select_filter = Label(frame, text="Filter: ")

    def init_text_input(self, frame):
        self.text_input = ttk.Entry(frame)
        self.text_input_2 = ttk.Entry(frame)
        self.label_between_to = ttk.Entry(frame)


class App:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.mycursor = self.conn.cursor()
        self.root = tk.Tk()

        # init light theme
        self.root.tk.call("source", "azure.tcl")
        self.root.tk.call("set_theme", "light")
        self.root.attributes('-topmost', True)
        self.root.geometry("800x900")
        self.root.title("208942342#312500457 Seminar Project")

        # init arrays for filters type queries
        self.filters_char = ['starts with', 'contains', 'is equal to', 'does not starts with', 'does not contain',
                             'is not equal to', 'is greater than', 'is less than', 'is less than or equal to', 'is greater than or equal to']
        self.filters_int_or_numeric = ['is equal to', 'is between', 'is less than', 'is less than or equal to',
                                       'is greater than',
                                       'is greater than or equal to',
                                       'is not equal to']
        self.filters_date = ['today', 'this week', 'last week', 'this month', 'last month', 'this year', 'last year',
                             'before', 'after', 'between']

        # dictionary for assigning label filter to the actual sign
        self.dict_attri_to_sign = {'is equal to': '= \'#\'', 'is less than': '< \'#\'', 'is less than or equal to': '<= \'#\'',
                                   'is greater than': '> \'#\'', 'is greater than or equal to': '>= \'#\'',
                                   'is between': '< \'#\' AND $ > \'#\'',
                                   'is not equal to': '!= \'#\'', 'starts with': 'LIKE \'#%\'', 'contains': 'LIKE \'%#%\'',
                                   'does not starts with': 'NOT LIKE \'#%\'', 'does not contain': 'NOT LIKE \'%#%\'',
                                   'today': '= "' + str(date.today()) + ' 00:00:00"',
                                   'this year': '>= "' + str(date.today().year) + '-01-01" AND # < "'
                                                + str(int(date.today().year) + 1) + '-01-01"',
                                   'this week': '>= "' + str(
                                       pendulum.now().subtract(days=date.today().weekday() + 1).date()) + '" AND # < "'
                                                + str(pendulum.now().date()) + '"', 'this month': '>= "' + str(
                pendulum.now().subtract(days=date.today().day - 1).date()) + '" AND # < "'
                                                                                                  + str(
                pendulum.now().date()) + '"',
                                   'last week': '>= "' + str(pendulum.now().subtract(weeks=1).date()) + '" AND # < "'
                                                + str(pendulum.now().date()) + '"',
                                   'last month': '>= "' + str(pendulum.now().subtract(months=1).date()) + '" AND # < "'
                                                 + str(pendulum.now().date()) + '"',
                                   'last year': '>= "' + str(pendulum.now().subtract(years=1).date()) + '" AND # < "'
                                                + str(pendulum.now().date()) + '"', 'before': '< ', 'after': '> ',
                                   'between': '> "^1" AND # < "^2"'}

        # init queries list that will contains all the queries that the user entered.
        self.query_filter_list = []
        self.count_query_filter = 0

        self.init_frame_header()
        # switch button for change theme (dark or light)
        self.switch = ttk.Checkbutton(self.frame_header, text="Light Mode", style="Switch.TCheckbutton",
                                      command=self.change_theme)
        self.switch.grid(row=0, column=2, padx=25)
        self.switch_is_on = False
        # init the frame for the table
        self.init_frame_table()
        # init the frame for middle section that contains add filter and submit buttons.
        self.frame_middle = Frame(self.root, height=10, width=300)

        # init the frame that contains all the filters and the query.
        self.init_frame_query()
        # init the footer frame that containt the exit and clear buttons.
        self.init_frame_footer()
        # init the frame that will contains the error label.
        self.init_error_frame()

        self.root.mainloop()

    # call to init the header frame
    # input: None
    # output: inserting to frame
    def init_frame_header(self):
        self.frame_header = Frame(self.root, height=150, width=300)
        self.frame_header.pack(pady=25, padx=50)

        self.selected_table_name = StringVar()
        self.selected_table_name.set('Select Table')
        self.mycursor.execute(
            "SELECT name "
            "FROM sqlite_master "
            "WHERE type='table';")
        # taking the tables names from the database
        self.databases_tup = tuple(x[0] for x in self.mycursor.fetchall())

        self.init_btn_labels_headers()
        # adding buttons with all the names of tables.
        for db_name in self.databases_tup:
            self.menu_select_table.add_radiobutton(
                label=db_name,
                variable=self.selected_table_name,
                value=db_name,
                command=self.init_selected_table
            )

    # call to init labels and buttons for header frame
    # input: None
    # output: inserting labels,menu and button to header frame.
    def init_btn_labels_headers(self):
        self.menu_select_table_btn = ttk.Menubutton(self.frame_header, text=self.selected_table_name.get())
        self.menu_select_table = Menu(self.menu_select_table_btn, tearoff=0)
        self.menu_select_table_btn["menu"] = self.menu_select_table
        self.label_select_table = Label(self.frame_header, text="Table: ")
        self.label_select_table.grid(row=0, column=0)
        self.menu_select_table_btn.grid(row=0, column=1)

    # call to init query frame
    # input: None
    # output: inserting frame container for canvas that contains frame for the filters
    def init_frame_query(self):
        self.frame_query_container = LabelFrame(self.root)
        self.canvas = Canvas(self.frame_query_container, scrollregion=(0, 0, 1000, 500))
        self.y_scrollbar_query_frame = ttk.Scrollbar(self.frame_query_container, orient=VERTICAL,
                                                     command=self.canvas.yview)
        self.x_scrollbar_query_frame = ttk.Scrollbar(self.frame_query_container, orient=HORIZONTAL,
                                                     command=self.canvas.xview)
        self.y_scrollbar_query_frame.pack(side=RIGHT, fill=Y)
        self.x_scrollbar_query_frame.pack(side=BOTTOM, fill=X)
        self.canvas.pack(fill=BOTH)
        self.canvas.configure(yscrollcommand=self.y_scrollbar_query_frame.set,
                              xscrollcommand=self.x_scrollbar_query_frame.set)
        self.frame_query_filters = Frame(self.canvas)
        self.frame_query_filters.pack()
        self.canvas.create_window((0, 0), anchor='nw', window=self.frame_query_filters)
        # enable scroll with mouse at all point inside the frame
        self.canvas.bind('<MouseWheel>', lambda x: self.canvas.yview_scroll(int(-1 * (x.delta / 120)), "units"))
        self.frame_query_filters.bind('<MouseWheel>',
                                      lambda x: self.canvas.yview_scroll(int(-1 * (x.delta / 120)), "units"))
        self.frame_query_container.bind('<MouseWheel>',
                                        lambda x: self.canvas.yview_scroll(int(-1 * (x.delta / 120)), "units"))

    # call to init table frame
    # input: None
    # output: inserting frame that contains tree view for the table
    def init_frame_table(self):
        self.frame_table = Frame(self.root)
        self.tree_view_table = ttk.Treeview(self.frame_table, height=7, show="headings")
        self.frame_table.configure(height=200)
        self.y_scrollbar_tree_table = Scrollbar(self.frame_table, orient=VERTICAL, command=self.tree_view_table.yview)
        self.x_scrollbar_tree_table = Scrollbar(self.frame_table, orient=HORIZONTAL, command=self.tree_view_table.xview)
        self.tree_view_table.configure(yscrollcommand=self.y_scrollbar_tree_table.set,
                                       xscrollcommand=self.x_scrollbar_tree_table.set)
        self.y_scrollbar_tree_table.pack(side=RIGHT, fill=Y)
        self.x_scrollbar_tree_table.pack(side=BOTTOM, fill=X)
        self.tree_view_table.pack(fill=X)

    # call to init footer frame
    # input: None
    # output: inserting frame that contains exit and clear buttons.
    def init_frame_footer(self):
        # init the footer frame and packing it
        self.frame_footer = Frame(self.root, height=150, width=300)
        self.frame_footer.pack(side=BOTTOM, pady=25)
        # define exit and clear buttons
        self.exit_btn = ttk.Button(self.frame_footer, text="Exit", style="Accent.TButton",
                                   command=lambda: self.root.destroy())
        self.exit_btn.grid(row=0, column=0, padx=25)
        self.clr_btn = ttk.Button(self.frame_footer, text="Clear", style="Accent.TButton", command=self.clear)
        self.clr_btn.grid(row=0, column=1, padx=25)

    # call to init the selected table
    # input: None
    # output: removing any table that was initiated before and inserting the current table to tree from the selected table.
    def init_selected_table(self):
        self.count_query_filter = 0
        self.frame_table.pack(padx=100, fill=X)
        # clearing the list each table selection
        self.query_filter_list.clear()
        # clear queries frame
        for child in self.frame_middle.winfo_children():
            child.destroy()
        for child in self.frame_query_filters.winfo_children():
            child.destroy()
        self.frame_middle.pack(pady=5, padx=50)
        self.frame_query_container.pack(pady=10, padx=10, expand=YES, fill=BOTH)
        self.mycursor.execute("PRAGMA table_info(" + self.selected_table_name.get() + ")")
        # list of tuple that contains header name and type.
        headers_type_tup = list(map(lambda x: (x[1], x[2]), self.mycursor.fetchall()))
        # list of the header's name
        headers = [x[0] for x in headers_type_tup]
        # dict of header name and type
        self.dict_headers_types = {k: v for (k, v) in headers_type_tup}
        length_headers = len(headers)
        # configure the tuple columns from headers.
        h_tuple = tuple((x + 1 for x in range(length_headers)))
        self.tree_view_table.configure(columns=h_tuple)
        # creating headers with header name
        for index, value in enumerate(headers):
            # self.insertQueries(index, value)
            self.tree_view_table.heading(index + 1, text=value, anchor='nw')
            self.tree_view_table.column(index + 1, stretch=YES, width=250)
        # define add button for adding new query
        add_query_btn = ttk.Button(self.frame_middle, text="Add Filter", command=self.add_filter)
        add_query_btn.grid(row=0, column=0, padx=10, pady=15)
        # define submit button for the current query
        submit_btn = ttk.Button(self.frame_middle, text="Submit", command=self.submit)
        submit_btn.grid(row=0, column=1, padx=10, pady=15)

        self.execute_selected_table(length_headers)
        self.menu_select_table_btn.configure(text=self.selected_table_name.get())

    # call to add new filter after the user pressed the button
    # input: None
    # output: inserting new filter 'row' that contains attribute menu and appending new filter to the list of filters.
    def add_filter(self):

        # new filter object that contain a menu for attribute and menu for the right filter menu by the attribute type.
        new_filter = Filter(self.count_query_filter, self.frame_query_filters)
        self.count_query_filter += 1
        new_filter.remove_button.configure(command=lambda: self.remove_filter(new_filter))

        for header_name, header_type in self.dict_headers_types.items():
            new_filter.menu_attribute.add_radiobutton(
                label=header_name,
                variable=new_filter.selected_attribute,
                value=header_name,
                command=lambda: self.init_filter(new_filter)
            )

        # array of all filters
        self.query_filter_list.append(new_filter)
        self.error_msg("")

    # call to initialize the menu filter
    # input: the selected filter
    # output: inserting the relevant menu list by the type
    def init_filter(self, filter):
        # each time the user select query attribute, the recent filter will be removed and a new one will be added.
        filter.label_select_filter.grid_forget()
        filter.menu_btn_filter.grid_forget()
        filter.text_input.grid_forget()
        filter.label_between_to.grid_forget()
        filter.text_input_2.grid_forget()

        filter.init_filter_widgets(self.frame_query_filters)

        filter.menu_btn_attribute.configure(text=filter.selected_attribute.get())

        # adding label and menu filter for the selected query attribute
        filter.label_select_filter.grid(row=filter.index, column=3, pady=5)
        filter.menu_btn_filter.grid(row=filter.index, column=4, pady=5)

        header_type = self.dict_headers_types[filter.selected_attribute.get()]

        # each condition is responsible for taking the relevant dictionary of filters by the filter type.
        if 'CHAR' in header_type:
            for label in self.filters_char:
                filter.menu_filter.add_radiobutton(
                    label=label,
                    variable=filter.selected_filter_type,
                    value=label,
                    command=lambda: self.init_filter_input(filter)
                )
            return
        if 'DATETIME' in header_type:
            for label in self.filters_date:
                filter.menu_filter.add_radiobutton(
                    label=label,
                    variable=filter.selected_filter_type,
                    value=label,
                    command=lambda: self.init_filter_date(filter)
                )
            return
        elif 'INTEGER' or 'NUMERIC' in header_type:
            for label in self.filters_int_or_numeric:
                filter.menu_filter.add_radiobutton(
                    label=label,
                    variable=filter.selected_filter_type,
                    value=label,
                    command=lambda: self.init_filter_input(filter)
                )

    # call to initialize all relevant inputs for the current filter
    # input: the selected filter
    # output: removing previous inputs and inserting to frame the new inputs fields.
    def init_filter_input(self, filter):
        # each time we select a filter we need to remove the last inputs by the type and initializing them again
        filter.text_input.grid_forget()
        filter.label_between_to.grid_forget()
        filter.text_input_2.grid_forget()
        filter.date_entry.grid_forget()
        filter.date_entry_2.grid_forget()

        selected_filter = filter.selected_filter_type.get()
        filter.menu_btn_filter.configure(text=selected_filter)
        filter.init_text_input(self.frame_query_filters)
        filter.text_input.grid(row=filter.index, column=5, pady=10, padx=10)
        if selected_filter in ('is between', 'is not between'):
            filter.label_between_to = ttk.Label(self.frame_query_filters, text='to')
            filter.label_between_to.grid(row=filter.index, column=6, pady=10, padx=5)
            filter.text_input_2.grid(row=filter.index, column=7, pady=10, padx=10)

    # call to clear all relevant frames, filters and queries
    # input: None
    # output: None
    def clear(self):
        for x in self.tree_view_table.get_children():
            self.tree_view_table.delete(x)
        self.tree_view_table.configure(columns=())
        self.frame_table.pack_forget()
        self.query_filter_list.clear()
        self.frame_middle.pack_forget()
        self.frame_query_container.pack_forget()
        self.selected_table_name.set('Select Table')
        self.count_query_filter = 0
        self.menu_select_table_btn.configure(text=self.selected_table_name.get())
        self.error_msg("")

    # call to submit the input by the user
    # input: string
    # output: None
    def submit(self):
        # if there is no filters added a message will appear to the user
        if len(self.query_filter_list) == 0:
            self.error_msg("No Filters Added. Please add at least one filter")
            return
        self.label_error.configure(text='')
        # init a query from the selected table
        queryText = "SELECT * FROM " + self.selected_table_name.get() + " \nWHERE "
        for index, query in enumerate(self.query_filter_list):
            # checking if the user select an attribute, if he didnt, a msg will appear to the user.
            if query.selected_attribute.get() == 'Select Attribute':
                self.error_msg("Attribute " + str(index + 1) + " Not Selected")
                return
            if query.selected_filter_type.get() == 'Select Filter':
                self.error_msg("Filter " + str(index + 1) + " Not Selected")
                return
            # taking the input type (INT, DATE, CHAR..)
            type = self.dict_headers_types[query.selected_attribute.get()]
            # checking the input by the matched type
            if not self.check_input(type, query, index):
                return
            queryText += query.selected_attribute.get() + " "
            # if the user choose between option we need to take both of the inputs from the user
            if query.selected_filter_type.get() == 'is between':
                queryText += "between " + \
                             query.text_input.get().replace(" ", "") + " AND " + query.text_input_2.get().replace(" ",
                                                                                                                  "")
            else:
                # assign the right sign from the selected filter type ( example: is equal --> ==)
                queryText += self.dict_attri_to_sign[query.selected_filter_type.get()]
            if 'DATETIME' in type:
                # if the selected filter option is before or after we need to take the date as is.
                if query.selected_filter_type.get() in ('before', 'after'):
                    queryText += '"' + str(query.date_entry.get_date()) + '"'
                # if its between, we need to make the query for example: Date > date1 AND Date < date2
                elif query.selected_filter_type.get() in 'between':
                    queryText = queryText.replace('#', str(query.selected_attribute.get()), 2)
                    queryText = queryText.replace('^2', str(query.date_entry_2.get_date()), 2)
                    queryText = queryText.replace('^1', str(query.date_entry.get_date()), 2)
                # if the user chose any other other option we need to replace only the hashtags.
                else:
                    queryText = queryText.replace('#', str(query.selected_attribute.get()), 2)
            elif 'CHAR' in type:
                # if the user didnt insert any input the default will be Null
                if len(query.text_input.get().replace(" ", "")) == 0:
                    queryText = queryText.replace('#', 'NULL')
                    queryText = queryText.replace('!=', 'is NOT')
                    queryText = queryText.replace('=', 'is')
                    queryText = queryText.replace('\'', '')
                queryText = queryText.replace('#', str(query.text_input.get().strip()))
            else:
                queryText = queryText.replace('#', str(query.text_input.get().replace(" ", "")))
            # adding AND between each row from the filters to make the query legit
            if (index + 1) < len(self.query_filter_list) and len(self.query_filter_list) > 1:
                queryText += '\nAND '
        queryText += ";"
        print(queryText)
        # executing the query
        self.data_query(len(self.dict_headers_types), queryText)

    # initialize the query from the input
    # input: length of the dictionary of headers names and the query from user
    # output: executing the table by the query input
    def data_query(self, headers_length, input_query):
        for x in self.tree_view_table.get_children():
            self.tree_view_table.delete(x)
        self.mycursor.execute(input_query)
        for row in self.mycursor:
            self.tree_view_table.insert('', 'end', values=row[0:headers_length])

    # initialize the table by the user choice
    # input: length of the dictionary of headers names
    # output: executing and showing the right table by the user choice
    def execute_selected_table(self, headers_length):
        for x in self.tree_view_table.get_children():
            self.tree_view_table.delete(x)
        self.mycursor.execute("SELECT *  FROM " + self.selected_table_name.get())
        for row in self.mycursor:
            self.tree_view_table.insert('', 'end', values=row[0:headers_length])

    def init_filter_date(self, query):
        """
        :param query: initialize the date picker
        :param input: the query data
        :return: None
        """
        query.text_input.grid_forget()
        query.label_between_to.grid_forget()
        query.text_input_2.grid_forget()
        query.date_entry.grid_forget()
        query.date_entry_2.grid_forget()

        selected_filter = query.selected_filter_type.get()
        query.menu_btn_filter.configure(text=selected_filter)
        # if the user chose the between option we need to add another input and label.
        if selected_filter in 'between':
            query.init_date(self.frame_query_filters)
            query.date_entry.grid(row=query.index, column=5, pady=10, padx=10)
            query.label_between_to = ttk.Label(self.frame_query_filters, text='to')
            query.label_between_to.grid(row=query.index, column=6, pady=10, padx=5)
            query.date_entry_2.grid(row=query.index, column=7, pady=10, padx=10)
        if selected_filter in ('before', 'after'):
            query.init_date(self.frame_query_filters)
            query.date_entry.grid(row=query.index, column=5, pady=10, padx=10)

    # removes filter line
    # input: query data
    # output: None
    def remove_filter(self, query):
        self.query_filter_list.remove(query)
        query.label_select_attribute.grid_forget()
        query.label_select_filter.grid_forget()
        query.menu_btn_attribute.grid_forget()
        query.menu_btn_filter.grid_forget()
        query.remove_button.grid_forget()
        query.text_input.grid_forget()
        query.text_input_2.grid_forget()
        query.date_entry.grid_forget()
        query.date_entry_2.grid_forget()
        query.label_between_to.grid_forget()
        if len(self.query_filter_list) == 0:
            self.init_selected_table()
        else:
            self.submit()

    # checking if the input we get is correct
    # getting type of input, the query data to get input, and index of the filter
    # returns True for bad input, False for good input
    def check_input(self, type, filter, index):
        if 'DATETIME' in type:
            return self.check_input_date(filter, index)
        if 'INTEGER' in type:
            return self.check_input_int(filter, index)
        if 'NUMERIC' in type:
            return self.check_input_numeric(filter, index)
        if 'CHAR' in type and filter.selected_filter_type.get() != 'is equal to' and filter.selected_filter_type.get() != 'is not equal to':
            input_char = filter.text_input.get().replace(" ", "")
            if len(input_char) == 0:
                self.error_msg("Please enter input for filter " + str(index + 1))
                return False
        return True

    # call to check input integer
    # input: query and query index in queries list
    # output: false\true depends on input
    def check_input_int(self, filter, index):
        input_int = filter.text_input.get().replace(" ", "")
        input_int_2 = filter.text_input_2.get().replace(" ", "")
        if len(input_int) == 0:
            self.error_msg("Please enter input for filter " + str(index + 1))
            return False
        if not input_int.isdigit():
            self.error_msg("Please enter numbers only in filter " + str(index + 1))
            return False
        if filter.selected_filter_type.get() in ('is between', 'is not between'):
            if len(input_int_2) == 0:
                self.error_msg("Please enter input for filter " + str(index + 1))
                return False
            if not input_int_2.isdigit():
                self.error_msg("Please enter numbers only in filter " + str(index + 1))
                return False
        print("here")
        return True

    # call to check input date
    # input: query and query index in queries list
    # output: false\true depends on input
    def check_input_date(self, filter, index):
        if filter.date_entry.get_date() > date.today():
            self.error_msg("Wrong Date in filter number " + str(index + 1))
            return False
        if filter.selected_filter_type.get() in 'between':
            if filter.date_entry.get_date() > date.today() or filter.date_entry_2.get_date() > date.today() \
                    or filter.date_entry.get_date() > filter.date_entry_2.get_date():
                self.error_msg("Invalid date in filter " + str(index + 1))
                return False
        return True

    # call to check input numeric
    # input: query and query index in queries list
    # output: false\true depends on input
    def check_input_numeric(self, filter, index):
        input_numeric = filter.text_input.get().replace(" ", "")
        input_numeric_2 = filter.text_input_2.get().replace(" ", "")
        if len(input_numeric) == 0:
            self.error_msg("no input in filter " + str(index + 1))
            return False
        if not is_float(input_numeric):
            self.error_msg("Only numbers or float allowed in filter " + str(index + 1))
            return False
        if filter.selected_filter_type.get() in ('is between', 'is not between'):
            if len(input_numeric_2) == 0:
                self.error_msg("no input in filter " + str(index + 1))
                return False
            if not is_float(input_numeric_2):
                self.error_msg("Only numbers or float allowed in filter " + str(index + 1))
                return False
        return True

    # call to change error label text
    # input: string
    # output: None
    def error_msg(self, msg):
        self.label_error.configure(text=msg, fg='red')

    # initialize error frame
    def init_error_frame(self):
        self.frame_error = Frame(self.root)
        self.frame_error.pack(side=BOTTOM, pady=25)
        self.label_error = Label(self.frame_error)
        self.label_error.pack()

        # setting theme color

    def change_theme(self):
        if self.switch_is_on is True:
            # Set light theme
            self.root.tk.call("set_theme", "light")
            self.switch.configure(text="Light Mode")
            self.switch_is_on = False

        else:
            # Set dark theme
            self.root.tk.call("set_theme", "dark")
            self.switch.configure(text="Dark Mode")
            self.switch_is_on = True


# calling the App
def main():
    App('chinook.db')


main()
