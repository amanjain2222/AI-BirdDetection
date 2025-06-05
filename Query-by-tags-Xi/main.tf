resource "aws_s3_bucket" "BirdStoreBucket" {
  bucket = "fit5225-birdstore" # name should be globally unique so change the name when you run this

  tags = {
    Name        = "BirdStore"
    Environment = "Prod"
  }
}

#
resource "aws_dynamodb_table" "BirdBaseTable" {
  name = "BirdBase" # the name of the table in DynamoDB
  billing_mode = "PAY_PER_REQUEST" # on-demand billing mode
  hash_key = "BirdID"

  attribute {
    name = "BirdID" # UUID 
    type = "S"
  }
  
  tags = {
    Name        = "BirdStore"
    Environment = "Prod"
  }
}

resource "aws_dynamodb_table" "BirdBaseIndexTable" {
  name = "BirdBaseIndex" # the name of the table in DynamoDB
  billing_mode = "PAY_PER_REQUEST" # on-demand billing mode
  hash_key = "TagName"
  range_key = "BirdID"

  attribute {
    name = "TagName" # hash key
    type = "S"
  }

  attribute {
    name = "BirdID" # range key 
    type = "S"
  }

  tags = {
    Name        = "BirdStore"
    Environment = "Prod"
  }
}
