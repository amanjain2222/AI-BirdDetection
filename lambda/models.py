from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, MapAttribute

class FileModel(Model):
    class Meta:
        table_name = "UploadedFiles"
        region = 'us-east-1'
        read_capacity_units = 1
        write_capacity_units = 1

    # Primary key
    FileId = UnicodeAttribute(hash_key=True)
    
    # File type: image, video or audio
    FileType = UnicodeAttribute()

    # Link to the file in S3
    S3URL = UnicodeAttribute()

    # Link to the image thumbnail
    ThumbnailURL = UnicodeAttribute(null=True)

    # Tags of the file
    FileTags = MapAttribute(of=NumberAttribute, null=True) 