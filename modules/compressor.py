from PIL import Image
from io import BytesIO


def compress(img_path:str, limit_size:int =False, given_res= False):
    if not (limit_size or given_res):
        raise Exception("Compression limit not defined")

    im = Image.open(img_path)
    buffer = BytesIO()

    if not limit_size:
        limit_size = float('inf')
    
    res=im.size
    quality=100

    if given_res==1:
        given_res = res

    while True:
        """Returns the File Path after compressing"""

        if given_res:
            res= given_res

        # print(res)
        im =im.resize(res)

        im.save(buffer,'jpeg',quality=quality)
        # print(buffer.tell()/1024)

        if buffer.tell()/1024 < limit_size:
            im.save("output/final.jpg",quality=quality, optimize=True)
            print(im.size)
            break
        else: 
            quality-=5
            res = tuple(map(lambda x: int(x*0.9), res))
            buffer.seek(0,0)

    return "output/final.jpg", quality, res


if __name__ == "__main__":
    output_path = compress("input/6.jpg",100,(1500,1125))