resource "aws_s3_bucket" "BirdStoreBucket" {
  bucket = "fit5225-birdstore" # name should be globally unique so change the name when you run this

  tags = {
    Name        = "BirdStore"
    Environment = "Prod"
  }
}