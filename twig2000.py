import builder, uploader
import os, yaml

from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk
import tkcalendar
from tkinterdnd2 import TkinterDnD as tkdnd, DND_FILES
import tkinter.filedialog as tkfd

class Twig(tkdnd.Tk):
    supported_img_files = ('.png', '.jpg', '.jpeg', '.avif', '.webp', '.heic')
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
        self.release_frame.columnconfigure(0, weight=1)
        self.release_frame.columnconfigure(1, weight=1)
        self.release_frame.rowconfigure(0, weight=1)

        self.release_list = tk.Listbox(self.release_frame, selectmode=tk.SINGLE)
        self.release_list.grid(column=0, columnspan=2, row=0, sticky='nesw')

        self.release_edit = ttk.Button(self.release_frame, text='Edit', command=self.edit_release)
        self.release_edit.grid(column=0, row=1, sticky='nesw')

        self.release_new = ttk.Button(self.release_frame, text='New', command=self.edit_release)
        self.release_new.grid(column=1, row=1, sticky='nesw')
        
        self.update_release_list()


        self.gig_frame = ttk.Frame(self.notebook)

        self.gig_list = tk.Listbox(self.gig_frame, selectmode=tk.SINGLE)
        self.gig_list.pack(expand=True, fill='both')
        self.update_gig_list()
        self.gig_list.bind('<<ListboxSelect>>', self.gig_selected)


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
            releases.append((release_dir, release_details['date']))


        releases.sort(key=lambda x: x[1], reverse=True)

        for release in releases:
            self.release_list.insert(tk.END, release[0])

    def on_tab_change(self, event):
        self.update_gig_list()
        self.update_release_list()

    def create_gig_popup(self):
        self.gig_popup = GigPopup(self)
        self.gig_popup.grab_set()
        self.wait_window(self.gig_popup)

    def create_release_popup(self, release_slug):
        self.release_popup = ReleasePopup(self, release_slug)
        self.release_popup.grab_set()
        self.wait_window(self.release_popup)

    def gig_selected(self, event):
        self.create_gig_popup()

    def edit_release(self):
        current_release = self.release_list.get(self.release_list.curselection())
        self.create_release_popup(current_release)

class GigPopup(tk.Toplevel):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.gig_entry = tk.Entry(self)
        self.gig_entry.pack()

class ReleasePopup(tk.Toplevel):
    def __init__(self, root, slug):
        super().__init__()
        self.root = root
        self.slug = slug
        self.dir = f'src/releases/{self.slug}/'
        self.cover_path = None
        
        self.load_gui()
        self.load_dir()

    def load_gui(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, weight=1)
        self.title_desc = ttk.Label(self, text='Title:')
        self.title_desc.grid(row=0, column=0, sticky='nsw')
        self.title_entry = ttk.Entry(self)
        self.title_entry.grid(row=0, column=1, sticky='nesw')

        self.date_desc = ttk.Label(self, text='Date:')
        self.date_desc.grid(row=1, column=0, sticky='nsw')
        self.date_entry = tkcalendar.DateEntry(self, locale='en_AU')
        self.date_entry.grid(row=1, column=1, sticky='nesw')

        self.description_desc = ttk.Label(self, text='Description:')
        self.description_desc.grid(row=2, column=0, sticky='nsw')
        self.description_entry = tk.Text(self, height=4)
        self.description_entry.grid(row=3, column=0, columnspan=2, sticky='nesw')

        self.links_desc = ttk.Label(self, text='Links:')
        self.links_desc.grid(row=4, column=0, sticky='nsw')
        self.links_entry = tk.Text(self, height=4)
        self.links_entry.grid(row=5, column=0, columnspan=2, sticky='nesw')


        self.photo_label = ttk.Label(self)
        self.photo_label.grid(row=6, column=0, sticky='nesw')

        self.photo_drop = ttk.Button(self, text='Click/Drag to set cover',
                                      command=self.choose_photo)
        self.photo_drop.drop_target_register(DND_FILES)
        self.photo_drop.dnd_bind('<<Drop>>', lambda e: self.cover_chosen(e.data))
        self.photo_drop.grid(row=6, column=1, columnspan=1, sticky='nesw', ipady=10)

        self.save_button = ttk.Button(self, text='Save and Close', command=self.save_dir)
        self.save_button.grid(row=7, column=0)

        self.cancel_button = ttk.Button(self, text='Cancel', command=self.force_close)
        self.cancel_button.grid(row=7, column=0)

    def load_dir(self):
        with open(self.dir+'info.yaml') as f:
            release_details = yaml.safe_load(f)

        self.title_entry.insert(tk.END, release_details['title'])
        self.date_entry.set_date(release_details['date'])
        self.description_entry.insert(tk.END, release_details['description'])

        for link_name, url in release_details['links'].items():
            self.links_entry.insert(tk.END, f'{link_name}: {url}\n')
        
        try:
            self.cover_img = Image.open(self.dir+'cover.png')
            self.cover_img.thumbnail((100, 100))
            self.cover_photo = ImageTk.PhotoImage(self.cover_img)
            self.photo_label.config(image=self.cover_photo)
        except FileNotFoundError:
            pass

    def save_dir(self):
        release_details = {}
        
        release_details['title'] = self.title_entry.get()
        release_details['date'] = self.date_entry.get_date()
        release_details['description'] = self.description_entry.get('1.0', tk.END).strip()

        release_details['links'] = {}
        links_raw = self.links_entry.get('1.0', tk.END)
        for line in links_raw.splitlines():
            if not line: continue
            name, url = line.split(': ')
            release_details['links'][name] = url

        if self.cover_path is not None:
            self.save_cover()

        with open(self.dir+'info.yaml', 'w') as f:
            yaml.safe_dump(release_details, f, default_flow_style=False)

    def choose_photo(self):
        if path := tkfd.askopenfilename():
            self.cover_chosen(path)

    def cover_chosen(self, path):
        file_type = ('.'+path.split('.')[-1]).lower()
        if file_type in Twig.supported_img_files:
            self.cover_path = path
            self.photo_drop.config(text='Click/Drag to set cover: '+path)
            self.cover_img = Image.open(path)
            self.cover_img.thumbnail((100, 100))
            self.cover_photo = ImageTk.PhotoImage(self.cover_img)
            self.photo_label.config(image=self.cover_photo)

    def save_cover(self):
        img = Image.open(self.cover_path)
        img.save(self.dir+f'cover.png')


twig = Twig()
