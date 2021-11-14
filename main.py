from tkinter import *
import tkinter as tk
from tkinter import ttk
from datetime import date
import sqlite3
import pendulum
from tkcalendar import DateEntry
pendulum.week_starts_at(pendulum.SUNDAY)
pendulum.week_ends_at(pendulum.SATURDAY)

class Query:
    def __init__(self, index, frame):
        self.index = index

        self.selectedItemQuery = StringVar()
        self.selectedItemQuery.set('Select Attribute')

        self.menu_btn_attribute = ttk.Menubutton(frame, text=self.selectedItemQuery.get())
        self.menu_attribute = Menu(self.menu_btn_attribute, tearoff=0)
        self.menu_btn_attribute["menu"] = self.menu_attribute
        self.menu_btn_attribute.grid(row=index, column=1, pady=5)

        self.label_select_attribute = Label(frame, text="Attribute: ")
        self.label_select_attribute.grid(row=index, column=0, pady=5)

        # init menu button for select option by type
        self.selected_type_filter = None
        self.menu_btn_filter = None
        self.menu_filter = None
        self.label_select_filter = None
        self.text_input = None
        self.label_between_to = None
        self.text_input_2 = None
        self.date_entry = None
        self.date_entry_2 = None
        self.init_filter(frame)
        self.init_text_input(frame)
        self.init_date(frame)

    def init_date(self, frame):
        self.date_entry = DateEntry(frame)
        self.date_entry_2 = DateEntry(frame)

    def init_filter(self, frame):
        self.selected_type_filter = StringVar()
        self.selected_type_filter.set('Select filter')

        self.menu_btn_filter = ttk.Menubutton(frame, text=self.selected_type_filter.get())
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
                             'is not equal to']
        self.filters_int_or_numeric = ['is equal to', 'is between', 'is less than', 'is less than or equal to',
                                       'is greater than',
                                       'is greater than or equal to',
                                       'is not equal to', 'is not between']
        self.filters_date = ['today', 'this week', 'last week', 'this month', 'last month', 'this year', 'last year',
                             'before', 'after', 'between']

        self.dict_attri_to_sign = {'is equal to': '= \'#\'', 'is less than': '< #', 'is less than or equal to': '<= #',
                                   'is greater than': '> #', 'is greater than or equal to': '>= #', 'is between' : '< # AND $ > #',
                                   'is not equal to': '!= #', 'starts with': 'LIKE \'#%\'', 'contains': 'LIKE \'%#%\'',
                                   'does not starts with': 'NOT LIKE \'#%\'', 'does not contain': 'NOT LIKE \'%#%\'',
                                   'today': '= "' + str(date.today()) + ' 00:00:00"',
                                   'this year': '>= "' + str(date.today().year) + '-01-01" AND # < "'
                                                + str(int(date.today().year) + 1) + '-01-01"', 'this week' : '>= "' + str(pendulum.now().subtract(days=date.today().weekday() + 1).date()) + '" AND # < "'
                                                + str(pendulum.now().date()) + '"' , 'this month' : '>= "' + str(pendulum.now().subtract(days=date.today().day -1).date()) + '" AND # < "'
                                                + str(pendulum.now().date()) + '"', 'last week' : '>= "' + str(pendulum.now().subtract(weeks=1).date()) + '" AND # < "'
                                                + str(pendulum.now().date()) + '"', 'last month' : '>= "' + str(pendulum.now().subtract(months=1).date()) + '" AND # < "'
                                                + str(pendulum.now().date()) + '"', 'last year' : '>= "' + str(pendulum.now().subtract(years=1).date()) + '" AND # < "'
                                                + str(pendulum.now().date()) + '"', 'before' : '< ', 'after' : '> ', 'between' : '< # AND ^ >' }

        # init queries list
        self.queries_list = []
        self.count_queries = 0

        self.initFrameHeader()
        self.switch = ttk.Checkbutton(self.frameHeader, text="Light Mode", style="Switch.TCheckbutton",
                                      command=self.change_theme)
        self.switch.grid(row=0, column=2, padx=25)
        self.switch_is_on = False
        self.initFrameTable()

        self.frameMiddle = Frame(self.root, height=10, width=300)

        self.frameQueries = Frame(self.root, height=150, width=300)

        self.initFrameFooter()
        self.init_errorFrame()

        self.root.mainloop()

    def initFrameHeader(self):
        self.frameHeader = Frame(self.root, height=150, width=300)
        self.frameHeader.pack(pady=25, padx=50)

        self.selectedItem = StringVar()
        self.selectedItem.set('Select Table')
        self.mycursor.execute(
            "SELECT name "
            "FROM sqlite_master "
            "WHERE type='table';")

        self.databases_tup = tuple(x[0] for x in self.mycursor.fetchall())

        self.initBtn()
        self.label_select_table = Label(self.frameHeader, text="Table: ")
        self.label_select_table.grid(row=0, column=0)
        for db_name in self.databases_tup:
            self.menu.add_radiobutton(
                label=db_name,
                variable=self.selectedItem,
                value=db_name,
                command=self.initSelectedTable
            )

    def initBtn(self):
        self.menu_btn = ttk.Menubutton(self.frameHeader, text=self.selectedItem.get())
        self.menu = Menu(self.menu_btn, tearoff=0)
        self.menu_btn["menu"] = self.menu
        self.menu_btn.grid(row=0, column=1)

    def initFrameTable(self):
        self.frameTable = Frame(self.root)
        self.tree = ttk.Treeview(self.frameTable, height=10, show="headings")
        self.frameTable.configure(height=200)
        self.y_scrollbar = Scrollbar(self.frameTable, orient=VERTICAL, command=self.tree.yview)
        self.x_scrollbar = Scrollbar(self.frameTable, orient=HORIZONTAL, command=self.tree.xview)

        self.tree.configure(yscrollcommand=self.y_scrollbar.set, xscrollcommand=self.x_scrollbar.set)
        self.y_scrollbar.pack(side=RIGHT, fill=Y)
        self.x_scrollbar.pack(side=BOTTOM, fill=X)

        self.tree.pack(fill=X)

    def initFrameFooter(self):
        # init the footer frame and packing it
        self.frameFooter = Frame(self.root, height=150, width=300)
        self.frameFooter.pack(side=BOTTOM, pady=25)

        # define exit and clear buttons
        self.exit_btn = ttk.Button(self.frameFooter, text="Exit", style="Accent.TButton",
                                   command=lambda: self.root.destroy())
        # self.exit_btn['font'] = self.btnFont
        self.exit_btn.grid(row=0, column=0, padx=25)

        self.clr_btn = ttk.Button(self.frameFooter, text="Clear", style="Accent.TButton", command=self.clear)
        self.clr_btn.grid(row=0, column=1, padx=25)

    def initSelectedTable(self):
        self.count_queries = 0
        self.frameTable.pack(padx=100, fill=X)
        # clearing the list each table selection
        self.queries_list.clear()
        # clear queries frame
        for child in self.frameMiddle.winfo_children():
            child.destroy()
        for child in self.frameQueries.winfo_children():
            child.destroy()
        self.frameMiddle.pack(pady=5, padx=50)
        self.frameQueries.pack(pady=25, padx=50)

        selectedTableName = self.selectedItem.get()
        self.mycursor.execute("PRAGMA table_info(" + selectedTableName + ")")
        # list of tuple that contains header name and type.
        headers_type_tup = list(map(lambda x: (x[1], x[2]), self.mycursor.fetchall()))
        # list of the header's name
        headers = [x[0] for x in headers_type_tup]
        # dict of header name and type
        self.dict_headers_types = {k: v for (k, v) in headers_type_tup}
        length_headers = len(headers)
        # configure the tuple columns from headers.
        h_tuple = tuple((x + 1 for x in range(length_headers)))
        self.tree.configure(columns=h_tuple)
        # creating headers with header name
        for index, value in enumerate(headers):
            # self.insertQueries(index, value)
            self.tree.heading(index + 1, text=value)
            self.tree.column(index + 1, stretch=YES, width=250)
        # define add button for adding new query
        add_query_btn = ttk.Button(self.frameMiddle, text="Add Query", command=self.addQuery)
        add_query_btn.grid(row=0, column=0, padx=10, pady=15)
        # define submit button for the current query
        submit_btn = ttk.Button(self.frameMiddle, text="Submit", command=self.submit)
        submit_btn.grid(row=0, column=1, padx=10, pady=15)

        self.data(length_headers)
        self.menu_btn.configure(text=selectedTableName)

    def addQuery(self):

        # new query object that contain a menu for attribute and menu for the right filter menu by the attribute type.
        new_query = Query(self.count_queries, self.frameQueries)
        self.count_queries += 1

        for header_name, header_type in self.dict_headers_types.items():
            new_query.menu_attribute.add_radiobutton(
                label=header_name,
                variable=new_query.selectedItemQuery,
                value=header_name,
                command=lambda: self.initQuery(new_query)
            )

        # array of all queries
        self.queries_list.append(new_query)

    def initQuery(self, query):
        # each time the user select query attribute, the recent filter will be removed and a new one will be added.
        query.label_select_filter.grid_forget()
        query.menu_btn_filter.grid_forget()
        query.text_input.grid_forget()
        query.label_between_to.grid_forget()
        query.text_input_2.grid_forget()

        query.init_filter(self.frameQueries)

        selected_item_query = query.selectedItemQuery.get()
        query.menu_btn_attribute.configure(text=selected_item_query)

        # adding label and menu filter for the selected query attribute
        query.label_select_filter.grid(row=query.index, column=2, pady=5)
        query.menu_btn_filter.grid(row=query.index, column=3, pady=5)

        header_type = self.dict_headers_types[selected_item_query]

        if 'CHAR' in header_type:
            for label in self.filters_char:
                query.menu_filter.add_radiobutton(
                    label=label,
                    variable=query.selected_type_filter,
                    value=label,
                    command=lambda: self.initFilter(query)
                )
            return
        if 'DATETIME' in header_type:
            for label in self.filters_date:
                query.menu_filter.add_radiobutton(
                    label=label,
                    variable=query.selected_type_filter,
                    value=label,
                    command=lambda: self.initFilterDate(query)
                )
            return
        elif 'INTEGER' or 'NUMERIC' in header_type:
            for label in self.filters_int_or_numeric:
                query.menu_filter.add_radiobutton(
                    label=label,
                    variable=query.selected_type_filter,
                    value=label,
                    command=lambda: self.initFilter(query)
                )

    def initFilter(self, query):
        # each time we select a filter we need to remove the last inputs by the type and initializing them again
        query.text_input.grid_forget()
        query.label_between_to.grid_forget()
        query.text_input_2.grid_forget()
        query.date_entry.grid_forget()
        query.date_entry_2.grid_forget()

        selected_filter = query.selected_type_filter.get()
        query.menu_btn_filter.configure(text=selected_filter)
        query.init_text_input(self.frameQueries)
        query.text_input.grid(row=query.index, column=4, pady=10, padx=10)
        if selected_filter in ('is between', 'is not between'):
            query.label_between_to = ttk.Label(self.frameQueries, text='to')
            query.label_between_to.grid(row=query.index, column=5, pady=10, padx=5)
            query.text_input_2.grid(row=query.index, column=6, pady=10, padx=10)

    def clear(self):
        for x in self.tree.get_children():
            self.tree.delete(x)
        self.tree.configure(columns=())
        self.frameTable.pack_forget()
        self.queries_list.clear()
        self.frameMiddle.pack_forget()
        self.frameQueries.pack_forget()
        self.selectedItem.set('Select Table')
        self.count_queries = 0
        self.menu_btn.configure(text=self.selectedItem.get())
        self.error_msg("")

    def submit(self):
        self.label_error.configure(text='')
        queryText = "SELECT * FROM " + self.selectedItem.get() + " \nWHERE "
        for index, query in enumerate(self.queries_list):
            type = self.dict_headers_types[query.selectedItemQuery.get()]
            if self.check_input(type, query, index):
                return
            queryText += query.selectedItemQuery.get() + " "
            if query.selected_type_filter.get() in ('is between', 'is not between'):
                queryText += query.selected_type_filter.get() + " " + query.text_input.get().replace(" ", "") + " to " + query.text_input_2.get().replace(" ", "")
            else:
                queryText += self.dict_attri_to_sign[query.selected_type_filter.get()]
            if 'DATETIME' in type:
                if query.selected_type_filter.get() in ('before', 'after'):
                    queryText += '"' + str(query.date_entry.get_date()) + '"'
                else:
                    queryText = queryText.replace('#', str(query.selectedItemQuery.get()), 2)
            elif 'CHAR' in type:
                queryText = queryText.replace('#', str(query.text_input.get()))
            else:
                queryText = queryText.replace('#', str(query.text_input.get().replace(" ", "")))
            if ((index + 1) < len(self.queries_list) and len(self.queries_list) > 1):
                queryText += '\nAND '
        queryText += ";"
        print(queryText)
        self.dataQuery(len(self.dict_headers_types), queryText)

    def dataQuery(self, headers_length, Q):
        for x in self.tree.get_children():
            self.tree.delete(x)
        self.mycursor.execute(Q)
        for row in self.mycursor:
            self.tree.insert('', 'end', values=row[0:headers_length])

    def data(self, headers_length):
        for x in self.tree.get_children():
            self.tree.delete(x)
        self.mycursor.execute("SELECT *  FROM " + self.selectedItem.get())
        for row in self.mycursor:
            self.tree.insert('', 'end', values=row[0:headers_length])

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

    def initFilterDate(self, query):
        query.text_input.grid_forget()
        query.label_between_to.grid_forget()
        query.text_input_2.grid_forget()
        query.date_entry.grid_forget()
        query.date_entry_2.grid_forget()

        selected_filter = query.selected_type_filter.get()
        query.menu_btn_filter.configure(text=selected_filter)
        if selected_filter in ('between'):
            query.init_date(self.frameQueries)
            query.date_entry.grid(row=query.index, column=4, pady=10, padx=10)
            query.label_between_to = ttk.Label(self.frameQueries, text='to')
            query.label_between_to.grid(row=query.index, column=5, pady=10, padx=5)
            query.date_entry_2.grid(row=query.index, column=6, pady=10, padx=10)
        if selected_filter in ('before', 'after'):
            query.init_date(self.frameQueries)
            query.date_entry.grid(row=query.index, column=4, pady=10, padx=10)

    def error_msg(self, msg):
        self.label_error.configure(text=msg, fg='red')

    def init_errorFrame(self):
        self.frameError = Frame(self.root)
        self.frameError.pack(side=BOTTOM, pady=25)
        self.label_error = Label(self.frameError)
        self.label_error.pack()

    # checking if the input we get is correct
    # getting type of input, the query data to get input, and index of the filter
    # returns True for bad input, False for good input
    def check_input(self, type, query, index):
        if 'DATETIME' in type:
            if query.date_entry.get_date() > date.today():
                self.error_msg("Wrong Date in filter number " + str(index + 1))
                return True
        if 'INTEGER' in type:
            input = query.text_input.get().replace(" ", "")
            input2 = query.text_input_2.get().replace(" ", "")
            if not input.isdigit():
               self.error_msg("Only numbers allowed in filter " + str(index + 1))
               return True
            if query.selected_type_filter.get() in ('is between', 'is not between'):
                if not input2.isdigit():
                    self.error_msg("Only numbers allowed in filter " + str(index + 1))
                    return True
        if 'NUMERIC' in type:
            input = query.text_input.get().replace(" ", "")
            input2 = query.text_input_2.get().replace(" ", "")
            if not self.isfloat(input):
                self.error_msg("Only numbers or float allowed in filter " + str(index + 1))
                return True
            if query.selected_type_filter.get() in ('is between', 'is not between'):
                if not self.isfloat(input2):
                    self.error_msg("Only numbers or float allowed in filter " + str(index + 1))
                    return True

        return False

    def isfloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

def main():
    App('chinook.db')


main()
