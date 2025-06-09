## Query by Image:

1. **Image Processing**: Takes a base64 encoded image, decodes it, and saves to a temporary file
2. **AI Detection**: Uses YOLO model to detect bird species in the image
3. **Database Query**: Searches the BirdBaseIndex table for birds matching the detected species
4. **Result Intersection**: Finds birds that match ALL detected species (AND logic)
5. **Data Retrieval**: Fetches full bird records from the main BirdBase table
6. **Response**: Returns matching birds with metadata

## Expected Request Format:

```json
{
  "image": "base64-encoded-image-data"
}
```

## Response Format:

```json
{
  "message": "Succeeded! Got 1 records",
  "results": [
    {
      "MediaId": "uuid",
      "FileType": "image",
      "MediaURL": "s3-url",
      "ThumbnailURL": "thumbnail-url",
      "Uploader": "username"
    }
  ]
}
```
