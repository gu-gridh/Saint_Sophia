from django.core.files.storage import FileSystemStorage
from django.conf import settings

class OriginalFileStorage(FileSystemStorage):
    def __init__(self,) -> None:

        location = settings.MEDIA_ROOT
        base_url = settings.ORIGINAL_URL

        super().__init__(location, base_url)

class IIIFFileStorage(FileSystemStorage):
    def __init__(self,) -> None:

        location = settings.MEDIA_ROOT
        base_url = settings.IIIF_URL

        super().__init__(location, base_url)