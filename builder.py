import yaml, os, chevron
from PIL import Image

#builder steps:
#   read site.yaml, read releases, read gigs
#   move photos and files, build pages


class Builder:
    def __init__(self):
        self.load_site()
        self.build_site()

    def load_site(self):
        self.load_manifest()
        self.load_gigs()
        self.load_releases()

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
            release_details['cover_url'] = f'covers/{directory}.png'
            link_list = []
            for name, link in release_details['links'].items():
                link_list.append({'name': name, 'url': link})
            release_details['links'] = link_list 

            self.db['releases'].append(release_details)
            self.load_release_cover(directory)

    def load_release_cover(self, directory):
        cover = 'src/releases/'+directory+'/cover.png'
        img = Image.open(cover)
        img.thumbnail((256, 256))
        img.save(f'site/covers/{directory}.png')

    def build_site(self):
        for page in os.listdir('src/templates'):
            page_title = page.split('.')[0]
            with open(f'src/templates/{page}') as f:
                template = f.read()

            rendered_page = chevron.render(template, self.db)

            with open(f'site/{page_title}.html', 'w') as f:
                f.write(rendered_page)


builder = Builder()

    
    
