import cv2
import numpy as np
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time
from dotenv import load_dotenv
load_dotenv()
lower_violet = np.array([130, 50, 50])
upper_violet = np.array([170, 255, 255])

def preprocess_image(img_name)->bool:
  # Convert the image to HSV color space
  img=cv2.imread(os.path.join('pre_process','input',img_name))
  hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

  # Apply thresholding to the violet color channel in HSV
  mask = cv2.inRange(hsv, lower_violet, upper_violet)

  # Apply the mask to the original image
  result = cv2.bitwise_and(img, img, mask=mask) 

  # Removing noise
  kernel = np.ones((3, 3), np.uint8)
  eroded_img = cv2.erode(result, kernel, iterations=1)

  # Gray
  gray=cv2.cvtColor(eroded_img,cv2.COLOR_BGR2GRAY)

  # Apply thresh
  thresh=cv2.threshold(gray,100,255,cv2.THRESH_BINARY)[1]
  coords=cv2.findNonZero(thresh)

  x,y,w,h=cv2.boundingRect(coords)
  if(x,y,w,h)==(0,0,0,0) or (w>500 and h>500):
      print("invalid image")
      return False


  x,y,w,h=max(x-50,0),max(y-50,0),min(w+100,thresh.shape[1]-x),min(h+100,thresh.shape[0]-y)

  # Cropped image
  cropped_img = img[ y:y+h,x:x+w]

  # Rotating the image
  if w<h:
        cropped_img=cv2.rotate(cropped_img,cv2.ROTATE_90_CLOCKWISE)
  cv2.imwrite(os.path.join('pre_process','processed',img_name),cropped_img)
  print("Image saved: Input", img_name)
  return True
  
def extract_text_from_image(image_name):
    client = ComputerVisionClient(
        endpoint="https://blindpharma.cognitiveservices.azure.com/",
        credentials=CognitiveServicesCredentials(os.environ['subscription_key'])
    )
    with open(os.path.join('pre_process','processed', image_name), "rb") as image_stream:
        # client.read_in_stream()
        job = client.read_in_stream(
            image=image_stream,
            mode="Printed",
            raw=True
        )
    operation_id = job.headers['Operation-Location'].split('/')[-1]

    image_analysis = client.get_read_result(operation_id)
    while image_analysis.status  in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
        time.sleep(1)
        image_analysis = client.get_read_result(
            operation_id=operation_id)
    print("Job completion is: {}\n".format(image_analysis.status))
    result=''
    if image_analysis.status == OperationStatusCodes.succeeded:
        for text_result in image_analysis.analyze_result.read_results:
            result='\n'.join(line.text for line in text_result.lines)
    
    # os.remove(os.path.join('pre_process','processed', image_name))
    return {'content':result}
    pass
