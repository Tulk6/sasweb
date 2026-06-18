import requests, os

class Neocities:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def _url(self, method):
        return f'https://neocities.org/api/{method}'

    def _post(self, method, **args):
        return requests.post(self._url(method), **args, 
                headers={'Authorization':'Bearer '+self.api_key})        

    def _get(self, method, **args):
        return requests.get(self._url(method), data=args,
                headers={'Authorization':'Bearer '+self.api_key})

    def _handle_response(self, response):
        if response.status_code == 200:
            print('###Success!###')
            return True
        else:
            raise(NeocitiesAPIError(response))

    ###<------BASE NEOCITIES API FUNCTIONS------>

    def upload_file(self, *files):
        payload = {}
        for (local_path, path_on_server) in files:
            payload[path_on_server] = open(local_path, 'rb')

        print('Uploading these files: ')
        print('\t'+'\n\t'.join(payload.keys()))
        
        r = self._post('upload', files=payload)

        return self._handle_response(r)

    def delete(self, *files):
        args = [(f"filenames[]", file) for file in files]
        r = self._post('delete', data=args)
        
        return self._handle_response(r)

    def list(self, path=None):
        if path is None:
            r = self._get('list')
        else:
            r = self._get('list', path=path)

        self._handle_response(r)
        
        files = r.json()['files']
        return files

    def info(self, sitename=None):
        if sitename is None:
            r = self._get('info')
        else:
            r = self._get('info', sitename=sitename)

        self._handle_response(r)

        info = r.json()['info']
        return info


    ###<------ADDED FUNCTIONS------>

    def upload_folder(self, local_source_path):
        file_paths = []
        for path, subdirs, files in os.walk(local_source_path):
            for file in files:
                file_type = file.split('.')[1].lower()
                if not file_type in 'apng asc atom avif bin cjs css csv dae eot epub geojson gif glb glsl gltf gpg htm html ico jpeg jpg js json jxl key kml knowl less manifest map markdown md mf mid midi mjs mtl obj opml osdx otf pdf pgp pls png py rdf resolveHandle rss sass scss sf2 svg text toml ts tsv ttf txt webapp webmanifest webp woff woff2 xcf xml yaml yml':
                    print(f'COULD NOT UPLOAD {file} - DISALLOWED FILE TYPE')
                    continue
                local_path = (path+'\\'+file).replace('\\', '/') #neocities wants posix format paths
                server_path = local_path[len(local_source_path):]
                file_paths.append((local_path, server_path)) #assumes that path on server same as local

        self.upload_file(*file_paths)

        print('FINISHED UPLOADING')

    def sync_server(self, local_source_path):
        pass


class NeocitiesAPIError(Exception):
    def __init__(self, response):
        self.response = response
        print(response)
        #self.response_json = response.json()

    def __str__(self):
        return self.response.text
        #return f"{self.response_json['error_type']}, {self.response_json['message']}"
