import cv2

class Resizer:
    """ Resizes the Image """
    def __init__(self, max_height, save_output = False):
        self.max_height = max_height
        self.save_output= save_output

    def __call__(self, image):
        
        if image.shape[0] <= self.max_height : return image

        ratio = round(self.max_height/image.shape[0] ,3)
        width = int(image.shape[1] * ratio)

        resized = cv2.resize(image, (width, self.max_height), interpolation=cv2.INTER_AREA)

        if self.save_output: cv2.imwrite(r'output/resized.jpg',resized)
        # cv2.imshow("resized",resized)
        # cv2.waitKey(0)
        return resized

