import builder, uploader
import os, yaml

#import tkinter as tk
import tkinter as tk
from tkinter import ttk

class Twig(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.builder = builder.Builder()
        self.uploader = uploader.Uploader('awd')

        self.load_gui()


    def load_gui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

        self.site_frame = ttk.Frame(self.notebook)
        

        self.release_frame = ttk.Frame(self.notebook)
        
        self.release_list = tk.Listbox(self.release_frame)
        self.release_list.pack(expand=True, fill='both')
        self.update_release_list()


        self.gig_frame = ttk.Frame(self.notebook)

        self.gig_list = tk.Listbox(self.gig_frame)
        self.gig_list.pack(expand=True, fill='both')
        self.update_gig_list()


        self.notebook.add(self.site_frame, text='Site')
        self.notebook.add(self.release_frame, text='Releases')
        self.notebook.add(self.gig_frame, text='Gigs')
        self.notebook.pack(expand=True, fill='both')

    def update_gig_list(self):
        self.gig_list.delete(0, tk.END)
        
        gigs = []
        for gig_file in os.listdir('src/gigs'):
            with open('src/gigs/'+gig_file) as f:
                gig_details = yaml.safe_load(f)
            gigs.append(gig_details)
            
        gigs.sort(key=lambda x: x['date'], reverse=True)

        for gig in gigs:
            self.gig_list.insert(tk.END, f'{gig["event"]} @ {gig["venue"]} on {gig["date"]}')

    def update_release_list(self):
        self.release_list.delete(0, tk.END)
        
        releases = []
        for release_dir in os.listdir('src/releases'):
            with open('src/releases/'+release_dir+'/info.yaml') as f:
                release_details = yaml.safe_load(f)
            releases.append(release_details)
            
        releases.sort(key=lambda x: x['date'], reverse=True)

        for release in releases:
            self.release_list.insert(tk.END, f'{release["title"]}')

    def on_tab_change(self, event):
        self.update_gig_list()
        self.update_release_list()
        

twig = Twig()
