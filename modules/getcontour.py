import cv2
import imutils

class GetContour:
    def __init__(self, save_output =False):
        self.save_output = save_output

    def __call__(self,image ,edges):
        cnts = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

        for c in cnts:
            peri = cv2.arcLength(c,True)
            approx = cv2.approxPolyDP(c, 0.02*peri, True)

            if len(approx) == 4:
                docCnt = approx
                break

        else:
            # print("No Edges Found!!")
            raise Exception("No Edges Found!")
        
        print(docCnt)
        
        # Draw the Contour
        cv2.drawContours(image.copy(), [docCnt], -1, (0, 255, 0), 2)
        if self.save_output: cv2.imwrite("output/contour.jpg", image)
        # cv2.imshow("Outline", image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return docCnt

