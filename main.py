from tkinter import *
from tkinter import messagebox as msg
from tkinter import filedialog
from PIL import ImageTk
import cx_Oracle
import smtplib
from email.message import EmailMessage as emsg
import random
import ssl
import os
import cv2
import numpy as np
from os import listdir
from os.path import isfile, join



flag_cap = 0

# Face_detection
def face_capture():
    # import capture
    # return
    face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml\haarcascade_frontalface_default.xml')

    # Load functions
    def face_extractor(img):
        # Function detects faces and returns the cropped face
        # If no face detected, it returns the input image
        
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)
        
        if faces == ():
            return None
        
        # Crop all faces found
        for (x,y,w,h) in faces:
            cropped_face = img[y:y+h, x:x+w]
    
        return cropped_face
    
    # Initialize Webcam
    cap = cv2.VideoCapture(0)
    count = 0
    
    # Collect 100 samples of your face from webcam input
    images = []
    while True:
    
        ret, frame = cap.read()
        if face_extractor(frame) is not None:
            count += 1
            face = cv2.resize(face_extractor(frame), (200, 200))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            face_bytes = cv2.imencode('.jpg', face)[1].tobytes()
            images.append(face_bytes)
            cv2.putText(face, str(count), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
            cv2.imshow('Face Cropper', face)
            
        else:
            print("Face not found")
            pass
        
        if cv2.waitKey(1) == 13 or count == 100: #13 is the Enter Key
            break
            
    cap.release()
    cv2.destroyAllWindows()      
    print("Collecting Samples Complete")

    global flag_cap
    flag_cap=1
    return images[len(images) // 2]

def face_lock():
    username = login_user_entry.get()

    # retrive face from database
    con=cx_Oracle.connect("my/my@//localhost:1521/xepdb1")
    cur=con.cursor()

    cur.execute("select face from user_data where username = :1",(username,))
    img = cur.fetchone()
    file_binary_from_db = img[0].read()
    nparr = np.frombuffer(file_binary_from_db, np.uint8)
    imge = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    con.commit()
    cur.close()
    con.close()


    data_path = os.path.abspath("E:\\2.Nirma University\\2nd Year\\sem-4\\sem-4_lab\\PSC\\PSC Project\\facesstore")
    onlyfiles = [f for f in listdir(data_path) if isfile(join(data_path, f))]

    # Create arrays for training data and labels
    Training_Data, Labels = [], []
    
    Training_Data.append(imge)
    Labels.append(0)

    # Create a numpy array for both training data and labels
    Labels = np.asarray(Labels, dtype=np.int32)

    # Initialize facial recognizer
    model = cv2.face.LBPHFaceRecognizer_create()

    # NOTE: For OpenCV 3.0 use cv2.face.createLBPHFaceRecognizer()

    # Let's train our model 
    model.train(np.asarray(Training_Data), np.asarray(Labels))
    print("Model trained sucessefully")

    face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml\haarcascade_frontalface_default.xml')

    def face_detector(img):
        if img is None or img.size == 0:
            return None, None
        # Convert image to grayscale
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)
        if faces == ():
            return img, []

        for (x,y,w,h) in faces:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,255),2)
            roi = img[y:y+h, x:x+w]
            roi = cv2.resize(roi, (200, 200))
        return img, roi


    # Open Webcam
    cap = cv2.VideoCapture(0)

    while True:

        ret, frame = cap.read()

        image, face = face_detector(frame)

        try:
            if image is None or image.size == 0:
                return None, None
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

            # Pass face to prediction model
            # "results" comprises of a tuple containing the label and the confidence value
            results = model.predict(face)
            confidence=0
            if results[1] < 500:
                confidence = int( 100 * (0.9 - (results[1])/400) )
                display_string = str(confidence) + '% Confident it is User'
            cv2.putText(image, display_string, (105, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255,120,150), 2)

            if confidence > 78:
                cv2.putText(image, "Unlocked", (250, 350), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
                cv2.imshow('Face Recognition', image )
                print("hiiiiiii")
                cap.release()
                cv2.destroyAllWindows()

                # connext to database for password
                connector = cx_Oracle.connect('my/my@//localhost:1521/xepdb1')
                cursor=connector.cursor()
                query='select email, pass from user_data where username=:1' #:1 etle niche tuple ma pelu aaya email aavse
                cursor.execute(query,(username,))
                recieved=cursor.fetchall() #aanu try catch karvanu se
                connector.commit()
                cursor.close()
                connector.close()
                print(recieved[0][0], username, recieved[0][1])
                login_window.destroy()
                main_window(recieved[0][0], username, recieved[0][1])
                print('hello')
                return    

                
            else:
                cv2.putText(image, "Locked", (250, 350), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)
                cv2.imshow('Face Recognition', image )

        except:
            cv2.putText(image, "No Face Found", (215, 50) , cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)
            cv2.putText(image, "Locked", (250, 350), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)
            cv2.imshow('Face Recognition', image )
            pass

        if cv2.waitKey(1) == 13: #13 is the Enter Key
            break

    cap.release()
    cv2.destroyAllWindows()     

def in_email_entry(event):
    if login_email_entry.get()=='abc123@gmail.com':
        login_email_entry.delete(0,END)
def in_login_user_entry(event):
    if login_user_entry.get()=='Username':
        login_user_entry.delete(0,END)
def in_pass_entry(event):
    if login_password_entry.get()=='Password':
        login_password_entry.delete(0,END)
def out_email_entry(event):
    if login_email_entry.get()=='':
        login_email_entry.insert(0,'abc123@gmail.com')
def out_login_user_entry(event):
    if login_user_entry.get()=='':
        login_user_entry.insert(0,'Username')
def out_pass_entry(event):
    if login_password_entry.get()=='':
        login_password_entry.insert(0,'Password')
def on_pass_entry(event):
    Login_button.invoke()
def cover():
    eye_image.config(file='csi.png')
    login_password_entry.config(show='*')
    eye_button_image.config(command=uncover)
def uncover():
    eye_image.config(file='opi.png')
    login_password_entry.config(show='')
    eye_button_image.config(command=cover)
def to_signup_page():

    def in_signup_email_entry(event):
        if signup_email_entry.get()=='E-mail':
            signup_email_entry.delete(0,END)
    def in_signup_user_entry(event):
        if signup_user_entry.get()=='Username':
            signup_user_entry.delete(0,END)
    def in_signup_pass_entry(event):
        if signup_password_entry.get()=='Password':
            signup_password_entry.delete(0,END)
    def in_signup_con_pass_entry(event):
        if signup_confirm_password_entry.get()=='Confirm Password':
            signup_confirm_password_entry.delete(0,END)
    def out_signup_email_entry(event):
        if signup_email_entry.get()=='':
            signup_email_entry.insert(0,'E-mail')
    def out_signup_user_entry(event):
        if signup_user_entry.get()=='':
            signup_user_entry.insert(0,'Username')
    def out_signup_pass_entry(event):
        if signup_password_entry.get()=='':
            signup_password_entry.insert(0,'Password')
    def out_signup_con_pass_entry(event):
        if signup_confirm_password_entry.get()=='':
            signup_confirm_password_entry.insert(0,'Confirm Password')


    user_face = None
    def Face():
        nonlocal user_face
        user_face = face_capture()

    def connect_signup():
        usr=signup_user_entry.get()
        email=signup_email_entry.get()
        if usr=='' or  email=='' or signup_password_entry.get()=='' or signup_confirm_password_entry.get=='':
            msg.showerror('ERROR','All fields are require to be filled.')
        elif usr=='Username' or email=='E-mail' or signup_password_entry.get()=='Password' or signup_confirm_password_entry.get=='Confrim Password':
            msg.showerror('ERROR','All fields are require to be filled.')
        elif signup_password_entry.get() != signup_confirm_password_entry.get():
            msg.showerror('ERROR','Both pass must be same.')
        elif '@gmail.com' not in email:
            msg.showerror('ERROR','Enter a valid email.')
        elif flag_cap == 0:
            msg.showerror('ERROR','Please capture your Face!')
        else:
            connector = cx_Oracle.connect('my/my@//localhost:1521/xepdb1')
            cursor=connector.cursor()

            password=signup_password_entry.get()

            query='select pass from user_data where email=:1' #:1 etle niche tuple ma pelu aaya email aavse
            cursor.execute(query,(email,))
            recieve=cursor.fetchall() #aanu try catch karvanu se

            query='select pass from user_data where username=:1' #:1 etle niche tuple ma pelu aaya email aavse
            cursor.execute(query,(usr,))
            recieve1=cursor.fetchall() #aanu try catch karvanu se
            
            if len(recieve)!=0:
                msg.showerror("WARNING","Email is already used once\nTry with other Email")
            elif len(recieve1)!=0:
                msg.showerror("WARNING","Username is already used once\nTry with other Email")
            else:
                cursor.execute('insert into user_data(email,username,pass,face) values(:1,:2,:3, :4)',(email,usr,password,user_face))
                cursor.execute(f"CREATE TABLE {usr} (filename VARCHAR2(100) PRIMARY KEY,filedata BLOB)")
                msg.showinfo("Congratulation",'You are Succefully Registered')
                connector.commit()
                cursor.close()
                connector.close()
                signup_window.destroy()

    


    signup_window=Toplevel(login_window)

    signup_window.geometry('671x577+300+25')
    signup_window.resizable(False,False)

    signup_window.title('Signup page')

    back_ground_image=ImageTk.PhotoImage(file='bgg.jpg')
    back_ground_label=Label(signup_window,image=back_ground_image)
    back_ground_label.place(x=0,y=0)

    Label(signup_window,text='Secure File Manager',font=('Microsoft Yahei UI Light',20,'bold'),bg='white',fg='red').place(x=200,y=150)


    signup_user_entry=Entry(signup_window,width=25,font=('Microsoft Yahei UI Light',11,'bold')) #entry()class is used for the input space.
    signup_user_entry.place(x=200,y=200)
    signup_user_entry.insert(0,'Username')
    signup_user_entry.bind('<FocusIn>',in_signup_user_entry)
    signup_user_entry.bind('<FocusOut>',out_signup_user_entry)
    Frame(signup_window,width=230,height=2,bg='blue').place(x=200,y=222)


    signup_email_entry=Entry(signup_window,width=25,font=('Microsoft Yahei UI Light',11,'bold')) #entry()class is used for the input space.
    signup_email_entry.place(x=200,y=250)
    signup_email_entry.insert(0,'E-mail')
    signup_email_entry.bind('<FocusIn>',in_signup_email_entry)
    signup_email_entry.bind('<FocusOut>',out_signup_email_entry)
    Frame(signup_window,width=230,height=2,bg='blue').place(x=200,y=272) #under line with blue color

    signup_password_entry=Entry(signup_window,width=25,font=('Microsoft Yahei UI Light',11,'bold')) #entry()class is used for the input space.
    signup_password_entry.place(x=200,y=300)
    signup_password_entry.insert(0,'Password')
    signup_password_entry.bind('<FocusIn>',in_signup_pass_entry)
    signup_password_entry.bind('<FocusOut>',out_signup_pass_entry)
    Frame(signup_window,width=230,height=2,bg='blue').place(x=200,y=322) #under line with blue color

    signup_confirm_password_entry=Entry(signup_window,width=25,font=('Microsoft Yahei UI Light',11,'bold')) #entry()class is used for the input space.
    signup_confirm_password_entry.place(x=200,y=350)
    signup_confirm_password_entry.insert(0,'Confirm Password')
    signup_confirm_password_entry.bind('<FocusIn>',in_signup_con_pass_entry)
    signup_confirm_password_entry.bind('<FocusOut>',out_signup_con_pass_entry)
    Frame(signup_window,width=230,height=2,bg='blue').place(x=200,y=372) #under line with blue color
    
    face_button=Button(signup_window,text='Face',font=('Open Sans',10,'bold'),bg='#1e90ff',fg='white',activebackground='green',width=17,command= Face)
    face_button.place(x=400,y=350)

    signup_button=Button(signup_window,text='Sign up',font=('Open Sans',16,'bold'),bg='#1e90ff',fg='white',activebackground='green',width=17,command=connect_signup)
    signup_button.place(x=200,y=390)


    signup_window.mainloop()

def connect_login():
    user=login_user_entry.get()
    email=login_email_entry.get()
    if user=='' or email=='' or login_password_entry.get()=='':
        msg.showerror('ERROR','All fields are require to be filled.')
    elif user=='Username' or email=='E-mail' or login_password_entry.get()=='Password':
        msg.showerror('ERROR','All fields are require to be filled.')
    elif '@gmail.com' not in email:
        msg.showerror('ERROR','Enter a valid email.')
    else:
        # local_host = cx_Oracle.makedsn('DESKTOP-6CLFP5M', '1521', 'XE') 
        connector = cx_Oracle.connect('my/my@//localhost:1521/xepdb1')
        cursor=connector.cursor()

        email=login_email_entry.get()
        password=login_password_entry.get()

        query='select pass from user_data where email=:1' #:1 etle niche tuple ma pelu aaya email aavse
        cursor.execute(query,(email,))
        recieve=cursor.fetchall()

        flag=False
        if(len(recieve)==0):
            msg.showerror("ERROR",'User does not exist!')
        else:
            pswrd=''
            pswrdline=recieve[0]
            for ele in pswrdline:
                if(ele!='(' and ele!=')' and ele!=',' and ele!="'"): #password aa form ma store hoy --> [(pass,)]
                    pswrd+=ele

            if(password==pswrd):
                msg.showinfo("Success","Login successfully")
                flag=True
                #import window here
            else:
                msg.showerror('error',"wrong Password ")
        connector.commit()
        cursor.close()
        connector.close()
        if flag==True:
            login_window.destroy()
            main_window(email,user,password)
            # a page will be imported

class main_window:
        def __init__(self, email,username, password):
            connection = cx_Oracle.connect('my/my@//localhost:1521/xepdb1')
            def select_file():
                file_path = filedialog.askopenfilename()
                if file_path:
                    # read file data as binary
                    with open(file_path, 'rb') as file:
                        file_binary = file.read()
                    # get file name from file path
                    file_name = file_path.split('/')[-1]
                    # insert file into database
                    insert_file(connection, file_name, file_binary)

            def insert_file(connection, file_name, file_binary):
                cursor = connection.cursor()
                try:
                    cursor.execute(f"""
                        INSERT INTO {self.username} (filename, filedata)
                        VALUES (:filename, :filedata)
                    """, [file_name, file_binary])
                    cursor.close()
                    connection.commit()
                except Exception:
                    msg.showerror("ERROR","Error occured while file uploading")
                display_files()
            

            self.master = Tk()
            self.master.geometry('612x612')
            self.master.title("Main Window")
            self.master.resizable(0,0)
            back_ground_image=ImageTk.PhotoImage(file='bgg1.jpg') #variable for background image
            back_ground_label=Label(self.master,image=back_ground_image)
            back_ground_label.place(x=0,y=0)
            self.email = email
            self.password = password
            self.username=username

            listbox = Listbox(self.master, font=('Open Sans', 12))
            listbox.place(relx=0.36, rely=0.4, anchor=CENTER, width=200, height=200)

            scrollbar_y = Scrollbar(listbox, orient=VERTICAL)
            scrollbar_y.pack(side=RIGHT, fill=Y)
            scrollbar_y.config(command=listbox.yview)

            scrollbar_x = Scrollbar(listbox, orient=HORIZONTAL)
            scrollbar_x.pack(side=BOTTOM, fill=X)
            scrollbar_x.config(command=listbox.xview)

            listbox.config(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)

            def display_files():

                # retrieve all file names from the database
                cursor = connection.cursor()
                cursor.execute(f"""
                    SELECT filename FROM {self.username}
                """)
                file_names = cursor.fetchall()
                if listbox.size()!=0:
                    listbox.delete(0,END)
                # create a listbox to display the file names
                for file_name in file_names:
                    listbox.insert(END, file_name[0])
                listbox.place(x=100,y=50)

                # add a button to open the selected file
            def open_file():
                if listbox.curselection():
                    file_name = listbox.get(listbox.curselection())
                    # Retrieve the file from the database and compare its contents with the original file
                    cursor = connection.cursor()
                    cursor.execute(f"""
                        SELECT filedata FROM {self.username} WHERE filename = :filename
                    """, [file_name])
                    result = cursor.fetchone()
                    file_binary_from_db = result[0].read()
                    cursor.close()
                    with open(file_name, 'wb') as file:
                        file.write(file_binary_from_db)
                    open_file1(file_name)
                else:
                    msg.showerror("ERROR", "Please select a file to open")

            def open_file1(filename):
                """
                Opens the file with its default application
                """
                try:
                    os.startfile(filename)
                except AttributeError:
                    try:
                        os.system('open "{}"'.format(filename))
                    except:
                        print("Unable to open file: {}".format(filename))

            def delete_file():
                if listbox.curselection():
                    file_name = listbox.get(listbox.curselection())
                    cursor = connection.cursor()
                    try:
                        cursor.execute(f"""
                            DELETE FROM {self.username}
                            WHERE filename = :filename
                        """, [file_name])
                        cursor.close()
                        connection.commit()
                        display_files()
                    except Exception:
                        msg.showerror("ERROR","Error occurred while deleting file")
                else:
                    msg.showerror("ERROR", "Please select a file to delete")


            # Create a menu bar
            menubar = Menu(self.master)
            self.master.config(menu=menubar)

            # Create a File menu with Open, Save, and Exit options
            file_menu = Menu(menubar, tearoff=False)
            menubar.add_cascade(label="File", menu=file_menu)
            file_menu.add_command(label="Add", command=select_file)
            file_menu.add_command(label="Open", command=open_file)
            file_menu.add_command(label="Delete", command=delete_file)
            file_menu.add_separator()
            file_menu.add_command(label="Exit", command=self.master.quit)
            
            upload_button = Button(self.master, text='Upload File', command=select_file)
            upload_button.place(x=5, y=5)
            open_button = Button(self.master, text='Open File', command=open_file)
            open_button.place(x=75,y=5)
            delete_button = Button(self.master, text='Delete File',command=delete_file)#command baki
            delete_button.place(x=135,y=5)
            display_files()


            self.master.mainloop()
        
def forget_password():

    otp=str(random.randint(100000,1000000))
    def sent_otp():
        connector = cx_Oracle.connect('my/my@//localhost:1521/xepdb1')
        cursor=connector.cursor()
        if forget_email_entry.get()=='':
            msg.showwarning("WARNING","Email must be filled.")
        elif '@gmail.com' not in forget_email_entry.get():
            msg.showwarning("WARNING","Enter valid email.")
        else:
            email=forget_email_entry.get()
            txt='select pass from user_data where email=:1'
            cursor.execute(txt,(email,))
            recieve=cursor.fetchall()

            if(len(recieve)==0):
                msg.showerror('ERROR','User does not exist!')
            else:
                email_sender='yagnikvasoya2511@gmail.com'
                email_password="rbixzhuisvvuqhdk" #google generated password
                email_receiver=email

                subject='OTP Varification'
                body=otp

                em=emsg()
                em['From']=email_sender
                em['To']=email_receiver
                em['Subject']=subject
                em.set_content(body)
                context1=ssl.create_default_context()

                try:
                    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context1) as smtp:
                        smtp.login(email_sender,email_password)
                        smtp.sendmail(email_sender,email_receiver,em.as_string())
                except Exception as exp:
                    print("Error occured",exp)
        connector.commit()
        cursor.close()
        connector.close()
    def verify():
        OTP=otp_entry.get()
        if otp==OTP:
            msg.showinfo("Varified","Varification Successfull")

            Label(forget_window,text='Password.',font=('Microsoft Yahei UI Light',10,'bold'),bg='white',fg='black',width=7).place(x=123,y=340)
            forget_password_entry=Entry(forget_window,width=25,font=('Microsoft Yahei UI Light',11,'bold')) #entry()class is used for the input space.
            forget_password_entry.place(x=200,y=340)
            Frame(forget_window,width=230,height=2,bg='blue').place(x=200,y=362)

            Label(forget_window,text='Confirm\nPassword.',font=('Microsoft Yahei UI Light',10,'bold'),bg='white',fg='black',width=7).place(x=123,y=370)
            forget_confirm_entry=Entry(forget_window,width=25,font=('Microsoft Yahei UI Light',11,'bold')) #entry()class is used for the input space.
            forget_confirm_entry.place(x=200,y=380)
            Frame(forget_window,width=230,height=2,bg='blue').place(x=200,y=402)

            def submit():
                # local_host = cx_Oracle.makedsn('DESKTOP-6CLFP5M', '1521', 'XE')
                connector = cx_Oracle.connect('my/my@//localhost:1521/xepdb1')
                cursor=connector.cursor()
                email=forget_email_entry.get()
                password=forget_password_entry.get()
                confirm_password=forget_confirm_entry.get()
                if password=='' or confirm_password=='':
                    msg.showwarning("WARNING",'Both fields must be filled!')
                elif password!=confirm_password:
                    msg.showwarning("WARNING",'Both password must match!')
                else:
                    query="update user_data set pass=:1 where email=:2"
                    cursor.execute(query,(password,email))
                    msg.showinfo('OK','Password updated succefully.')
                connector.commit()
                cursor.close()
                connector.close()
                forget_window.destroy()
                # import login

            submit_button=Button(forget_window,text='Submit',font=('Open Sans',16,'bold'),bg='#1e90ff',fg='white',activebackground='green',width=11,command=submit)
            submit_button.place(x=240,y=420)

        else:
            msg.showerror("ERROR","Verification failed")

    forget_window=Toplevel()

    forget_window.geometry('671x577+300+25')
    forget_window.resizable(False,False) 

    forget_window.title('Forget Password!')

    back_ground_image=ImageTk.PhotoImage(file='bgg.jpg') 
    back_ground_label=Label(forget_window,image=back_ground_image)
    back_ground_label.place(x=0,y=0) 

    Label(forget_window,text='E-mail.',font=('Microsoft Yahei UI Light',10,'bold'),bg='white',fg='black',width=7).place(x=123,y=140)
    forget_email_entry=Entry(forget_window,width=25,font=('Microsoft Yahei UI Light',11,'bold')) 
    forget_email_entry.place(x=200,y=140)
    Frame(forget_window,width=230,height=2,bg='blue').place(x=200,y=162)

    OTP_button=Button(forget_window,text='Send OTP',font=('Open Sans',16,'bold'),bg='#1e90ff',fg='white',activebackground='green',width=11,command=sent_otp)
    OTP_button.place(x=240,y=180)

    Label(forget_window,text='OTP',font=('Microsoft Yahei UI Light',10,'bold'),bg='white',fg='black',width=7).place(x=123,y=240)
    otp_entry=Entry(forget_window,width=25,font=('Microsoft Yahei UI Light',11,'bold')) 
    otp_entry.place(x=200,y=240)
    Frame(forget_window,width=230,height=2,bg='blue').place(x=200,y=262)

    varify_button=Button(forget_window,text='Verify',font=('Open Sans',16,'bold'),bg='#1e90ff',fg='white',activebackground='green',width=11,command=verify)
    varify_button.place(x=240,y=280)

    forget_window.mainloop()

login_window=Tk() #creating a login_window using Tk() class

login_window.geometry('671x577+300+25')
login_window.resizable(False,False) #login_window size gets fixed value of row and column can't be change.

login_window.title('Login page')

back_ground_image=ImageTk.PhotoImage(file='bgg.jpg') #variable for background image
back_ground_label=Label(login_window,image=back_ground_image)
back_ground_label.place(x=0,y=0) #placing bgimage at 0,0 cordinate

Label(login_window,text='Secure File Manager',font=('Microsoft Yahei UI Light',20,'bold'),bg='white',fg='red').place(x=200,y=150)

Label(login_window,text='Username.',font=('Microsoft Yahei UI Light',10,'bold'),bg='white',fg='black',width=7).place(x=123,y=200)
login_user_entry=Entry(login_window,width=25,font=('Microsoft Yahei UI Light',11,'bold')) #entry()class is used for the input space.
login_user_entry.place(x=200,y=200)
login_user_entry.insert(0,'Username')
login_user_entry.bind('<FocusIn>',in_login_user_entry)
login_user_entry.bind('<FocusOut>',out_login_user_entry)
Frame(login_window,width=230,height=2,bg='blue').place(x=200,y=222)

Label(login_window,text='E-mail.',font=('Microsoft Yahei UI Light',10,'bold'),bg='white',fg='black',width=7).place(x=123,y=250)
login_email_entry=Entry(login_window,width=25,font=('Microsoft Yahei UI Light',11,'bold')) #entry()class is used for the input space.
login_email_entry.place(x=200,y=250)
login_email_entry.insert(0,'abc123@gmail.com')
login_email_entry.bind('<FocusIn>',in_email_entry)
login_email_entry.bind('<FocusOut>',out_email_entry)
Frame(login_window,width=230,height=2,bg='blue').place(x=200,y=272) #under line with blue color

Label(login_window,text='Password.',font=('Microsoft Yahei UI Light',10,'bold'),bg='white',fg='black').place(x=123,y=300)
login_password_entry=Entry(login_window,width=25,font=('Microsoft Yahei UI Light',11,'bold'),show='*') #entry()class is used for the input space.
login_password_entry.place(x=200,y=300)
login_password_entry.insert(0,'Password')
login_password_entry.bind('<FocusIn>',in_pass_entry)
login_password_entry.bind('<FocusOut>',out_pass_entry)
login_password_entry.bind("<Return>",on_pass_entry)
Frame(login_window,width=230,height=2,bg='blue').place(x=200,y=322) #under line with blue color

eye_image=PhotoImage(file='csi.png')
eye_button_image=Button(login_window,image=eye_image,command=uncover) #4th argument can be given as cursor
eye_button_image.place(x=430,y=300)

forget_button=Button(login_window,text='Forgot Password?',bd=0,bg='white',fg='blue',activebackground='yellow',command=forget_password)
forget_button.place(x=400,y=340)
Frame(login_window,width=100,height=2,bg='blue').place(x=400,y=360) #under line with blue color

lock_button=Button(login_window,text='Face Lock',bd=0,bg='white',fg='blue',activebackground='yellow',command=face_lock)
lock_button.place(x=200,y=340)

Login_button=Button(login_window,text='Login',font=('Open Sans',16,'bold'),bg='#1e90ff',fg='white',activebackground='green',width=19,command=connect_login)
Login_button.place(x=200,y=380)

signup_button=Button(login_window,text='Create New Account',font=('Open Sans',16,'bold'),bg='#1e90ff',fg='white',activebackground='green',width=19,command=to_signup_page)
signup_button.place(x=200,y=440)

login_window.mainloop()
