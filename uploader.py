import neocities, keys

class Uploader(neocities.Neocities):
    def __init__(self, api_key):
        super().__init__(api_key)

    def upload(self):
        response = self.upload_folder('site')
