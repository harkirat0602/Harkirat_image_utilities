import cv2

class FastDenoise:
    """This Denoise the provided image by using the fastNlMeansDenoising method"""

    def __init__(self, strength=False, save_output=False):
        self.strength = strength
        self.save_output = save_output

    def __call__(self, image):
        
        if self.strength:
            denoised = cv2.fastNlMeansDenoisingColored(image,h=self.strength)
            if self.save_output:
                cv2.imwrite(r"output/denoise.jpg",denoised)
        else:
            for strength in range(11):
                denoised = cv2.fastNlMeansDenoisingColored(image,h=strength)
                if self.save_output:
                    cv2.imwrite(f"output//denoise_{strength}.jpg",denoised)

        return denoised
