resource "aws_s3_bucket" "BirdStoreBucket" {
  bucket = "fit5225-birdstore"

  tags = {
    Name        = "BirdStore"
    Environment = "Prod"
  }
}