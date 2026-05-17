import yaml, os, chevron, datetime
import tkinter as tk
from tkinter import ttk


class Builder:
    def build_site(self):
        self.templates = os.listdir('./templates')

        self.load_site()
        self.clean_database()

        for template_path in self.templates:
            self.build_page(template_path)

    def load_site(self):
        self.db = {}
        with open('src/site.yaml') as f:
            site = yaml.safe_load(f)
            for item in site:
                item_class = list(item.keys())[0]
                if item_class not in list(self.db.keys()):
                    self.db[item_class] = []

                self.db[item_class].append(item[item_class])

    def clean_database(self):
        #check which gigs are over
        self.db['Upcoming Gig'] = []
        self.db['Past Gig'] = []
        for gig in self.db['Gig']:
            date_obj = datetime.datetime.strptime(gig['date'], '%d/%m/%Y')
            gig['date_obj'] = date_obj
            print((date_obj - datetime.datetime.now()))
            if date_obj > datetime.datetime.now():
                #gig is upcoming
                self.db['Upcoming Gig'].append(gig)
            else:
                self.db['Past Gig'].append(gig)

        self.db['Upcoming Gig'].sort(key=lambda x: date_obj)
        self.db['Past Gig'].sort(key=lambda x: date_obj)

    def render_template(self, data, template):
        return chevron.render(template, data)

    def build_page(self, path):
        page_name = os.path.basename(path).split('.')[0]
        with open('templates/'+path) as f:
            template = f.read()

        rendered_page = self.render_template(self.db, template)

        with open(f'out/{page_name}.html', 'w') as f:
            f.write(rendered_page)


class Editor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.builder = Builder()
        
        self.load_gui()
        self.load_site()
        self.sync_gui()


    def load_gui(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self)

        self.release_frame = ttk.Frame(self.notebook)
        self.release_frame.columnconfigure(1, weight=1)
        self.release_frame.rowconfigure(0, weight=1)
        
        self.release_listbox = tk.Listbox(self.release_frame)
        self.release_listbox.grid(row=0, column=0, sticky='nesw')

        self.release_title = tk.Label(self.release_frame)

        self.release_desc = tk.Label(self.release_frame)

        
        self.gig_frame = ttk.Frame(self.notebook)
        self.gig_frame.columnconfigure(1, weight=1)
        self.gig_frame.rowconfigure(0, weight=1)
        
        self.gig_listbox = tk.Listbox(self.gig_frame)
        self.gig_listbox.grid(row=0, column=0, sticky='nesw')


        self.notebook.add(self.release_frame, text='Releases')
        self.notebook.add(self.gig_frame, text='Gigs')
        self.notebook.grid(row=0, column=1, sticky='nesw')


    def load_site(self):
        self.db = {}
        with open('src/site.yaml') as f:
            site = yaml.safe_load(f)
            for item in site:
                item_class = list(item.keys())[0]
                if item_class not in list(self.db.keys()):
                    self.db[item_class] = []

                self.db[item_class].append(item[item_class])


    def sync_gui(self):
        for gig in self.db['Gig']:
            self.gig_listbox.insert(0, gig['venue'])

        for release in self.db['Release']:
            self.release_listbox.insert(0, release['title'])


editor = Editor()

    


