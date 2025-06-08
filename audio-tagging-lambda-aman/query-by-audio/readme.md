## Query by Audio:

1. **Audio Processing**: Takes a base64 encoded image, decodes it, and saves to a temporary file
2. **Database Query**: Searches the BirdBaseIndex table for birds matching the detected species
3. **Result Intersection**: Finds birds that match ALL detected species (AND logic)
4. **Data Retrieval**: Fetches full bird records from the main BirdBase table
5. **Response**: Returns matching birds with metadata

## Expected Request Format:

```json
{
  "audio": "base64-encoded-image-data"
  "filename": "filename.extension"
}
```

## Response Format:

```json
{
  "detected_species": ["Turdus merula_Eurasian Blackbird"],
  "matching_media": [
    {
      "MediaID": "8782ca5b-763e-43b9-9194-08da6a553e32",
      "FileType": "audio",
      "MediaURL": "https://birdstore.s3.us-east-1.amazonaws.com/audio/8782ca5b-763e-43b9-9194-08da6a553e32.wav",
      "ThumbnailURL": "",
      "Uploader": ""
    }
  ]
}
```

## failed Response Format:

```json
{}
```
