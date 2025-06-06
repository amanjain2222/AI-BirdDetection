from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, MapAttribute

class BirdBaseModel(Model):
    class Meta:
        table_name = "BirdBase"
        region = 'us-east-1'
        read_capacity_units = 1
        write_capacity_units = 1

    # Primary key
    BirdID = UnicodeAttribute(hash_key=True)
    
    # File type: image, video or audio
    FileType = UnicodeAttribute()

    # Link to the file in S3
    MediaURL = UnicodeAttribute()

    # Link to the image thumbnail
    ThumbnailURL = UnicodeAttribute(null=True)

    # Uploaded date
    UploadedDate = UnicodeAttribute()

    # Uploader's username
    Uploader = UnicodeAttribute()

class BirdBaseIndexModel(Model):
    class Meta:
        table_name = "BirdBaseIndex"
        region = 'us-east-1'
        read_capacity_units = 1
        write_capacity_units = 1

    # Primary key
    TagName = UnicodeAttribute(hash_key=True)

    # Number of a specific species
    TagValue = NumberAttribute()

    # UUID of the media file
    BirdID = UnicodeAttribute(range_key=True)