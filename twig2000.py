#NEW TEST FOR UPDATYER

import builder, uploader, keys, updater
import os, yaml, datetime, shutil

from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk
import tkcalendar
from tkinterdnd2 import TkinterDnD as tkdnd, DND_FILES
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmb
import tkinter.simpledialog as tksd

class Twig(tkdnd.Tk):
    supported_img_files = ('.png', '.jpg', '.jpeg', '.avif', '.webp', '.heic')
    def __init__(self):
        super().__init__()

        dir_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(dir_path)

        self.builder = builder.Builder()
        self.uploader = uploader.Uploader(keys.NEOCITIES_API_KEY)

        self.load_gui()
        
        self.update_release_list()
        self.update_gig_list()
        
        self.mainloop()

    def load_gui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

        self.site_frame = ttk.Frame(self.notebook)

        self.publish_button = ttk.Button(self.site_frame, text='Publish Changes', command=self.publish)
        self.publish_button.pack()

        self.build_button = ttk.Button(self.site_frame, text='Build site', command=self.build)
        self.build_button.pack()

        self.upload_button = ttk.Button(self.site_frame, text='Upload local site', command=self.upload)
        self.upload_button.pack()

        self.archive_var = tk.BooleanVar()
        self.archive_var.set(True)
        self.archive_checkbox = ttk.Checkbutton(self.site_frame, text='Create site archive', variable=self.archive_var)
        self.archive_checkbox.pack()

        self.update_button = ttk.Button(self.site_frame, text='Update', command=updater.update)
        self.update_button.pack()


        self.release_frame = ttk.Frame(self.notebook)
        self.release_frame.columnconfigure(0, weight=1)
        self.release_frame.columnconfigure(1, weight=1)
        self.release_frame.columnconfigure(2, weight=1)
        self.release_frame.rowconfigure(0, weight=1)

        self.release_list = tk.Listbox(self.release_frame, selectmode=tk.SINGLE)
        self.release_list.grid(column=0, columnspan=3, row=0, sticky='nesw')

        self.release_edit = ttk.Button(self.release_frame, text='Edit', command=self.edit_release)
        self.release_edit.grid(column=0, row=1, sticky='nesw')

        self.release_new = ttk.Button(self.release_frame, text='New', command=self.ask_new_release)
        self.release_new.grid(column=1, row=1, sticky='nesw')

        self.release_delete = ttk.Button(self.release_frame, text='Delete', command=self.ask_delete_release)
        self.release_delete.grid(column=2, row=1, sticky='nesw')

        self.gig_frame = ttk.Frame(self.notebook)
        self.gig_frame.columnconfigure(0, weight=1)
        self.gig_frame.columnconfigure(1, weight=1)
        self.gig_frame.columnconfigure(2, weight=1)
        self.gig_frame.rowconfigure(0, weight=1)

        self.gig_list = tk.Listbox(self.gig_frame, selectmode=tk.SINGLE)
        self.gig_list.grid(column=0, row=0, columnspan=3, sticky='nesw')

        self.gig_edit = ttk.Button(self.gig_frame, text='Edit', command=self.edit_gig)
        self.gig_edit.grid(row=1, column=0, sticky='nesw')

        self.gig_new = ttk.Button(self.gig_frame, text='New', command=self.ask_new_gig)
        self.gig_new.grid(row=1, column=1, sticky='nesw')

        self.gig_delete = ttk.Button(self.gig_frame, text='Delete', command=self.ask_delete_gig)
        self.gig_delete.grid(row=1, column=2, sticky='nesw')

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
            gig_details['slug'] = gig_file.split('.')[0]
            gigs.append(gig_details)

        gigs.sort(key=lambda x: x['date'], reverse=True)

        for gig in gigs:
            self.gig_list.insert(tk.END, gig['slug'])

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

    def create_gig_popup(self, gig_slug):
        self.gig_popup = GigPopup(self, gig_slug)
        self.gig_popup.grab_set()
        self.wait_window(self.gig_popup)

    def edit_gig(self):
        if not self.gig_list.curselection(): return
        current_gig = self.gig_list.get(self.gig_list.curselection())
        self.create_gig_popup(current_gig)

    def ask_new_gig(self):
        while True:
            gig_name = tksd.askstring('Enter ID', prompt='Please enter an ID (this will not be visible to others so you can choose whatever)')
            if not gig_name:
                return
            if not gig_name.replace(' ', '').replace('_', '').isalnum():
                tkmb.showerror('Invalid ID', message='ID must contain only letters, numbers, _, and spaces')
            elif os.path.exists(f'src/gigs/{gig_name}.yaml'):
                tkmb.showerror('Invalid ID', message='ID already exists')
            else:
                break

        self.new_gig(gig_name)
        self.update_gig_list()

    def new_gig(self, gig_name):
        today = datetime.date.today()
        with open(f'src/gigs/{gig_name}.yaml', 'w') as f:
            f.write(f'date: {today}\n'
                    'event: \n'
                    'link: \n'
                    'venue: ')

        self.update_gig_list()


    def ask_delete_gig(self):
        if not self.gig_list.curselection(): return
        gig_name = self.gig_list.get(self.gig_list.curselection())
        sure_delete = tkmb.askyesno(title='Delete Gig?', message=f'Would you like to delete {gig_name}?')
        if sure_delete:
            self.delete_gig(gig_name)

    def delete_gig(self, slug):
        os.remove(f'src/gigs/{slug}.yaml')
        self.update_gig_list()

    def create_release_popup(self, release_slug):
        self.release_popup = ReleasePopup(self, release_slug)
        self.release_popup.grab_set()
        self.wait_window(self.release_popup)

    def edit_release(self):
        if not self.release_list.curselection(): return
        current_release = self.release_list.get(self.release_list.curselection())
        self.create_release_popup(current_release)

    def ask_new_release(self):
        while True:
            release_name = tksd.askstring('Enter ID', prompt='Please enter an ID (this will not be visible to others so you can choose whatever)')
            if not release_name:
                return
            if not release_name.replace(' ', '').replace('_', '').isalnum():
                tkmb.showerror('Invalid ID', message='ID must contain only letters, numbers, _, and spaces')
            elif os.path.exists(f'src/releases/{release_name}'):
                tkmb.showerror('Invalid ID', message='ID already exists')
            else:
                break

        self.new_release(release_name)
        self.update_release_list()

    def new_release(self, name):
        today = datetime.date.today()
        dr = f'src/releases/{name}/'
        os.mkdir(dr)
        with open(dr+'info.yaml', 'w') as f:
            f.write((f'date: {today}\n'
                    'description: New Release\n'
                    'links:\n'
                    '   Bandcamp: \n' 
                    '   Soundcloud: \n'
                    '   Spotify: \n'
                    '   YouTube: \n'
                    'title: New Release'))

        self.update_release_list()

    def ask_delete_release(self):
        if not self.release_list.curselection(): return
        release_name = self.release_list.get(self.release_list.curselection())
        sure_delete = tkmb.askyesno(title='Delete Release?', message=f'Would you like to delete {release_name}?')
        if sure_delete:
            self.delete_release(release_name)

    def delete_release(self, name):
        shutil.rmtree(f'src/releases/{name}')
        self.update_release_list()

    def build(self):
        sure_build = tkmb.askokcancel('Continue building', message='This will remove all unsaved changes. Proceed?')
        if sure_build:
            self.builder.rebuild_site(make_archive=self.archive_var.get())
            return True
        else: return False

    def upload(self):
        sure_upload = tkmb.askokcancel('Continue uploading', message='Uploading will replace files on the server. Proceed?')
        if sure_upload:
            self.uploader.upload()

    def publish(self):
        if self.build(): #ugly but so if cancelled building, cancel uploading
            self.upload()

    
class GigPopup(tk.Toplevel):
    def __init__(self, root, slug):
        super().__init__()
        self.root = root
        self.slug = slug
        self.src = f'src/gigs/{slug}.yaml'

        self.load_gui()
        self.load_src()

    def load_gui(self):
        self.protocol('WM_DELETE_WINDOW', self.ask_close)
        self.resizable(True, False)

        self.columnconfigure(1, weight=1)
        
        self.event_desc = ttk.Label(self, text='Event: ')
        self.event_desc.grid(row=0, column=0, sticky='nesw')
        self.event_entry = ttk.Entry(self)
        self.event_entry.grid(row=0, column=1, sticky='nesw')

        self.date_desc = ttk.Label(self, text='Date: ')
        self.date_desc.grid(row=1, column=0, sticky='nesw')
        self.date_entry = tkcalendar.DateEntry(self, locale='en_AU')
        self.date_entry.grid(row=1, column=1, sticky='nesw')

        self.link_desc = ttk.Label(self, text='Link: ')
        self.link_desc.grid(row=2, column=0, sticky='nesw')
        self.link_entry = ttk.Entry(self)
        self.link_entry.grid(row=2, column=1, sticky='nesw')

        self.venue_desc = ttk.Label(self, text='Venue: ')
        self.venue_desc.grid(row=3, column=0, sticky='nesw')
        self.venue_entry = ttk.Entry(self)
        self.venue_entry.grid(row=3, column=1, sticky='nesw')

        self.button_frame = tk.Frame(self)
        self.button_frame.grid(row=4, column=0, columnspan=2, sticky='nesw')

        self.cancel_button = ttk.Button(self.button_frame, text='Cancel', command=self.force_close)
        self.cancel_button.pack(side='right')
        
        self.save_button = ttk.Button(self.button_frame, text='Save and Close', command=self.save_and_close)
        self.save_button.pack(side='right')

    def load_src(self):
        with open(self.src) as f:
            gig_details = yaml.safe_load(f)
            
        self.event_entry.insert(tk.END, gig_details['event'] or '')
        self.date_entry.set_date(gig_details['date'])
        self.link_entry.insert(tk.END, gig_details['link'] or '')
        self.venue_entry.insert(tk.END, gig_details['venue'] or '')

    def save_src(self):
        gig_details = {}
        gig_details['event'] = self.event_entry.get()
        gig_details['date'] = self.date_entry.get_date()
        gig_details['link'] = self.link_entry.get()
        gig_details['venue'] = self.venue_entry.get()

        with open(self.src, 'w') as f:
            yaml.safe_dump(gig_details, f)

    def save_and_close(self):
        self.save_src()
        self.force_close()

    def ask_close(self):
        sure_close = tkmb.askokcancel(title='Close without saving', message='Your changes are not saved. Would you like to close without saving?')
        if sure_close:
            self.force_close()

    def force_close(self):
        self.destroy()

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
        self.protocol('WM_DELETE_WINDOW', self.ask_close)
        
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

        self.photo_drop = ttk.Button(self, text='Click to select cover',
                                      command=self.choose_photo)
        self.photo_drop.drop_target_register(DND_FILES)
        self.photo_drop.dnd_bind('<<Drop>>', lambda e: self.cover_chosen(e.data))
        self.photo_drop.grid(row=6, column=1, columnspan=1, sticky='nesw', ipady=10)

        self.button_frame = tk.Frame(self)
        self.button_frame.grid(row=7, column=0, columnspan=2, sticky='nesw')

        self.cancel_button = ttk.Button(self.button_frame, text='Cancel', command=self.force_close)
        self.cancel_button.pack(side='right')

        self.save_button = ttk.Button(self.button_frame, text='Save and Close', command=self.save_and_close)
        self.save_button.pack(side='right')

    def load_dir(self):
        with open(self.dir+'info.yaml') as f:
            release_details = yaml.safe_load(f)

        self.title_entry.insert(tk.END, release_details['title'] or '')
        self.date_entry.set_date(release_details['date'])
        self.description_entry.insert(tk.END, release_details['description'] or '')

        for link_name, url in release_details['links'].items():
            if url is None: url = ''
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


    def save_and_close(self):
        self.save_dir()
        self.force_close()

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

    def force_close(self):
        self.destroy()

    def ask_close(self):
        sure_close = tkmb.askokcancel(title='Close without saving', message='Your changes are not saved. Would you like to close without saving?')
        if sure_close:
            self.force_close()

twig = Twig()
