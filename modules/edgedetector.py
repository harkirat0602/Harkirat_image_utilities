import cv2

class GetEdges:
    def __init__(self, contour1=75, contour2=200, save_output= False):
        self.contour1 = contour1
        self.contour2 = contour2
        self.save_output = save_output

    def __call__(self, image):
        
        # greyimage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        greyimage = cv2.GaussianBlur(image, (5,5), 0)

        edges = cv2.Canny(greyimage, self.contour1, self.contour2)

        if self.save_output: cv2.imwrite(r"output/edges.jpg", edges)
        # cv2.imshow("original",image)
        # cv2.imshow("edges", edges)
        # cv2.waitKey(0)
        return edges
    