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
#IMPORTING IO LIBRARY.
import io

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
                   password="admin@123")
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
@st.cache_data
def load_image():
    reader = easyocr.Reader(['en'], model_storage_directory=".")
    return reader

## CREATING  A DATABASE IN MYSQL CALLED bizcardx_db

mycur.execute("CREATE DATABASE IF NOT EXISTS bizcardx_db")
mycur.execute("USE bizcardx_db")

# CREATING A TABLE IN MYSQL DATABASE FOR STORING DATA WHICH IS EXTRACTED.
mycur.execute('''CREATE TABLE IF NOT EXISTS bizcard_data
                   (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    card_holder TEXT,
                    designation TEXT,
                    company_name TEXT,
                    mobile_number VARCHAR(50),
                    email TEXT,
                    website TEXT,
                    address TEXT,
                    pin_code VARCHAR(100),
                    image LONGBLOB
                    )''')


def image_preview(image,result): 
    for (coord, text, prob) in result:
        (topleft, topright, bottomright, bottomleft) = coord
        tx,ty = (int(topleft[0]), int(topleft[1]))
        bx,by = (int(bottomright[0]), int(bottomright[1]))
        cv2.rectangle(image, (tx,ty), (bx,by), (0, 0, 255), 2)

    plt.imshow(image)         
    

def get_data(result):
    ext_dic = {'Name': [], 'Designation': [], 'Company name': [], 'Contact': [], 'Email': [], 'Website': [],
               'Address': [], 'Pincode': []}

    ext_dic['Name'].append(result[0])
    ext_dic['Designation'].append(result[1])

    for m in range(2, len(result)):
        if result[m].startswith('+') or (result[m].replace('-', '').isdigit() and '-' in result[m]):
            ext_dic['Contact'].append(result[m])

        elif '@' in result[m] and '.com' in result[m]:
            small = result[m].lower()
            ext_dic['Email'].append(small)

        elif 'www' in result[m] or 'WWW' in result[m] or 'wwW' in result[m]:
            small = result[m].lower()
            ext_dic['Website'].append(small)

        elif 'TamilNadu' in result[m] or 'Tamil Nadu' in result[m] or result[m].isdigit():
            ext_dic['Pincode'].append(result[m])

        elif re.match(r'^[A-Za-z]', result[m]):
            ext_dic['Company name'].append(result[m])

        else:
            removed_colon = re.sub(r'[,;]', '', result[m])
            ext_dic['Address'].append(removed_colon)

    for key, value in ext_dic.items():
        if len(value) > 0:
            concatenated_string = ' '.join(value)
            ext_dic[key] = [concatenated_string]
        else:
            value = 'NA'
            ext_dic[key] = [value]

    return ext_dic


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
    image_file = st.file_uploader("Choose an Image of a Business Card",type=["jpg", "jpeg", "png"])
    result1 = []
    col1,col2 = st.columns(2)
    reader_1 = load_image()
    if image_file is not None:
        input_image = Image.open(image_file)               
        with col1:
                st.markdown("YOU HAVE UPLOADED THIS BUSINESS CARD IMAGE")   
                st.image(input_image,caption="Business Card")    
                with st.spinner("Please wait processing image..."):
                    st.set_option('deprecation.showPyplotGlobalUse', False)
                    result = reader_1.readtext(np.array(input_image),detail=1)
                    image_path = os.getcwd()+"\\Biscard data\\"+image_file.name
                    img = cv2.imread(image_path)
                    st.markdown("### Image Processed and Data Extracted")
                    button_opt = st.button("TEXT BOUNDING IMAGE")
                    if button_opt:
                        st.pyplot(image_preview(img,result))
        #easy OCR
        result1 = reader_1.readtext(np.array(input_image),detail = 0,paragraph=False)    
        st.success("### Data Extracted!")
        # Converting image into bytes
        image_bytes = io.BytesIO()
        input_image.save(image_bytes, format='PNG')
        image_data = image_bytes.getvalue()
        # Creating dictionary
        data1 = {"image": [image_data]}
        # Declaring a Dictionary called data for Storing Extracting data.
        data = get_data(result1)
        df = create_df(data)    
        df_1 = pd.DataFrame(data1)
        concat_df = pd.concat([df, df_1], axis=1)                  
        with col2:
            tab1,tab2 = st.tabs(["UNDEFINED DATA","PRE-DEFINED DATA"]) 
            st.write(df)
            with tab1:
                annotated_text("Please ","note: ","This ","Process ","will ","only ","allow ",("Business ","Card ","#de5d83"),"only ","It ","will ","not ","allow ","any other ","images.")
                st.write(result1)
                
            with tab2:
                annotated_text("Please","note: ","This ","Process ","will ","only ","allow ",("Business ","Card ","#de5d83"),"only. ","It ","will ","not ","allow ","any other ","images.")    
                annotated_text("To ",("Upload ","data","#915c83"),"to",("MYSQL"," ","#915c83"),"click ","below ","button.")
                button_opt1 = st.button("UPLOAD")
                
                st.write("COMPANY NAME: ",data["Company name"][0])
                st.write("CARD HOLDER: ",data["Name"][0])
                st.write("DESIGNATION: ",data["Designation"][0])
                st.write("CONTACT NUMBER: ",data["Contact"][0])
                st.write("E-MAIL: ",data["Email"][0])
                st.write("WEBSITE: ",data["Website"][0])
                st.write("ADDRESS: ",data["Address"][0])
                st.write("PINCODE: ",data["Pincode"][0])
                
                if button_opt1:
                    for i,row in concat_df.iterrows():
                    # here %s means string values 
                        sql_query = """INSERT INTO bizcard_data(card_holder,designation,company_name,mobile_number,email,website,address,pin_code,image)
                                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
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
            mycur.execute("SELECT card_holder FROM bizcard_data")
            result = mycur.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))
            st.markdown("#### Update or modify any data below")
            mycur.execute("select card_holder,designation,company_name,mobile_number,email,website,address,pin_code from bizcard_data WHERE card_holder=%s",
                            (selected_card,))
            result = mycur.fetchone()

            # Displaying all the informations
            card_holder = st.text_input("Card_Holder", result[0])
            designation = st.text_input("Designation", result[1])
            company_name = st.text_input("Company name", result[2])
            mobile_number = st.text_input("Mobile_Number", result[3])
            email = st.text_input("Email", result[4])
            website = st.text_input("Website", result[5])
            address = st.text_input("Address", result[6])
            pin_code = st.text_input("Pin_Code", result[7])
            if st.button("Commit changes to DB"):
                # Update the information for the selected business card in the database
                mycur.execute("""UPDATE bizcard_data SET card_holder=%s,designation=%s,company_name=%s,mobile_number=%s,email=%s,website=%s,address=%s,pin_code=%s
                                    WHERE card_holder=%s""",(card_holder,designation,company_name,mobile_number,email,website,address,pin_code,selected_card))
                mydb.commit()
                st.success("Information updated in database successfully.")
        with col2:
            st.markdown('__<p style="font-color:#873260;">DELETE BUSINESS CARD DATA IN DB</p>__',unsafe_allow_html=True)
    
            mycur.execute("SELECT card_holder FROM bizcard_data")
            result = mycur.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to Delete", list(business_cards.keys()))
            st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
            st.write("#### Proceed to delete this card?")
            
            if st.button("Yes Delete Business Card"):
                mycur.execute(f"DELETE FROM bizcard_data WHERE card_holder='{selected_card}'")
                mydb.commit()
                st.success("Business card information deleted from database.")
            st.image(Image.open("C:\\Users\\mahes\\Downloads\\Extract-Data.jpg"))    
        with col3:
            st.markdown('__<p style="font-color:#873260;">TO VIEW UPDATED DATA IN DB</p>__',unsafe_allow_html=True)
            
            if st.button("View updated data"):
                mycur.execute("select card_holder,designation,company_name,mobile_number,email,website,address,pin_code from bizcard_data")
                updated_df = pd.DataFrame(mycur.fetchall(),columns=["Card_Holder","Designation","Company_Name","Mobile_Number","Email","Website","Address","Pin_Code"])
                st.write(updated_df)   
            st.image(Image.open("C:\\Users\\mahes\\Downloads\\db.png"))             
    except:
        st.warning("There is no data available in the database")
                                        

    

        
        