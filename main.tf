resource "aws_s3_bucket" "BirdStoreBucket" {
  bucket = "fit5225-birdstore" # name should be globally unique so change the name when you run this

  tags = {
    Name        = "BirdStore"
    Environment = "Prod"
  }
}

#
resource "aws_dynamodb_table" "UploadedFilesTable" {
  name = "UploadedFiles" # the name of the table in DynamoDB
  billing_mode = "PAY_PER_REQUEST" # on-demand billing mode
  hash_key = "FileId"

  attribute {
    name = "FileId" # The UUID for the file? To be discussed
    type = "S"
  }

  attribute {
    name = "FileType" # Image/Video/Audio
    type = "S"
  }

  attribute {
    name = "FileUrl" # The URL of full-sized image
    type = "S"
  }

  attribute {
    name = "FileThumbUrl" # The URL of thunbnail image
    type = "S"
  }

  attribute {
    name = "FileTags" # {"crow": 3}
    type = "M"
  }

  attribute {
    name = "UploadedDate"
    type = "S"
  }

  tags = {
    Name        = "BirdStore"
    Environment = "Prod"
  }
}
