from django.db import models

from django.core.files import File
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex 
from saintsophia.storages import OriginalFileStorage, IIIFFileStorage

from PIL import Image
from typing import *
import uuid
import os
import pyvips

Image.MAX_IMAGE_PIXELS = None

TIFF_KWARGS = {
    "tile": True, 
    "pyramid": True, 
    # "compression": 'jpeg', 
    "Q": 100, 
    "tile_width": 512, 
    "tile_height": 512
}

DEFAULT_FIELDS  = ['created_at', 'updated_at', 'published']
DEFAULT_EXCLUDE = ['created_at', 'updated_at', 'published', 'polymorphic_ctype']


def get_fields(model: models.Model, exclude=DEFAULT_EXCLUDE):
    return [field.name for field in (model._meta.fields + model._meta.many_to_many) if field.name not in exclude]

def get_many_to_many_fields(model: models.Model, exclude=DEFAULT_EXCLUDE):
    return [field.name for field in (model._meta.many_to_many) if field.name not in exclude]

def get_media_directory(instance: models.Model, label: str):

    # Fetches the app name, e.g. 'arosenius'
    app = instance._meta.app_label
    
    # Resulting directory is e.g. 'arosenius/iiif/'
    return os.path.join(app, label)

def get_save_path(instance: models.Model, filename, label: str):

    # Fetches the closest directory
    directory = get_media_directory(instance, label)
    
    # Resulting directory is e.g. 'arosenius/iiif/picture.jpg'
    return os.path.join(directory, filename)


def get_iiif_path(instance: models.Model, filename):

    return get_save_path(instance, filename, "iiif")

def get_original_path(instance: models.Model, filename):

    return get_save_path(instance, filename, "original")


def save_tiled_pyramid_tif(obj, path=IIIFFileStorage().location):
    """Uses pyvips to generate a tiled pyramid tiff.

        Args:
            path (str, optional): The path to save the images. Defaults to IIIF_PATH.
        """

    # Create directory if it does not exist
    save_path = os.path.join(path, get_iiif_path(obj, ""))
    if not os.path.exists(save_path):
        os.makedirs(save_path) 

    # The images are saved with their uuid as the key
    filename = str(obj.uuid) + ".tif"
    out_path = os.path.join(path, get_iiif_path(obj, filename))

    tmp_name = get_iiif_path(obj, f"{str(obj.uuid)}_tmp.tif")
    tmp_path = os.path.join(path, tmp_name)


    # When updating the file, remove the iiif_file
    if os.path.isfile(out_path):
        os.remove(out_path)
        obj.iiif_file.delete(False) # Do not yet save the image deletion

    obj_path =os.path.join(path, get_original_path(obj, obj.file.name))

    # Get the original image as a Pillow object before saving
    image_object = Image.open(obj.file.open())
    image = pyvips.Image.new_from_array(image_object)
 
    # image = pyvips.Image.new_from_file(obj_path, access='sequential')

    # Create temporary file
    image.tiffsave(tmp_path, bigtiff=True, **TIFF_KWARGS)

    # Prepare saving the new IIIF file
    with open(tmp_path, 'rb') as f:
        tiff_image = File(f) 
        obj.iiif_file.save(filename, tiff_image, save=False)
        
    # Remove the temporary path
    if os.path.isfile(tmp_path):
        os.remove(tmp_path)

    return path


#####################################################
class CINameField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(CINameField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return str(value).lower()


########################################################

class AbstractBaseModel(models.Model):
    """Abstract base model for all new tables in the Diana based backend.
    Supplies all rows with datetimes for publication and modification, 
    as well as a toggle for publication.
    """
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("abstract.created_at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("abstract.updated_at"))
    published  = models.BooleanField(default=True, verbose_name=_("abstract.published"))

    class Meta:
        abstract = True


##########################################################


class AbstractTagModel(AbstractBaseModel):
    """Abstract model which creates a simple tag with a case-insensitive text field.
    """
    text = models.CharField(max_length=256, unique=True, verbose_name=_("general.text"))

    class Meta:
        abstract = True


##########################################################

class AbstractImageModel(AbstractBaseModel):
    """Abstract image model for new image models in the Diana based backend. Supplies all images
    with a corresponding UUID and file upload.

    Args:
        AbstractBaseModel (models.Model): The abstract base model for all models in Diana based
    """

    # Create an automatic UUID signifier
    # This is used mainly for saving the images on the IIIF server
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    # The name of a supplied field is available in file.name
    file = models.ImageField(storage=OriginalFileStorage, upload_to=get_original_path, verbose_name=_("general.file"))

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.file}"


class AbstractTIFFImageModel(AbstractImageModel):
    """
    Abstract image model for new TIFF images in the Diana based backend. Beside supplying all images with a 
    UUID and file, it also dynamically generates a pyramidization of the input file, saving it to the IIIF storage.
    """

    class Meta:
        abstract = True

    # The path to the IIIF file
    iiif_file = models.ImageField(storage=IIIFFileStorage, upload_to=get_iiif_path, blank=True, null=True, verbose_name=_("abstract.iiif_file"))

    def save(self, **kwargs) -> None:

        # self._save_tiled_pyramid_tif()
        save_tiled_pyramid_tif(self)

        super().save(**kwargs)



class AbstractDocumentModel(AbstractBaseModel):
    """
    The abstract document model supplies a model with an automatic UUID field, a text field as well as
    a text_vector field. The text_vector may be used as a generated column to hold a tokenized version of
    the text field. This must be generated for example by means of a PostgreSQL trigger, however
    """

    # Create an automatic UUID signifier
    # This is used mainly for saving the images on the IIIF server
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    # The textual content
    text    = models.TextField(default="", verbose_name=_("general.text"))

    # The text vector is a generated column which holds
    # tokenized versions of all columns which should be searchable
    # Performance is vastly improved if accompanied by a manual migration 
    # which adds this column automatically, instead of at runtime
    text_vector = SearchVectorField(null=True, verbose_name=_("abstract.text_vector"))

    class Meta:
        abstract = True
        indexes = (GinIndex(fields=["text_vector"]),)

    def __str__(self) -> str:
        return f"{self.text[0:50]}"