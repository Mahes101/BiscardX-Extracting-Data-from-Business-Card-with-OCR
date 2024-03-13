# IMPORTING  PYTHON LIBRARIES 
import streamlit as st
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from annotated_text import annotated_text
import pymysql as sql
import pandas as pd
import numpy as np
from PIL import Image
import re
# IMPORTING EASYOCR LIBRARY.
import easyocr
# IMPORTING CV LIBRARY.
import cv2
#IMPORTING OS LIBRARY
import os

# ASSIGNING OS ENVIRONMENT DUPLICATE KEY.
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

# ICON FOR PAGE
icon = Image.open("C:\\Users\\mahes\\Downloads\\logo.jpg")
# SETTING PAGE CONFIGURATION.
st.set_page_config(page_title="BizCardX: Extracting Business Card Data with OCR | By UMAMAHESWARI S",
                   page_icon=icon,
                   layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items={'About': """# This OCR app is created by *UMAMAHESWARI S*!"""})
st.markdown("<h1 style='text-align: center; color: white;'>BizCardX: Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)

#BACKGROUND COLOR SETTING USING CSS ###
pg_bg_img = """
   <style>
   [data-testid="stAppViewContainer"]{
        background-color:#004225;
   }
   [data-testid="stHeader"]{
       background-color:#004225;
   }
   [data-testid="stSidebarContent"]{
       background-color:#004225;  
   }
   [data-testid="stSelectBox"]{
       background-color:#3d2b1f;
   }
   [data-testid="element-container"]{
       font-color:#3d2b1f;
   }
   [data-testid="stButton"]{
       font-color:#000000;
       font-size:20px;
       border-color: #ffffff;
       box-shadow: none;
       color: #21abcd
       
   }
   </style>
   """
st.markdown(pg_bg_img,unsafe_allow_html=True)

#CONNECTION STRING EXECUTION FOR MYSQL.
mydb = sql.connect(host="localhost",
                   user="root",port=3306,
                   password="admin@123",
                   database= "youtube_db"
                  )
mycur = mydb.cursor()  

# CODING FOR OPTION MENU IN STREAMLIT 
with st.sidebar:
    st.image(Image.open("C:\\Users\\mahes\\Downloads\\Data-Extraction.jpg"))
    choice_op = option_menu(menu_title ="Main Menu", 
                            options=["Home","Upload and Extract Data","Modify Or Delete Data"], 
                           icons=["house-fill","Upload","tools"],
                           default_index=0,
                           orientation="vertical",
                           styles={"nav-link": {"font-size": "30px", "text-align": "centre", "margin": "0px", 
                                                "--hover-color": "#cc5500"},
                                   "icon": {"font-size": "30px"},
                                   "container" : {"max-width": "6000px"},
                                   "nav-link-selected": {"background-color": "#ffc1cc"},})
    
## INITIALIZING  EasyOCR READER
reader = easyocr.Reader(['en'])

## CREATING  A DATABASE IN MYSQL CALLED bizcardx_db

mycur.execute("CREATE DATABASE IF NOT EXISTS bizcardx_db")
mycur.execute("USE bizcardx_db")

# CREATING A TABLE IN MYSQL DATABASE FOR STORING DATA WHICH IS EXTRACTED.
mycur.execute('''CREATE TABLE IF NOT EXISTS card_data
                   (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    company_name TEXT,
                    card_holder TEXT,
                    designation TEXT,
                    mobile_number VARCHAR(50),
                    email TEXT,
                    website TEXT,
                    area TEXT,
                    city TEXT,
                    state TEXT,
                    pin_code VARCHAR(10),
                    image LONGBLOB
                    )''')

def save_card(uploaded_card):
    with open(os.path.join("Biscard data", uploaded_card.name), "wb") as f:
        f.write(uploaded_card.getbuffer())   

def image_preview(image,res): 
    for (bbox, text, prob) in res: 
        # unpack the bounding box
        (tl, tr, br, bl) = bbox
        tl = (int(tl[0]), int(tl[1]))
        tr = (int(tr[0]), int(tr[1]))
        br = (int(br[0]), int(br[1]))
        bl = (int(bl[0]), int(bl[1]))
        cv2.rectangle(image, tl, br, (0, 255, 0), 2)
        cv2.putText(image, text, (tl[0], tl[1] - 10),
         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    plt.rcParams['figure.figsize'] = (15,15)
    plt.axis('off')
    plt.imshow(image)         
    
# Converting image to binary to upload to SQL database
def img_to_binary(file):
    # Convert image data to binary format
    with open(file, 'rb') as file:
        binaryData = file.read()
    return binaryData  


def get_data(res):
    for ind,i in enumerate(res):
        # To get website url
        if "www" in i.lower() or "www." in i.lower():
            data["website"].append(i)
        elif "WWW" in i:
            data["website"] = res[4] +"." + res[5]
        # To get email ID
        elif "@" in i:
            data["email"].append(i)
        # To get mobile number
        elif "-" in i:
            data["mobile_number"].append(i)
            if len(data["mobile_number"]) ==2:
                data["mobile_number"] = " & ".join(data["mobile_number"])
        # To get company name  
        elif ind == len(res)-1:
            data["company_name"].append(i)
        # To get card holder name
        elif ind == 0:
            data["card_holder"].append(i)
        # To get designation
        elif ind == 1:
            data["designation"].append(i)
        # To get area
        if re.findall('^[0-9].+, [a-zA-Z]+',i):
            data["area"].append(i.split(',')[0])
        elif re.findall('[0-9] [a-zA-Z]+',i):
            data["area"].append(i)
        # To get city name
        match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
        match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
        match3 = re.findall('^[E].*',i)
        if match1:
            data["city"].append(match1[0])
        elif match2:
            data["city"].append(match2[0])
        elif match3:
            data["city"].append(match3[0])
        # To get state
        state_match = re.findall('[a-zA-Z]{9} +[0-9]',i)
        if state_match:
                data["state"].append(i[:9])
        elif re.findall('^[0-9].+, ([a-zA-Z]+);',i):
            data["state"].append(i.split()[-1])
        if len(data["state"])== 2:
            data["state"].pop(0)
        # To get pincode        
        if len(i)>=6 and i.isdigit():
            data["pin_code"].append(i)
        elif re.findall('[a-zA-Z]{9} +[0-9]',i):
            data["pin_code"].append(i[10:])  

# Function to create dataframe
def create_df(data):
    df = pd.DataFrame(data)
    return df            

#STREAMLIT CODING FRAMEWORK FOR OPTION MENU'S OPTIONS.
if choice_op == "Home":
    
    # Title Image
    st.title(":sunset[BizCardX: Extracting Business Card Data with OCR]")
    col1,col2 = st.columns(2)
    with col1:
        st.image(Image.open("C:\\Users\\mahes\\Downloads\\business-card-data-extraction.jpg"),width=400)
        st.subheader(":orange[OCR DEFINITION]")
        st.markdown("OCR is formerly known as Optical Character Recognition which is actually a complete process under which the images/documents which are present in a digital world are processed and from the text are being processed out as normal editable text.")
        st.subheader(":orange[PURPOSE OF OCR]")
        st.markdown("OCR is a technology that enables you to convert different types of documents, such as scanned paper documents, PDF files, or images captured by a digital camera into editable and searchable data.")
    with col2:    
        st.markdown("## :orange[TECHNOLOGIES USED]: Python,OCR,streamlit GUI, SQL,Data Extraction")
        st.subheader(":orange[EasyOCR]")
        st.markdown("EasyOCR is actually a python package that holds PyTorch as a backend handler. It detects the text from images also when high end deep learning library(PyTorch) is supporting it in the backend which makes it accuracy more credible. EasyOCR supports 42+ languages for detection purposes. EasyOCR is created by the company named Jaided AI company.")
        st.markdown("## :orange[Done by] : UMAMAHESWARI S")
        st.markdown("[Githublink](https://github.com/mahes101)")    
    st.image(Image.open("C:\\Users\\mahes\\Downloads\\image extraction.jpg"))    
    
# UPLOAD AND EXTRACT PAGE
elif choice_op == "Upload and Extract Data":
    # TITLE OF PAGE
    st.header("UPLOAD A BIZCARD AND EXTRACT DATA OF A BISCARD")
    col1,col2 = st.columns(2)
    with col1:
        image_file = st.file_uploader("Choose an Image of a Business Card",type=["jpg", "jpeg", "png"])
        if image_file is not None:
            save_card(image_file)
        st.markdown("YOU HAVE UPLOADED THIS BUSINESS CARD IMAGE")    
        st.image(image_file)    
        with st.spinner("Please wait processing image..."):
                st.set_option('deprecation.showPyplotGlobalUse', False)
                saved_img = os.getcwd()+ "\\" + "Biscard data"+ "\\"+ image_file.name
                image = cv2.imread(saved_img)
                result = reader.readtext(saved_img)
                st.markdown("### Image Processed and Data Extracted")
                button_opt = st.button("TEXT BOUNDING IMAGE")
                if button_opt:
                    st.pyplot(image_preview(image,result))
    #easy OCR
    saved_img = os.getcwd()+ "\\" + "Biscard data"+ "\\"+ image_file.name
    result1 = reader.readtext(saved_img,detail = 0,paragraph=False)    
    # Declaring a Dictionary called data for Storing Extracting data.
    data = {"company_name" : [],
                    "card_holder" : [],
                    "designation" : [],
                    "mobile_number" :[],
                    "email" : [],
                    "website" : [],
                    "area" : [],
                    "city" : [],
                    "state" : [],
                    "pin_code" : [],
                    "image" : img_to_binary(saved_img)
                }
    get_data(result1)
    with col2:
        tab1,tab2 = st.tabs(["UNDEFINED DATA","PRE-DEFINED DATA"])
        df = create_df(data)
        st.success("### Data Extracted!")
        st.write(df)
        with tab1:
            annotated_text("Please ","note: ","This ","Process ","will ","only ","allow ",("Business ","Card ","#de5d83"),"only ","It ","will ","not ","allow ","any other ","images.")
            st.write(result1)
            
        with tab2:
            annotated_text("Please","note: ","This ","Process ","will ","only ","allow ",("Business ","Card ","#de5d83"),"only. ","It ","will ","not ","allow ","any other ","images.")    
            annotated_text("To ",("Upload ","data","#915c83"),"to",("MYSQL"," ","#915c83"),"click ","below ","button.")
            button_opt1 = st.button("UPLOAD")
            
            st.write("COMPANY NAME: ",data["company_name"][0])
            st.write("CARD HOLDER: ",data["card_holder"][0])
            st.write("DESIGNATION: ",data["designation"][0])
            st.write("MOBILE NUMBER: ",data["mobile_number"][0])
            st.write("E-MAIL: ",data["email"][0])
            st.write("WEBSITE: ",data["website"][0])
            st.write("AREA: ",data["area"][0])
            st.write("CITY: ",data["city"][0])
            st.write("STATE: ",data["state"][0])
            st.write("PINCODE: ",data["pin_code"][0])
            
            if button_opt1:
                for i,row in df.iterrows():
                # here %s means string values 
                    sql_query = """INSERT INTO card_data(company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,image)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                    mycur.execute(sql_query, tuple(row))
                    # the connection is not auto committed by default, so we must commit to save our changes
                    mydb.commit()
            st.success("#### Uploaded to database successfully!")
            st.balloons()

#MODIFY OR DELETE A RECORD PAGE.
elif choice_op == "Modify Or Delete Data":
    st.title("MODIFY RECORD IN MYSQL OR DELETE A RECORD IN MYSQL")     
    
    col1,col2,col3 = st.columns(3,gap="large")
    try:
        with col1:
            
            st.markdown('__<p style="font-color:#873260;">MODIFY DATA OF BUSINESS CARD</p>__',unsafe_allow_html=True)
            mycur.execute("SELECT card_holder FROM card_data")
            result = mycur.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))
            st.markdown("#### Update or modify any data below")
            mycur.execute("select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data WHERE card_holder=%s",
                            (selected_card,))
            result = mycur.fetchone()

            # Displaying all the informations
            company_name = st.text_input("Company_Name", result[0])
            card_holder = st.text_input("Card_Holder", result[1])
            designation = st.text_input("Designation", result[2])
            mobile_number = st.text_input("Mobile_Number", result[3])
            email = st.text_input("Email", result[4])
            website = st.text_input("Website", result[5])
            area = st.text_input("Area", result[6])
            city = st.text_input("City", result[7])
            state = st.text_input("State", result[8])
            pin_code = st.text_input("Pin_Code", result[9])
            if st.button("Commit changes to DB"):
                # Update the information for the selected business card in the database
                mycur.execute("""UPDATE card_data SET company_name=%s,card_holder=%s,designation=%s,mobile_number=%s,email=%s,website=%s,area=%s,city=%s,state=%s,pin_code=%s
                                    WHERE card_holder=%s""", (company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,selected_card))
                mydb.commit()
                st.success("Information updated in database successfully.")
        with col2:
            st.markdown('__<p style="font-color:#873260;">DELETE BUSINESS CARD DATA IN DB</p>__',unsafe_allow_html=True)
    
            mycur.execute("SELECT card_holder FROM card_data")
            result = mycur.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to Delete", list(business_cards.keys()))
            st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
            st.write("#### Proceed to delete this card?")
            
            if st.button("Yes Delete Business Card"):
                mycur.execute(f"DELETE FROM card_data WHERE card_holder='{selected_card}'")
                mydb.commit()
                st.success("Business card information deleted from database.")
            st.image(Image.open("C:\\Users\\mahes\\Downloads\\Extract-Data.jpg"))    
        with col3:
            st.markdown('__<p style="font-color:#873260;">TO VIEW UPDATED DATA IN DB</p>__',unsafe_allow_html=True)
            
            if st.button("View updated data"):
                mycur.execute("select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_data")
                updated_df = pd.DataFrame(mycur.fetchall(),columns=["Company_Name","Card_Holder","Designation","Mobile_Number","Email","Website","Area","City","State","Pin_Code"])
                st.write(updated_df)   
            st.image(Image.open("C:\\Users\\mahes\\Downloads\\db.png"))             
    except:
        st.warning("There is no data available in the database")
                                        

    

        
        