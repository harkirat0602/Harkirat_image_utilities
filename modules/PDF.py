from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
import PyPDF2


def generate_pdf(folder_path:str,output:str="output.pdf",add_watermark:bool=True,custom_watermark:str=None):
    c = canvas.Canvas(output)

    page_number=0
    for file in os.scandir(folder_path):
        try:
            if file.is_file():
                image = ImageReader(file.path)
                img_w, img_h = image.getSize()

                c.setPageSize((img_w,img_h))
                c.drawImage(file.path,0,0,img_w,img_h)
                
                c.setFontSize(18)
                page_number+=1
                if add_watermark:
                    c.drawString(20,20,f"Page: {page_number}",)

                if custom_watermark:
                    c.drawString(img_w-5-c.stringWidth(custom_watermark),img_h-20,custom_watermark,)

                c.showPage()


        except:
            continue

    c.save()


def password_protect(file_path,file_name,password):
    with open(file_path+file_name, "rb") as unprotected:
        reader = PyPDF2.PdfReader(unprotected)
        writer = PyPDF2.PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(password)

        output_name = file_path+file_name.split(".")[-2]+"_protected.pdf"
        with open(output_name,"wb") as protected:
            writer.write(protected)
        return output_name




if __name__ == "__main__":
    generate_pdf("D:\Repositories\Harkirat_Image_Utilities\input",custom_watermark="Harkirat`s Image Utilities")
    password_protect("","output.pdf","Harkirat123")