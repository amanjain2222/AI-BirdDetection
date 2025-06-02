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
  
  tags = {
    Name        = "BirdStore"
    Environment = "Prod"
  }
}
