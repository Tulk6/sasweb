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
            return True
        else:
            raise(NeocitiesAPIError(response))

    ###<------BASE NEOCITIES API FUNCTIONS------>

    def upload(self, *files):
        payload = {}
        for (local_path, path_on_server) in files:
            payload[path_on_server] = open(local_path, 'rb')

        print(payload)
        
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
                local_path = (path+'\\'+file).replace('\\', '/') #neocities wants posix format paths
                server_path = local_path[len(local_source_path):]
                file_paths.append((local_path, server_path)) #assumes that path on server same as local

        self.upload(*file_paths)

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
