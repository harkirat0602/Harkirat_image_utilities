from modules.denoise import *
from modules.edgedetector import *
from modules.getcontour import *
from modules.resize import *
from modules.threshold import *
from modules.warp import *
import sys


class DocScan:
    def __init__(self, output=False, height:int =1000, final_output =True) -> None:
        self.output = output
        self.height = height
        self.final_output = final_output
    
    def scan(self, image):
        resizer = Resizer(self.height)
        image = resizer(image)

        denoiser = FastDenoise(save_output=self.output,strength=4)
        image = denoiser(image)

        edgedetector = GetEdges(save_output=self.output)
        edges = edgedetector(image)

        getcontour = GetContour(save_output=self.output)
        contour = getcontour(image, edges)

        warper = WarpPerspective(output=self.output)
        final_result = warper(image,contour)

        final_dest = "output/final.jpg"
        if self.final_output: cv2.imwrite(final_dest, final_result)
        return final_result, final_dest


if __name__ == "__main__":
    try:
        image = cv2.imread(sys.argv[1])

        scanner = DocScan()
        scanner.scan(image)
    except Exception as e:
        print("Error Occured")
        print(e)
