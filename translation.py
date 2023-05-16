# Create a python script for opening "SSBHistory.json" file, which is a Json file with Turkish items in it, and translate them into English using GPT-4 of openai api.

# Importing libraries
import json
import openai
import os
import requests
import time
import regex as re


# Setting up the openai api key
openai.api_key = ""

# Opening the json file
with open("SSBHistory.json", "r") as f:
    data = json.load(f) # Loading the json file

# Creating a list for storing the translated items
translated = []
src = "https://www.savunmasanayii360.com"

# get keys and values separately


# Looping through the items in the json file
for parentkey, parentvalue in data.items():

    for child in data[parentkey]:

        # if cover_img, gallery or video is not empty, we need to download them into our local machine by creating a respective folder for the category key

        # json parse videos and gallery
        child["videos"] = json.loads(child["videos"])
        child["gallery"] = json.loads(child["gallery"])


        if child["cover_img"] != "":
            ## check if folder exists or not
            if not os.path.exists(f"images/{parentkey}"):
                os.mkdir(f"images/{parentkey}")

            child["cover_img"] = src + child["cover_img"]
            
            # use requests instead of wget
            # os.system(f"wget {child['cover_img']} -P images/{item}")
            r = requests.get(child['cover_img'])
            #keep original name as there might be many images with same name, we'll be downloading webp image

            

            child['cover_img'] = child['cover_img'].split('?')[0]
            # if file doesn't exist in local
            if not os.path.exists(f"images/{parentkey}/{child['cover_img'].split('/')[-1]}"):

                with open(f"images/{parentkey}/{child['cover_img'].split('/')[-1]}", "wb") as f:
                    f.write(r.content)


        if child["gallery"] != []:
            if not os.path.exists(f"images/{parentkey}"):
                os.mkdir(f"images/{parentkey}")

            for img in child["gallery"]:
                img = src + img
                r = requests.get(img)

                img = img.split('?')[0]
                if not os.path.exists(f"images/{parentkey}/{img.split('/')[-1]}"):
                    with open(f"images/{parentkey}/{img.split('/')[-1]}", "wb") as f:
                        f.write(r.content)


                    

        if child["videos"] != []:

            if not os.path.exists(f"videos/{parentkey}"):
                os.mkdir(f"videos/{parentkey}")

            for video in child["videos"]:
                video = src + video

                r = requests.get(video)
                if not os.path.exists(f"videos/{parentkey}/{video.split('/')[-1]}"):
                    with open(f"videos/{parentkey}/{video.split('/')[-1]}", "wb") as f:
                        f.write(r.content)


        ### instead of translating the entire json object, we'll translate the following:
        # title
        # slug
        # yuz_yil
        # body

        # also we'll change "lang" from "tr" to "en"

        # Creating a dictionary for storing the translated items
        translated_item = {}

        # Looping through the keys and values of the child item
        for key, value in child.items():
            
            translated_slug = ""

            # If the key is "lang", we need to change the value from "tr" to "en"
            if key == "lang":
                translated_item[key] = "en"

            # If the key is "title", "slug", "yuz_yil" or "body", we need to translate the value
            elif key == "title" or key == "yuz_yil" or key == "body" or key == "slug":
                # Creating a prompt for the openai api
                # Prompt example: Json below is in Turkish. It has some Turkish characters as binary code, for example: "\u0131" for the letter "ı". I need you to translate it into English but keep the data structure the same:
                prompt = f"""Translate to English from Turkishand keep HTML tags. \n\n{value}\n\nEnglish:"""
                try:

                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a translator which translates text to English from Turkish and keeps HTML tags."},
                            {"role": "user", "content": prompt},
                            ],
                        temperature=0.7,

                    )
                except openai.error.APIError as e:
                    print(f"OpenAI API returned an API Error: {e}")
                    pass
                except openai.error.APIConnectionError as e:
                    print(f"Failed to connect to OpenAI API: {e}")
                    pass
                except openai.error.RateLimitError as e:
                    print(f"OpenAI API request exceeded rate limit: {e}")
                    pass
                except openai.error.Timeout as e:
                    print(f"OpenAI API request timed out: {e}")
                    pass
                except openai.error.InvalidRequestError as e:
                    print(f"Invalid request to OpenAI API: {e}")
                    pass
                except openai.error.AuthenticationError as e:
                    print(f"Authentication error with OpenAI API: {e}")
                    pass
                except openai.error.ServiceUnavailableError as e:
                    print(f"OpenAI API service unavailable: {e}")
                    pass

                translated_item[key] = response["choices"][0]["message"]["content"]

                
                
                # print original \n english
                print(f"{value}\n\nEnglish: {translated_item[key]}")
                print("--------------------------------------------------")


            # If the key is not "lang", "title", "slug", "yuz_yil" or "body", we need to keep the value as it is
            else:
                translated_item[key] = value

            
            if key == "slug":
                #get translated_item["title"] and turn it into slug using smart regex, also clear html tags
                translated_slug = re.sub(r'<[^>]*>', '', translated_item["title"]) # remove html tags
                translated_slug = re.sub(r'[^a-zA-Z0-9\s]', '', translated_slug) # remove special characters
                translated_slug = re.sub(r'\s+', '-', translated_slug) # replace spaces with dash
                translated_slug = translated_slug.lower() # make it lowercase
                translated_slug = re.sub(r'-+', '-', translated_slug) # replace multiple dashes with single dash
                translated_slug = translated_slug.strip('-') # remove dash from start and end

                # assign translated item as string
                translated_item[key] = str(translated_slug)


        # Appending the translated item to the translated list
        translated.append(translated_item)

        """
        desired format for output:
        {
            "mo-3-yuzyil": [
            ...
            ],
            "mo-4-yuzyil": [
            ...
            ]
        }
        """



        # update parentkey>nth child with translated_item
        data[parentkey][data[parentkey].index(child)] = translated_item

        # write to file
        with open("SSBHistoryTranslated.json", "w") as f:
            json.dump(data, f, indent=4)


        



        # wait 10 seconds after each translation
        time.sleep(10)