import requests
import pandas as pd
import numpy as np
import urllib
import cv2
from PIL import Image
import matplotlib.pyplot as plt
import random

'''
This class searches the MET  Museum database using the api and returns
1) List of object ids that fit the search
2) List of artwork titles
3) Ability to export
'''

class SearchMET():
    def __init__(self,keyword = None) -> None:
        """ Exports images as icons to files in working directory


        Parameters
        ------------
            keywords (str) : user search term
        Return
        -----------
            None

        >>> export_image_icons()
        <check project folder>

        """

        #Perform api call and populate dataframes
        BASE_URL = 'https://collectionapi.metmuseum.org/public/collection/v1'
        if keyword == None:
          keyword = "sunflower" 
        print("Requesting search string...")
        resp = requests.get(BASE_URL + "/search?isHighlight=true&q=" + keyword)
        objs = resp.json()["objectIDs"]
        resp = requests.get(f"{BASE_URL}/objects/{objs[0]}")
        respDict = resp.json()

        #list will organize the data based on response json structure
        list_cols = ['constituents', 'measurements', 'tags']
        url_cols = ["additionalImages"]
        other_cols = [k for k,v in respDict.items() if not isinstance(v,list)]
        lists = {k:[] for k in list_cols}
        img_lists = []
        rows = []

        #Iterate through the first 10 objects for the full details of each one
        for i,id in enumerate(objs):
            if i >= 10:
              break

            
            resp = requests.get(BASE_URL + "/objects/" + str(id))
        
            respDict = resp.json()
            retDict = { c: respDict[c] for c in other_cols}
            #print(retDict)

            for k in list_cols:
                if respDict[k]:
                    lists[k] += [{"objectID":id,**r} for r in respDict[k]]
        
            img_lists += [[id] + [r] for r in respDict["additionalImages"]]
            if len(respDict["primaryImage"]) >0:
                img_lists += [[id,respDict["primaryImage"]]]
            rows += [retDict]

        self.df_objects = pd.DataFrame(rows)
        self.df_objects = self.df_objects.reset_index(drop=True)
        self.df_objects.loc[self.df_objects.title == "", "title"] = "Unknown"
        
        #Create images dataframe
        self.df_images = pd.DataFrame(img_lists,columns=["objectID","url"])

        #Create constituent dataframe
        self.df_constituents = pd.DataFrame(lists['constituents'])

        #Create the measruements dataframe
        df_measurements1 =  pd.DataFrame(lists['measurements'])
        df_measurements2 = pd.DataFrame(df_measurements1["elementMeasurements"].to_list())
        self.df_measurements = pd.concat([df_measurements1,df_measurements2],axis=1)
        

        #Source: https://pyimagesearch.com/2015/03/02/convert-url-to-image-with-python-and-opencv/

        pims = [Image.open(requests.get(url, stream=True).raw) for url in self.df_images.url]
        self.cropped_imgs = []
        print("Locating objects and cropping images...")
        for pim in pims:
            image = np.array(pim)
            #print(image.shape)

            #Source:https://dontrepeatyourself.org/post/edge-and-contour-detection-with-opencv-and-python/
            # apply thresholding on the gray image to create a binary image
            gray = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
            edged = cv2.Canny(gray, 10, 200)
            blurred = cv2.GaussianBlur(edged, (101, 101), 0)
            ret, im = cv2.threshold(blurred, 10, 200, cv2.THRESH_BINARY)

            
            
            # find the contours
            contours, hierarchy  = cv2.findContours(im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)



            #create bounding boxes for each object in image file
            rects = []
            #print(cnt)
            for cnt in contours:
                if (cnt.shape[0] > 1):
                    x,y,w,h = cv2.boundingRect(cnt)
                    if w > 256 and h > 256:
                        rects += [(x,y,w,h)] 

            #create a new image for each object
            for x,y,w,h in rects:
                wpad = int(.1*w/2)
                hpad = int(.1*h/2)
                # x = [x-wpad,x+w+wpad]
                # y = [y-hpad,y+h+hpad]
                x = [x,x+w]
                y = [y,y+h]
                
                #print(x,y)
                if 0 <= y[0] < y[1] <= image.shape[0] and 0 <= x[0]< x[1] <= image.shape[1]: 
                    self.cropped_imgs += [Image.fromarray(image[y[0]:y[1],x[0]:x[1]])]

        #choose no more that 10 images
        if len(self.cropped_imgs) > 10:
            self.cropped_imgs = random.sample(self.cropped_imgs,10)





                
    def objects(self):
        #title
        #artist
        #department
        return self.df_objects[["objectID", "title", "artistDisplayName"]]

    def regions(self):
        #list of regions
        return self.df_objects[self.df_objects["region"] != ""]["region"].unique()

    def titles(self):
        return self.df_objects[self.df_objects["title"] != ""]["title"].unique()

    def cropped_images(self):
        """ Returns list of Pillow images


        Parameters
        ------------
            None
        Return
        -----------
            list of Pillow images

        >>> s = SearchMET()
        >>> s.export_image_icons()
        >>> figure, axes = plt.subplots(len(cropped_imgs), 1, figsize=(30,30))
        >>> for ax,img in zip(axes,cropped_imgs):
        >>>  ax.imshow(img)
        <diplay of images>

        """
        #title and image url
        return self.cropped_imgs
    
    def export_image_icons(self):
        """ Exports images as icons to files in working directory


        Parameters
        ------------
            None
        Return
        -----------
            None

        >>> export_image_icons()
        <check project folder>

        """
        
        for i,img in enumerate(self.cropped_imgs):
            img.save(f"image{i+1}.ico",sizes=[(256,256)])
        

    def images(self):
        #title and image url
        return self.df_images.merge(s.df_objects, on="objectID")[["objectID", "title", "url"]]

    def artists(self):
        #List of artists
        return self.df_objects["artistDisplayName"].unique()

if __name__ == "__main__":
    #print("here")
    s = SearchMET("sun")
    imgs = s.cropped_images()
    for i in imgs:
        print(i.size)
    print(type(imgs))
    print(len(imgs))
    print(s.artists())
    print(s.titles())
    print(s.regions())
    print(s.objects())
    s.export_image_icons()

