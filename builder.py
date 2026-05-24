import yaml, os, shutil, chevron, zipfile, pathlib
import datetime
from PIL import Image

#builder steps:
#   read site.yaml, read releases, read gigs
#   archive
#   move photos and files, build pages
#


# rn doesnt move/downscale photos
# if added should probs be made selective ???

class Builder:
    def __init__(self):
        pass

    def rebuild_site(self, make_archive=False, clean_build=True):
        if make_archive: self.archive_site()
        if clean_build: self.clear_site()
        self.build_site()

    def clear_site(self):
        print('Clearing site...')
        shutil.rmtree('site')
        os.mkdir('site')
        print('Site cleared')

    def load_site(self):
        print('Loading site...')
        self.load_manifest()
        self.load_gigs()
        self.load_releases()
        print('Site loaded')

    def build_site(self):
        self.load_site()
        print('Building site...')
        self.build_folders()
        self.build_static()
        self.build_pages()
        self.build_covers()
        #self.build_images()
        print('Site built')

    def load_manifest(self):
        self.db = {}
        with open('src/manifest.yaml') as f:
            site = yaml.safe_load(f)
            self.db = site

    def load_gigs(self):
        self.db['gigs'] = []
        for directory in os.listdir('src/gigs'):
            with open(f'src/gigs/{directory}/info.yaml') as f:
                release_details = yaml.safe_load(f)
            self.db['gigs'].append(release_details)

    def load_releases(self):
        self.db['releases'] = []
        for directory in os.listdir('src/releases'):
            with open(f'src/releases/{directory}/info.yaml') as f:
                release_details = yaml.safe_load(f)
            release_details['slug'] = directory
            release_details['cover_url'] = f'covers/{directory}.png'
            link_list = []
            for name, link in release_details['links'].items():
                link_list.append({'name': name, 'url': link})
            release_details['links'] = link_list

            self.db['releases'].append(release_details)

    def load_gigs(self):
        self.db['gigs'] = []
        self.db['upcoming gigs'] = []
        self.db['past gigs'] = []
        for gig in os.listdir('src/gigs'):
            with open(f'src/gigs/{gig}') as f:
                gig_details = yaml.safe_load(f)
            gig_details['slug'] = gig
            today = datetime.date.today()
            if (today<=gig_details['date']): #check if gig is upcoming is past
                self.db['upcoming gigs'].append(gig_details)
            else:
                self.db['past gigs'].append(gig_details)
            self.db['gigs'].append(gig_details)

        self.db['past gigs'].sort(key=lambda x: x['date'], reverse=True)
        self.db['upcoming gigs'].sort(key=lambda x: x['date'], reverse=True)

    def build_covers(self):
        print('Converting covers...')
        for release in self.db['releases']:
            self.load_release_cover(release['slug'])
        print('Covers converted')

    def load_release_cover(self, directory):
        cover = 'src/releases/'+directory+'/cover.png'
        img = Image.open(cover)
        img.thumbnail((256, 256))
        img.save(f'site/covers/{directory}.png')

    def archive_site(self):
        today = datetime.datetime.today()
        archive_name = f'site_{today.day}_{today.month}_{today.year}_{today.hour}_{today.minute}'
        print('Creating site archive...')
        while os.path.isfile(f'archive/{archive_name}.zip'): # really ugly way of making sure we dont override an archive,
            #but that we also always successfully archive
            archive_name += 'n'
        shutil.make_archive(f'archive/{archive_name}.zip', 'zip', 'site/')
        print('Site archived')

    def build_folders(self):
        #os.mkdir('site/audio')
        #os.mkdir('site/textures')
        #os.mkdir('site/fonts')
        os.mkdir('site/covers')
        #os.mkdir('site/images')

    def build_pages(self):
        print('Rendering page templates...')
        for page in os.listdir('src/templates'):
            page_title = page.split('.')[0]
            with open(f'src/templates/{page}') as f:
                template = f.read()

            rendered_page = chevron.render(template, self.db)

            with open(f'site/{page_title}.html', 'w') as f:
                f.write(rendered_page)

        print('Pages rendered')

    def build_static(self):
        print('Moving static files...')
        for root, dirs, files in os.walk('src/static'):
            #print(root)
            for dr in dirs:
                #print(f'Making dir {dr}')
                os.mkdir(f'site/{dr}')
            for file in files:
                path = pathlib.Path(f'{root}/{file}')
                rel_path = path.relative_to('src/static')
                #print(rel_path)
                shutil.copyfile(path, f'site/{rel_path}')
        print('Static files moved')

    def build_images(self):
        pass
##        for file in os.listdir('src/images'):
##            img = Image.open(f'src/images/{file}')
##            #img.thumbnail((512, 512))
##            file_name = file.split('.')[0]
##            img.save(f'site/images/{file_name}.png')

#builder = Builder()
#builder.rebuild_site()
