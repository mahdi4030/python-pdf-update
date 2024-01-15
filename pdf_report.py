from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import pdfminer
import datetime
from pathlib import Path

from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter

import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import ttk
from PIL import ImageTk, Image

from tkinter import Tk, Button, X
from tkinter.messagebox import showinfo, showwarning, showerror

import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

file_path = ''

def openFileDialog():
    global file_path
    file_path = askopenfilename(filetypes=(("PDF File", "*.pdf"), ("All Files","*.pdf")), title = "Choose a file.")
    filePathEntry.delete(0,END)
    filePathEntry.insert(0, file_path)


# To find the first page that contains Calibration Date and 'Main (Tester):' & 'Remote (Tester):' position
fp = ''
first_page = 0
found = 0
main_x = 0.0
main_y = 0.0
remote_x = 0.0
remote_y = 0.0

c_x1 = 0.0
c_y1 = 0.0
c_x2 = 0.0
c_y2 = 0.0

def parse_obj_main(objs, first_page):
    global found
    global main_x, main_y, remote_x, remote_y
    # loop over the object list
    for obj in objs:
        # if it's a textbox, print text and location
        if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            if(obj.get_text().find('Main (Tester):') != -1 or obj.get_text().find('Main (Module):') != -1):
                found=1
                for o in obj._objs:
                    if isinstance(o,pdfminer.layout.LTTextLine):
                        text = o.get_text()
                        if(text.find('Main (Tester):') != -1 or text.find('Main (Module):') != -1):
                            if text.strip():
                                for c in  o._objs:
                                    if isinstance(c, pdfminer.layout.LTChar):
                                        if(c.get_text() == ':'):
                                            main_x = c.bbox[2]
                                            main_y = c.bbox[1]
                                            break
                        elif(text.find('Remote (Tester):') != -1 or text.find('Remote (Module):') != -1):
                            if text.strip():
                                for c in  o._objs:
                                    if isinstance(c, pdfminer.layout.LTChar):
                                        if(c.get_text() == ':'):
                                            remote_x = c.bbox[2]
                                            remote_y = c.bbox[1]
                                            break
                break
        # if it's a container, recurse
        elif isinstance(obj, pdfminer.layout.LTFigure):
            if found==1:
                break
            parse_obj_main(obj._objs, first_page)


cnt = 0;
def parse_obj_calibaration_date(objs, first_page):
    global found
    global c_x1, c_y1, c_x2, c_y2, cnt
    cnt = 0
    # loop over the object list
    for obj in objs:
        # if it's a textbox, print text and location
        if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
            if (obj.get_text().find('Calibration Date:') != -1):
                for o in obj._objs:
                    if isinstance(o, pdfminer.layout.LTTextLine):
                        text = o.get_text()
                        if (text.find('Calibration Date:') != -1):
                            if text.strip():
                                for c in o._objs:
                                    if isinstance(c, pdfminer.layout.LTChar):
                                        if (c.get_text() == ':'):
                                            if (cnt == 0) :
                                                c_x1 = c.bbox[2]
                                                c_y1 = c.bbox[1]
                                                cnt = cnt + 1
                                            else:
                                                c_x2 = c.bbox[2]
                                                c_y2 = c.bbox[1]
                                                cnt = cnt + 1
                                            break
                if (cnt == 2) :
                    found = 1
                    break
        # if it's a container, recurse
        elif isinstance(obj, pdfminer.layout.LTFigure):
            if found == 1:
                break
            parse_obj_calibaration_date(obj._objs, first_page)

def change_date():
    global fp
    global main_x, main_y, remote_x, remote_y, c_x1, c_y1, c_x2, c_y2
    # Code to change the Calibration Date after find the first page and position
    packet = io.BytesIO()
    # create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)
    target_date = dateEntry.get(1.0, "end-1c")
    if main_x > 0.0 and main_y > 0.0 and remote_x > 0.0 and remote_y > 0.0 :
        can.setFillColorRGB(190/256, 220/256, 255/256)
        can.rect(main_x, main_y, 50, 10, stroke=0, fill=1)
        can.rect(remote_x, remote_y, 50, 10, stroke=0, fill=1)
        can.setFillColorRGB(0, 0, 0)
        pdfmetrics.registerFont(TTFont('ArialMT', 'font.ttf'))
        can.setFont('ArialMT', 9)
        can.drawString(main_x+2.5, main_y+2, target_date)
        can.drawString(remote_x+2.5, remote_y+2, target_date)
    elif c_x1 < 250 :
        can.setFillColorRGB(255, 255, 255)
        can.rect(c_x1, c_y1, 50, 10, stroke=0, fill=1)
        can.rect(c_x2, c_y2, 50, 10, stroke=0, fill=1)
        can.setFillColorRGB(0, 0, 0)
        pdfmetrics.registerFont(TTFont('ArialMT', 'font.ttf'))
        can.setFont('ArialMT', 7)
        can.drawString(c_x1 + 2.5, c_y1 + 1, target_date)
        can.drawString(c_x2 + 2.5, c_y2 + 1, target_date)
    elif c_x1 > 250 :
        can.setFillColorRGB(190 / 256, 220 / 256, 255 / 256)
        can.rect(c_x1, c_y1, 50, 10, stroke=0, fill=1)
        can.rect(c_x2, c_y2, 50, 10, stroke=0, fill=1)
        can.setFillColorRGB(0, 0, 0)
        pdfmetrics.registerFont(TTFont('ArialMT', 'font.ttf'))
        can.setFont('ArialMT', 9)
        can.drawString(c_x1 + 2.5, c_y2 + 2, target_date)
        can.drawString(c_x2 + 2.5, c_y2 + 2, target_date)
	
    can.save()

    #move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(fp)
    output = PdfFileWriter()

    total_page = existing_pdf.numPages
    for idx in range(total_page):
    #for idx in range(10):
        page = existing_pdf.getPage(idx)
        if idx>=(first_page-1):
            page.mergePage(new_pdf.getPage(0))
        output.addPage(page)
        progressbar['value'] = idx/total_page * 100
        r.update_idletasks()

    progressbar['value'] = 100
    r.update_idletasks()

    # finally, write "output" to a real file
    millis = round(datetime.datetime.utcnow().timestamp() * 1000)
    file_name = "converted_{}.pdf".format(millis)
    outputStream = open(file_name, "wb")
    output.write(outputStream)
    outputStream.close()
    return file_name


def convert():
    global fp, file_path, first_page, found, main_x, main_y, remote_x, remote_y, c_x1, c_y1, c_x2, c_y2
    found = 0
    first_page = 0
    main_x = 0.0
    main_y = 0.0
    remote_x = 0.0
    remote_y = 0.0
    c_x1 = 0.0
    c_y1 = 0.0
    c_x2 = 0.0
    c_y2 = 0.0
    if(file_path == ''):
        showwarning('Warning', 'Select PDF file to convert!')
        return
    
    target_date = dateEntry.get(1.0, "end-1c")
    if(target_date == ''):
        showwarning('Warning', 'Please input date')
        return

    # Open a PDF file.
    fp = open(file_path, 'rb')

    # Create a PDF parser object associated with the file object.
    parser = PDFParser(fp)

    # Create a PDF document object that stores the document structure.
    # Password for initialization as 2nd parameter
    document = PDFDocument(parser)

    # Check if the document allows text extraction. If not, abort.
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed

    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()

    # Create a PDF device object.
    device = PDFDevice(rsrcmgr)

    # BEGIN LAYOUT ANALYSIS
    # Set parameters for analysis.
    laparams = LAParams()

    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)

    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    b_open["state"] = DISABLED
    b_convert["state"] = DISABLED

    # loop over all pages in the document
    for page in PDFPage.create_pages(document):
        # read the page into a layout object
        interpreter.process_page(page)
        layout = device.get_result()
            
        # extract text from this object
        parse_obj_main(layout._objs, first_page)
        if found==1:
            break
        parse_obj_calibaration_date(layout._objs, first_page)
        if found==1:
            break
        first_page += 1

    first_page += 1
    if(found == 0):
        b_open["state"] = NORMAL
        b_convert["state"] = NORMAL
        showwarning('Warning', 'Could not find appropriate date in this pdf!')
        return

    # print("main(%f, %f), remote(%f,%f), %d" % (main_x, main_y, remote_x, remote_y, first_page))
    # print("Cal date(%f, %f), Cal date(%f,%f), %d" % (c_x1, c_y1, c_x2, c_y2, first_page))

    #to change the date
    file_name = change_date()
    progressbar['value'] = 0
    r.update_idletasks()
    fp.close()

    #button state to normal
    b_open["state"] = NORMAL
    b_convert["state"] = NORMAL
    showinfo('info', 'Convert finished, converted file name is {}'.format(file_name))

if __name__ == "__main__":
    r = Tk()
    r.resizable(width=False, height=False)
    screen_width = r.winfo_screenwidth()
    screen_height = r.winfo_screenheight()
    x = -250 + (screen_width/2)
    y = -100 + (screen_height/2)
    r.geometry('%dx%d+%d+%d' % (500, 300, x, y))

    r.title('PDF Report')

    img = ImageTk.PhotoImage(Image.open("Elektrotech Logo.png"))
    panel = Label(r, image = img)
    panel.pack()
    panel.place(x=180, y=10)

    l1 = Label(r, text='Calibration Test Results Converter', font=('Arial', 14))
    l1.pack()
    l1.place(height=25, width=500, x=0, y=80)

    #PDF file label
    l2 = Label(r, text='PDF file :')
    l2.pack()
    l2.place(height=25, width=50, x=10, y=120)

    #File path entry
    filePathEntry = Entry(r)
    filePathEntry.pack()
    filePathEntry.place(height=25, width=300, x=70, y=120)

    #pdf file open button
    b_open = Button(r)
    b_open['text'] = "Open"
    b_open['command'] = openFileDialog
    b_open.pack()
    b_open.place(height=25, width=50, x=400, y=120)

    #PDF file label
    l2 = Label(r, text='Date :')
    l2.pack()
    l2.place(height=25, width=50, x=10, y=160)

    #get date from keyfile
    date = ''
    my_file = Path("pdf_report.salt")
    if my_file.exists():
        file = open("pdf_report.salt", "r")
        contents = file.read()
        password = "xxx".encode()
        salt = b'0pdf1_report2_date3_keygen4_key5' # CHANGE THIS - recommend using a key from os.urandom(16), must be of type bytes
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password)) # Can only use kdf once

        f = Fernet(key)
        date = f.decrypt(contents.encode())
        file.close()
    else:
        showwarning('Warning', 'Program can not be run!\nPlease contact your program provider...')
        exit(1)

    #date input entry
    dateEntry = Text(r)
    dateEntry.insert('end', date.decode())
    dateEntry.config(state=DISABLED)
    dateEntry.pack()
    dateEntry.place(height=25, width=300, x=70, y=160)

    #convert button
    b_convert = Button(r)
    b_convert['text'] = "Convert"
    b_convert['command'] = convert
    b_convert.pack()
    b_convert.place(height=25, width=50, x=400, y=160)

    #progress bar
    progressbar=ttk.Progressbar(r, orient="horizontal", mode="determinate")
    progressbar.pack()
    progressbar['value'] = 0
    progressbar['maximum'] = 100
    progressbar.place(height=25, width=440, x=10, y=220)

    r.mainloop()