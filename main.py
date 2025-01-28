from pdf2image import convert_from_path
import os
import base64
from langchain_groq import ChatGroq
import json
from openai import OpenAI
import cv2
import openai
import openai
from langsmith.wrappers import wrap_openai
from langsmith import traceable
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from datetime import datetime


units_map={"kwh" : "Kilowatt-hour (kWh)",
           "kvah" : "Kilovolt-ampere hour (kVAh)"
}


class Output(BaseModel):
    unit: str = Field(description="Unit of electricity being used in the electricity bill")
    amount: str = Field(description="Amount of electricity consumed")
    country: str = Field(description="Country to which the electricity bill belongs")

parser = JsonOutputParser(pydantic_object=Output)


load_dotenv()



client = OpenAI()
#client = wrap_openai(openai.Client())
#print(f"Wrapped OpenAI client: {client}")




country_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            '''Task Description:

You will be given two inputs:

A country name provided by the user.
A list of country names, which contains several country names that may or may not match the input country name directly.
Your task is to check if the country name provided by the user exists exactly in the list of country names. If the country is found in the list, return the country name as it is. If the country is not exactly present in the list, you should search for a matching country in the list that most closely matches the user’s input. If a match is found, return the name of the closest matching country from the list.

For example:

If the user enters "Sultanate of Oman", and the list contains "Oman", you should return "Oman" since it is the closest match.
If the user enters a country name that directly matches one in the list (e.g., "France" and "France" is in the list), return "France" as it is.
Clarifications:

The goal is to check for exact matches first. If no exact match is found, you should attempt to find a close match.
Do not return anything that is not an actual country name from the list.
The country names are provided in a standardized format, so any slight variations in the name (such as "Sultanate of Oman" vs "Oman") should be handled correctly.
Please ensure that:

You search for the country name in the list.
If there is no exact match, find a relevant country from the list that best matches the input.

You just need to return the country name , and nothing else.

Example outputs:
Oman

Albania

List of Countries is as below:
Afghanistan
Albania
Algeria
American Samoa
Andorra
Angola
Anguilla
Antigua and Barbuda
Argentina
Armenia
Aruba
Australia
Austria
Azerbaijan
Bahamas
Bahrain
Bangladesh
Barbados
Belarus
Belgium
Belize
Benin
Bermuda
Bhutan
Bolivia (Plurinational State of)
Bonaire, Sint Eustatius and Saba
Bosnia and Herzegovina
Botswana
Brazil
British Virgin Islands
Brunei Darussalam
Bulgaria
Burkina Faso
Burundi
Cabo Verde
Cambodia
Cameroon
Canada
Canary Islands (Spain)
Cayman Islands
Central African Republic
Chad
Channel Islands (U.K)
Chile
China
Colombia
Comoros
Congo
Cook Islands
Costa Rica
Côte d’Ivoire
Croatia
Cuba
Curaçao
Cyprus
Czechia
Democratic People's Republic of Korea
Democratic Republic of the Congo
Denmark
Djibouti
Dominica
Dominican Republic
Ecuador
Egypt
El Salvador
Equatorial Guinea
Eritrea
Estonia
Eswatini
Ethiopia
Falkland Islands (Malvinas)
Faroe Islands
Fiji
Finland
France
French Guiana
French Polynesia
Gabon
Gambia
Georgia
Germany
Ghana
Gibraltar
Greece
Greenland
Grenada
Guadeloupe
Guam
Guatemala
Guinea
Guinea-Bissau
Guyana
Haiti
Honduras
Hungary
Iceland
India
Indonesia
Iran (Islamic Republic of)
Iraq
Ireland
Isle of Man
Israel
Italy
Jamaica
Japan
Jordan
Kazakhstan
Kenya
Kiribati
Kosovo
Kuwait
Kyrgyzstan
Lao People's Democratic Republic
Latvia
Lebanon
Lesotho
Liberia
Libya
Liechtenstein
Lithuania
Luxembourg
Madagascar
Madeira (Portugal)
Malawi
Malaysia
Maldives
Mali
Malta
Marshall Islands
Martinique
Mauritania
Mauritius
Mayotte
Mexico
Micronesia (Federated States of)
Monaco
Mongolia
Montenegro
Montserrat
Morocco
Mozambique
Myanmar
Namibia
Nauru
Nepal
Netherlands
New Caledonia
New Zealand
Nicaragua
Niger
Niue
North Macedonia
Northern Mariana Islands
Norway
Oman
Pakistan
Palau
Panama
Papua New Guinea
Paraguay
Peru
Philippines
Poland
Portugal
Puerto Rico
Qatar
Republic of Korea
Republic of Moldova
Réunion
Romania
Russian Federation
Rwanda
Saint Helena
Saint Kitts and Nevis
Saint Lucia
Saint Martin (French Part)
Saint Pierre and Miquelon
Saint Vincent and the Grenadines
Samoa
San Marino
Sao Tome and Principe
Saudi Arabia
Senegal
Serbia
Seychelles
Sierra Leone
Singapore
Sint Maarten (Dutch part)
Slovakia
Solomon Islands
Somalia
South Africa
South Sudan
Spain
Sri Lanka
State of Palestine
Sudan
Suriname
Sweden
Switzerland
Syrian Arab Republic
Taiwan (Chinese Taipei)
Tajikistan
Thailand
Timor-Leste
Togo
Trinidad and Tobago
Tunisia
Turkey
Turkmenistan
Turks and Caicos Islands
Tuvalu
Uganda
Ukraine
United Arab Emirates
United Kingdom of Great Britain and Northern Ireland
United Republic of Tanzania
United States of America
United States Virgin Islands
Uruguay
Uzbekistan
Vanuatu
Venezuela (Bolivarian Republic of)
Viet Nam
Yemen
Zambia
Zimbabwe

''',
        ),
        ("human", "{country}"),
    ]
)

# Initialize the Groq model

model_country = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)



# Path to your PDF
pdf_path = "electricity_bills.pdf"

# Convert the PDF pages to images (one image per page)
images = convert_from_path(pdf_path)

# Function to encode an image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Iterate through the images extracted from the PDF

def bill_extractor():
        
        final_answer={
             "electricity":[]
        }
             
        
        for page_number, image in enumerate(images, start=1):

            # Save the image as a PNG in the /content folder
            image_path = f"page_sample_bill_{page_number}.jpeg"
            image.save(image_path, "JPEG")

            
            #binary_image_path = f"{page_number}.jpeg"

            base64_image = encode_image(image_path)

            # Debug: Print base64 encoded image length to ensure it is being passed correctly
            #print(f"Base64 Image Length for Page {page_number}: {len(base64_image)}")

            # Debug: Print the base64 image string to ensure it's being encoded correctly
            #print(f"Base64 Image for Page {page_number}: {base64_image[:50]}...")  # Print first 50 chars for brevity

            try:
                # Prepare the Groq request
                #response = client.chat.completions.create(
                #model="gpt-4o-mini",
                response= client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages = [{
                    'role': 'user',
                    'content': [
                    {"type" :"text",
                    "text": '''

### Task: Extract Information from an Electricity Bill Image

You will be analyzing an image of an electricity bill. Your task is to carefully extract **specific details** as accurately as possible. Follow the instructions below closely to avoid errors or omissions.  

#### Information to Extract:

1. **Country of the Bill**  
   To determine the country, look for:  
   - **Phone Numbers**: Identify any country codes in phone numbers, customer service numbers, or international dialing codes (e.g., +1 for the USA, +44 for the UK, etc.).  
   - **Language**: Check the language used on the bill, as it may indicate the country or region (e.g., English, Spanish, French, etc.).  
   - **Addresses**: Search for any address on the bill, especially one that includes a country name, city, or region.  
   - **Country-Specific Terms**: Look for regulatory body names, utility company references, or billing terms that are unique to a particular country (e.g., Ofgem for the UK or Public Utility Commission for the USA).  
   - **Tax or Banking Details**: Inspect any tax identification numbers, VAT details, or banking information that follow country-specific formats.  
   - **Logos or Branding**: Pay attention to any company logos or symbols that are unique to a specific country or utility provider.  

2. **Electricity Consumption Details**  
   Extract the **unit of electricity consumed** and the **exact amount consumed**:  
   - Look for the **unit of measurement** which would either be kWh or kVAh , and is typically  next to the consumption value.  
   - Extract the **exact number of units consumed**, not the charges or costs. Ensure the number is accurate, including all digits .  
   - If multiple consumption values are mentioned, find and extract the **total consumption amount**. This value is typically indicated as a summation of other consumption figures.  

#### Important Notes:
- **Accuracy is critical**: Double-check extracted values and units to avoid mistakes.  
- Focus **only on the country and electricity consumption details**. Ignore unrelated numbers or values.  
- If the country is not immediately obvious, look for multiple clues and ensure the conclusion is consistent.  

---

### Expected Output in json Format:

{Country: [Country name]  
 Unit: [Unit of electricity ( kWh or kVAh)]  
Amount : [Exact number of units consumed] }


#### Example Output :  

{Country: United States  
 Unit: kWh  
Amount: 5124 } 


 

Follow the instructions carefully and ensure your response adheres to the format above.

'''
                    },
                    {
                        'type': 'image_url',
                        'image_url': {
                            "url":f"data:image/jpeg;base64,{base64_image}",
                        }
                    }
                    ]
                }]
                )



                parsed_response=parser.invoke(response.choices[0].message.content)
            

                country_chain=country_prompt|model_country
                correct_country=country_chain.invoke({"country": parsed_response["Country"]})


                parsed_response["Country"]=correct_country.content
                parsed_response["Unit"]=units_map[parsed_response["Unit"].lower()]
                




                

                # Debug: Print the messages structure to ensure it's correct
                #print(f"Messages for Page {page_number}: {json.dumps(messages, indent=2)}")

                # Send the request to Groq and get the response
                #country_response = model.invoke(messages)

                # Print the response for this page
                print(parsed_response)
                #print(correct_country)
                #print(f"Response for page {page_number}: {response.choices[0].message.content}")
                #print(f"Final response for page {page_number} : {final_response.content} ")
                #print("\n")
              
                final_answer["electricity"].append({
                    "country": parsed_response["Country"],
                    "unit": parsed_response["Unit"],
                    "value": parsed_response["Amount"],
                    "description": "", 
                    "updated_at":  datetime.utcnow().isoformat() + "Z",
                    "attachments": "",
                    "renewable_energy_contract": "No",
                    "emission_scope": "scope2",
                    "id": 1
                    }
                )
                os.remove(image_path)
                

            except Exception as e:
                print(f"Error processing page {page_number}: {e}")
    
        return final_answer




final_data =bill_extractor()

#print(final_data)
   

    

  
