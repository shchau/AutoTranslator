import boto3
import io
from PIL import Image, ImageDraw, ImageFont
from googletrans import Translator

if __name__ == "__main__":

    # Change the value of bucket to the S3 bucket that contains your image file.
    # Change the value of photo to your image file name.
    bucket='manga-page-bucket'
    photo='OPM-CH03-PG04.jpg'

    client=boto3.client('rekognition')
                        
    # Load image from S3 bucket
    s3_connection = boto3.resource('s3')
    s3_object = s3_connection.Object(bucket,photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=Image.open(stream)
    
    # Call DetectText
    response=client.detect_text(Image={'S3Object':{'Bucket':bucket,'Name':photo}})

    imgWidth, imgHeight = image.size  
    draw = ImageDraw.Draw(image)  


    textDetections=response['TextDetections']
    
    translator= Translator()
    fnt = ImageFont.truetype("arial.ttf", 10)
    
    for text in textDetections:
            if text['Type'] == "WORD":
                
                # Get bounding box
                box = text["Geometry"]['BoundingBox']
                left = imgWidth * box['Left']
                top = imgHeight * box['Top']
                width = imgWidth * box['Width']
                height = imgHeight * box['Height']
                
                # Store words and positions of words
                line = text["DetectedText"]
                textResult = [line, [left, top]]
                
                # Draw white rectangle to cover over original text. 
                draw.rectangle(((left, top), (left + width, top + height)), fill="white")
                
                # Translate line and place back in
                translatedLine = translator.translate(line).text
                draw.multiline_text((left, top), translatedLine, font=fnt, fill=(0, 0, 0))
                
    image.show()
    image.save("RESULT.PNG")
    
