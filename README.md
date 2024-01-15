1.	Install python 3.5 or above.
You can check installed python version with cmd command “python -V”.
2.	When you run pdf_report.py and pdf_date_keygen.py with “python pdf_report.py” or “python pdf_date_keygen.py” you will get error messages because you don’t install python 3rd party libraries.
You need to install all 3rd party libraries with e.g “pip install PDFParser”.
3.	Place the “font.ttf” and “Elektrotech Logo.png” at the same folder with “pdf_report.py”.
4.	You can run pdf_report and keygen with “python pdf_report.py” or ”python pdf_date_keygen.py”.
5.	If 1~4 steps are all works well you can build the python script to executable program.
6.	To build the executable program you need to install PyInstaller with the cmd command “pip install pyinstaller”
7.	After pyinstaller installed successfully you can build the python file with the command “pyinstaller --windowed -d pdf_report.py” or “pyinstaller --windowed -d pdf_date_keygen.py”
Then it makes 3 folder, and the dist folder is final result.
You need to place “font.ttf”, “Elektrotech Logo.png”, and date key generated *.salt file at the same folder with pdf_report.exe.
8.	Then you can run pdf_report.exe and it will work well.
