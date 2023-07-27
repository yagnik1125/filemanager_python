# Secure File Manager

This program requires several Python modules to run properly. To download these modules, follow these instructions:

1. Open a terminal or command prompt.
2. Type `pip install tkinter` and press Enter to install the tkinter module.
3. Type `pip install pillow` and press Enter to install the PIL module.
4. Type `pip install cx_Oracle` and press Enter to install the cx_Oracle module.
5. Type `pip install smtplib` and press Enter to install the smtplib module.
6. Type `pip install opencv-python` and press Enter to install the OpenCV module.
7. Type `pip install numpy` and press Enter to install the NumPy module.

or you can run  `pip install numpy tkinter cx_Oracle pillow smtplib opencv-python` in your terminal.  

If you are using **anaconda** the run `conda install numpy tkinter cx_Oracle pillow smtplib opencv-python` in your terminal.   

>Note: 
>1. Some modules may have additional dependencies that also need to be installed.
>2. We have used oracle database to store the data, so to run this program properly you first have to setup oracle database in your device and run `data.sql` script in oracle database.

# How to Run
Once you've installed all the required modules, you can run the program by opening a terminal or command prompt, navigating to the directory where the program is located, and typing `python main.py` and press Enter.


#  Features
The features of this project include:

*  Secure storage of files in an Oracle database
* User authentication using face detection
* Encryption of files to protect them from unauthorized access(Oracle database)
* User-friendly interface for easy file management
* Multiple Users can store and access files form a single device


# Team Details
This project was developed by
* SHRUT (21bce314@nirmauni.ac.in)
* YAGNIK (21bce321@nirmauni.ac.in)
* ANKUSH (21bce319@nirmauni.ac.in)