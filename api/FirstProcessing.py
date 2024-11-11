import base64
import cv2
import numpy
from PIL import Image
from io import BytesIO

def FormatImageData(image): # the api recieves the image as a URL, this function converts it to a numpy array so it can be processed
    im_bytes = base64.b64decode(image.split("base64,")[1]) # the format of the URL is "data:image/jpeg;base64, <image data>" so  split the string at the "base64," and take the second part
    # then use b64decode to convert the image data to bytes
    im_arr = numpy.frombuffer(im_bytes, dtype=numpy.uint8) # convert the bytes to a buffer numpy array
    img = cv2.imdecode(im_arr, flags=cv2.IMREAD_GRAYSCALE) # convert use cv2 to convert the data to grayscale
    image = Image.fromarray(img).resize((404, 404)) # Use PIL to resize the image to 404x404
    image.save("Test.png")
    return image # return the PIL image

def Blend(Data, Kernal, Depth):
    X, Y = Data.shape
    # the following code is different from what i suggested in the desing as i found i can make the blend part > 100x faster by using numpy
    Data = Data.astype(numpy.float32) # convert the data to a float32 numpy array so that it can have values greater than 255

    # the general idea of this is to shift the image by 1 pixel in each direction, this does the equivalent of taking a 3x3 kernal at each pixel, however it is much more efficient as it can use vectorized operations, and reuse values
    OffsetLeft = numpy.pad(Data[:, 0:-1], ((0, 0), (1, 0)), 'constant', constant_values=0) 
    OffsetRight = numpy.pad(Data[:, 1:], ((0, 0), (0, 1)), 'constant', constant_values=0)
    OffsetUp = numpy.pad(Data[0:-1, :], ((1, 0), (0, 0)), 'constant', constant_values=0)
    OffsetDown = numpy.pad(Data[1:, :], ((0, 1), (0, 0)), 'constant', constant_values=0)
    DiagonalLeftUp = numpy.pad(Data[0:-1, 0:-1], ((1, 0), (1, 0)), 'constant', constant_values=0)
    DiagonalLeftDown = numpy.pad(Data[1:, 0:-1], ((0, 1), (1, 0)), 'constant', constant_values=0)
    DiagonalRightUp = numpy.pad(Data[0:-1, 1:], ((1, 0), (0, 1)), 'constant', constant_values=0)
    DiagonalRightDown = numpy.pad(Data[1:, 1:], ((0, 1), (0, 1)), 'constant', constant_values=0)
    SumForAverage = Data + OffsetLeft + OffsetRight + OffsetUp + OffsetDown + DiagonalLeftUp + DiagonalLeftDown + DiagonalRightUp + DiagonalRightDown # add all the shifted images together
    Average = SumForAverage / 9 # divide by 9 to get the average
    Average[Average < 128] = 0 # threshold the image
    Average[Average >= 128] = 255
    Data = Average.astype(numpy.uint8) # convert the data back to a uint8 numpy array
    img = Image.fromarray(Data) # convert the data to a PIL image
    img.save("Test.png")
    
    Map = Maper(Data.copy()) # get the map of the image
    Data = Data[Kernal//2:-Kernal//2-1, Kernal//2:-Kernal//2 -1] # remove the padding from the image
    Copy = Data.copy()
    URL = 'data:image/jpeg;base64,' + im_2_b64(Image.fromarray(Data).convert('RGB')) # convert the image to a URL using the custom im_2_b64 function, the image is converted to RGB as the image is grayscale and the URL needs to be in RGB
    DataString = convertDataToSting(Data.tolist()) # convert the data to a string so it can be sent to the client
    MapString = convertDataToSting(Map.tolist()) # convert the map to a string so it can be sent to the client
    return MapString, DataString, URL, Copy

def convertDataToSting(Data):# join each row with a comma to a string and then join each row with a semicolon
    Output = ",".join(str(elm) for elm in Data[0]) # join the first row
    for Index in range(1, len(Data)): #loop through the rest of the rows
        stri = ",".join(str(elm) for elm in Data[Index]) # join the row
        Output += ";" + stri # add the row to the string seperated by a semicolon
    return Output

def im_2_b64(image):
    buff = BytesIO() # create a buffer to store the image while it is converted to bytes and then to base64
    image.save(buff, format="JPEG") # save the image to the bytes buffer
    img_str = base64.b64encode(buff.getvalue()).decode("utf-8") # convert the bytes to base64 using b64encode and then decode it to a string
    return img_str

def Place(Data, Map):
    Data[Map != True] = -1 # sets the pixels that have already been groupes to -1 so they can't have the same value as the pixel being checked
    return Data

def Maper(Data):
    Xsize, Ysize = Data.shape # get loop sizes
    Map = numpy.zeros((Xsize-2, Ysize-2)) # create an empty map of the image
    Map = numpy.pad(Map, pad_width=1, mode='constant', constant_values=-1) # pad the map with -1
    #this is done so that the edges of the image can be checked without going out of bounds when checking the pixels around them
    # and the padding will never be added to the que as they don't have group values of 0
    Ids = 0 # create a variable to store the current group id
    for Y in range(1, Ysize-1):# loop through the image avoiding the edges
        for X in range(1, Xsize-1):
            if Map[X, Y] == 0: # if the pixel has not been grouped
                Ids += 1 # create a new group
                Que = [(X, Y)] # create a queue to store the pixels that need to be checked
                while len(Que) > 0: # while there are pixels that need to be checked
                    Xer, Yer = Que.pop(0) # get the next pixel to check
                    if Map[Xer, Yer] == 0: # if the pixel has not been grouped
                        Map[Xer, Yer] = Ids # set the pixel to the current group
                        DataCopy = Data[Xer-1:Xer+2, Yer-1: Yer+2].copy() # copy the 3x3 area around the pixel that needs to be checked
                        #this is required as numpy data are objects so taking a subset of the data will only change the variable name meaning any alterations also effect the data as a whole,
                        #  in order to get an independent version of the data a copy must be made
                        ToAdd = numpy.transpose(numpy.where((Place(DataCopy, Map[Xer-1:Xer+2, Yer-1: Yer+2] == 0) == Data[Xer, Yer]) == True)) + numpy.array([Xer, Yer]) - 1
                        #Map[Xer-1:Xer+2, Yer-1: Yer+2] gets the 3x3 area around the pixel that needs to be checked
                        # Map[Xer-1:Xer+2, Yer-1: Yer+2] == 0 checks if the pixel has already been grouped
                        # Place(DataCopy, Map[Xer-1:Xer+2, Yer-1: Yer+2] == 0) changes the value of any already seen pixels to -1 so they can't be the same as the pixel being checked
                        # == Data[Xer, Yer] checks if the pixel being checked has the same value as the pixel being checked
                        # transpose(numpy.where(Place() == True)) gets the x and y coordinates of the pixels that have the same value, in the sub section
                        # + numpy.array([Xer, Yer]) - 1 adds the x and y coordinates of the pixel being checked so that the coordinates are relative to the whole image
                        Que = Que + [tuple(x) for x in ToAdd.tolist()] # add the pixels that need to be checked to the que
                    
    return Map