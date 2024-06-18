import cv2
import numpy as np

class WarpPerspective:
    def __init__(self, output=False):
        self.save_output = output

    def __call__(self, image, contour):
        
        pts = contour.reshape(4,2)
        rect= np.zeros((4,2), dtype="float32")
        
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]


        (tl, tr, br, bl) =rect
        widthA = np.sqrt( (br[0]-bl[0])**2 + (br[1]-bl[1])**2 )
        widthB = np.sqrt( (tr[0]-tl[0])**2 + (tr[1]-tl[1])**2 )

        heightA = np.sqrt( (tr[0]-br[0])**2 + (tr[1]-br[1])**2 )
        heightB = np.sqrt( (tl[0]-bl[0])**2 + (tl[1]-bl[1])**2 )


        maxWidth = max(int(widthA), int(widthB))
        maxHeight = max(int(heightA), int(heightB))

        dest = np.array([
            [0,0],
            [maxWidth-1, 0],
            [maxWidth-1, maxHeight-1],
            [0, maxHeight-1]
        ], dtype='float32')

        M = cv2.getPerspectiveTransform(rect,dest)
        warp = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

        if self.save_output:    cv2.imwrite("output/final.jpg",warp)
        # cv2.imshow("output",warp)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return warp
    