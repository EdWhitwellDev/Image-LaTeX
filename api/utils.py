
import random
import time
import numpy
import cv2
from PIL import Image
from .ImageRecognition import *
from .models import *

def OrderCharacters(Characters, Dividers, Roots, ImageHeight, ImageWidth): # this is the managment function for the character ordering 

    Zones = MakeZonesFromRootsAndDividers(Roots, Dividers, ImageHeight, ImageWidth) 
    Zones = MergeSortZones(Zones) # this function sorts the zones in accending order based on their width

    Zones = PlaceCharactersInZones(Zones, Characters) 
    Zones = PlaceZonesInZones(Zones)

    Zones = OrderContent(Zones)

    return Zones

def PrintZonesContent(Zones): # this function prints the content of the zones, it is used for debugging
    for Zone in Zones:
        content = []
        for Content in Zone.Content:
            content.append(Content.Value)
        print(Zone.Type, content)

def MakePredictions(Selected, SelectedKeys, Map, self): # this function makes predictions for the selected characters, using a convolutional neural network
    Characters, Dividers, Roots = [], [], [] # there are three catagories that need to be handled differently, characters, dividers and roots, so there is a list for each
    EquationImage = EquationImageModel.objects.get(Id=self.request.session["EquationImageId"]) # this is the equation image object that the characters belong to
    Values = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R","S", "T", "U", "V", "Y", "W", "X", "Z"]
    # the SQL equivalent of this is:
    # SELECT * FROM EquationImageModel WHERE Id = self.request.session["EquationImageId"];
    #however as in real SQL the EquationImage object would not be a foreign key, but its Id
    for Index in range(0, len(Selected)): # this loop goes through all the selections
        FileName = "media/images/Character" + CreateFileName() + str(Index) + ".png" # this is the path where the image that gets run through the neural network will be saved
        DataDict = Selected[Index][SelectedKeys[Index]] # this is the dictionary that contains the furthest points data for the selected character

        Type = Selected[Index]["Type"] # this is the string for the type of character, for example a number, or a letterAJ
        NeuralNetwork = SelectNeuralNetwork(Type) # this selects the correct neural network for the character type

        NeuralNetwork.Type() 

        #NeuralNetwork.Train(200)

        Left = max(DataDict["Left"], 0) # this is the furthest left point of the character, minus 10, but not less than 0
        Right = min(DataDict["Right"], Map.shape[1]) # this is the furthest right point of the character, plus 10, but not more than the width of the image
        Top = max(DataDict["Top"], 0) # this is the furthest top point of the character, minus 10, but not less than 0
        Botom = min(DataDict["Botom"], Map.shape[0]) # this is the furthest botom point of the character, plus 10, but not more than the height of the image

        Data = Map[Top:Botom, Left:Right] # get the subsection of the map that contains the character
        Data = NeuralNetwork.PrepareData(Data, SelectedKeys[Index]) # this function prepares the data for the neural network
#   
        print(FileName)
        img = Image.fromarray(Data[0]*255).convert("L")
        img.save(FileName) # this saves the image that will be run through the neural network, to the path specified above
        Result, Label, _ = NeuralNetwork.Forward(Data) # finally this runs the image through the neural network, and gets the result and the label
        Result = Values[Index]
        print(Result, Label)
#
        NewClassifiedImage = CharacterImage(Image=FileName, EquationImage=EquationImage, CharacterSet=Type, Value="*", EncodedLabel=2) 
        NewClassifiedImage.save()
        ## an entry is made in the CharacterImage table, which is the SQL equivalent of is:
        ## INSERT INTO CharacterImage (Image, EquationImage, CharacterSet, Value, EncodedLabel) VALUES (FileName, EquationImage, Type, Result, Label);
#
        ##as i mentioned roots, division and normal characters are handled differently, so the code below returns the correct object for the character
        ## the classes that this uses are found in Character.py
        if Result == "/": 
            NewDivider = Divider(Selected[Index][SelectedKeys[Index]]["Left"], Selected[Index][SelectedKeys[Index]]["Right"], Selected[Index][SelectedKeys[Index]]["Top"], Selected[Index][SelectedKeys[Index]]["Botom"])
            Dividers.append(NewDivider)
        elif Result == "root":
            NewRoot = Root(Selected[Index][SelectedKeys[Index]]["Left"], Selected[Index][SelectedKeys[Index]]["Right"], Selected[Index][SelectedKeys[Index]]["Top"], Selected[Index][SelectedKeys[Index]]["Botom"])
            Roots.append(NewRoot)
        else:
            NewCharacter = Character(Type, Selected[Index][SelectedKeys[Index]]["Left"], Selected[Index][SelectedKeys[Index]]["Right"], Selected[Index][SelectedKeys[Index]]["Top"], Selected[Index][SelectedKeys[Index]]["Botom"], Result)
            Characters.append(NewCharacter)

    return Characters, Dividers, Roots

def SelectNeuralNetwork(Type):
    print("Selecting Neural Network for " + Type)
    # this works simply by using a dictionary where the key is the type of character, and the value is the neural network object
    NetworksDictionary = { "number": Numbers(), 
                        "+-x/)": Operator(), 
                        "Greek": Greek(), 
                        "U - Z": LettersUZ(), 
                        "A - J": LettersAJ(), 
                        "K - T": LettersKT() }
    return NetworksDictionary[Type]

def MakeZonesFromRootsAndDividers(Roots, Dividers, ImageHeight, ImageWidth): # roots and dividers make zones 
    CanvasZone = Zone(0, ImageWidth, 0, ImageHeight, "Base") # this is the base zone, which is the entire image, it is needed as characters may not be depenedent on roots or dividers
    Zones = [CanvasZone] # this is the list of the zones 
    for Root in Roots: # this loop goes through all the roots
        NewZone = Zone(Root.Left, Root.Right, Root.Top, Root.Botom, "Root")
        Zones.append(NewZone)

    for Divider in Dividers: # this loop goes through all the dividers
        TopLevel = 0
        BottomLevel = ImageHeight
        # when a zone for a divider is made, it initially goes all the way to the top or bottom of the image, but this may need to be changed if there is a root or divider in the way
        for OtherDivider in Dividers: # this loop goes through all the dividers again to check if they are in the way
            if Divider == OtherDivider: 
                pass
            elif Divider.Width < OtherDivider.Width: # if the other divider is smaller than the other divider, then it is the other divider that is in this divider's domain, and so it doesn't need to change it's range for it
                if Divider.Center < OtherDivider.Right and Divider.Center > OtherDivider.Left: # if this divider is smaller than the other divider, and it is in the other divider's domain, then it needs to change it's range
                    # this step is important to account for adjacent dividers, opposed to dividers that are on top of each other

                    # then it need to check which side of the other divider it is on, and change the range accordingly
                    if OtherDivider.Level < Divider.Level: 
                        TopLevel = max(TopLevel, OtherDivider.Level) # if the other divider is on the top, then the numerator zone is capped at the level of the other divider
                        #max is used as the zone may have already been capped by another divider that is closer
                    else:
                        BottomLevel = min(BottomLevel, OtherDivider.Level) # same as above, but for the bottom

        for Root in Roots: # this loop goes through all the roots to check if the divider is in the root
            if Divider.Center < Root.Right and Divider.Center > Root.Left: 
                if Root.Top < Divider.Level and Root.Botom > Divider.Level:
                    # apposed to other dividers if the divider is withing a root then it effects both the numerator and denominator
                    TopLevel = max(TopLevel, Root.Top)
                    BottomLevel = min(BottomLevel, Root.Botom)

        Top = Zone(Divider.Left, Divider.Right, TopLevel, Divider.Level, "x/") # create the numerator zone
        Bottom = Zone(Divider.Left, Divider.Right, Divider.Level, BottomLevel, "/x") # create the denominator zone
        
        Zones.append(Top)
        Zones.append(Bottom)
        # the zones are added to the list of zones
    return Zones

def MergeSortZones(Zones): # this function sorts the zones by width, this is used to make sure that the zones are processed in the correct order
    # a lot of this algorithm depends on which zone is bigger, as the smaller zones may be dependent on the larger zones but larger zones are not dependent on smaller zones
    # that is of course assuming the input image is neat enough

    if len(Zones) > 1:
        Middle = len(Zones) // 2
        # take sublist for the left and right side of the list
        Left = Zones[:Middle]
        Right = Zones[Middle:]

        Right = MergeSortZones(Right) 
        Left = MergeSortZones(Left) # this is a recursive function, it calls itself until the list is only one element long

        #next merge the ordered lists with a linear loop
        Index = 0
        IndexerLeft = 0
        IndexerRight = 0
        while IndexerLeft < len(Left) and IndexerRight < len(Right):
            # check if the left or right side is smaller, and take the smaller one to add to the list
            if Left[IndexerLeft].Width <= Right[IndexerRight].Width:
                Zones[Index] = Left[IndexerLeft] #overide the current element with the smaller one
                IndexerLeft += 1
            else:
                Zones[Index] = Right[IndexerRight]
                IndexerRight += 1
            Index += 1
        
        # at the end of the loop, one of the lists will be empty, so the remaining elements of the other list are added to the end of the list
        while IndexerLeft < len(Left):
            Zones[Index] = Left[IndexerLeft]
            IndexerLeft += 1
            Index += 1

        while IndexerRight < len(Right):
            Zones[Index] = Right[IndexerRight]
            IndexerRight += 1
            Index += 1

    return Zones


def PlaceCharactersInZones(Zones, Characters):
    for Character in Characters: # loop through all the characters
        for Zone in Zones: 
            if Zone.PlaceCharacter(Character): # for each zone check if the character can be placed in it
                break # if it is placed into a zone then the loop is broken, as the character can only be in one zone
    #print("zones and their content (not in order):")
    #PrintZonesContent(Zones)
    return Zones

def PlaceZonesInZones(Zones): # this function does the same as the PlaceCharactersInZones function, but for other zones
    for Index in range(len(Zones)-1):
        for Indexer in range(Index+1, len(Zones)): # this is why it is important that the zones are sorted by width, as the smaller zones need to be placed in the smallest larger zone
            if Zones[Indexer].PlaceZone(Zones[Index]):
                break

    print("zones and their content (not in order):")
    PrintZonesContent(Zones)
    return Zones

def OrderContent(Zones):
    # loops through all the zones telling them to order their content, the OrderContents function also adjusts the zones to fit the content
    for Zone in Zones: 
        Zone.OrderContents() 
    return Zones

def CreateFileName(): # the function creates a unique file name for the image
    return str(int(time.time())) + str(random.randint(0, 1000000))

def TrainNetworks():
    Networks = [Numbers(), Operator(), Greek(), LettersUZ(), LettersAJ(), LettersKT()]

    for Network in Networks:
        Network.Train()

def MakeEquationDataSetFromDataBase(Equations, Verified):
    X_Data  = numpy.empty((0, 398 * 398), dtype=object)
    Y_Data = numpy.array([])
    for Equation in Equations:
        EquationImages = EquationImageModel.objects.filter(Equation=Equation)
        if Verified:
            EquationImages = EquationImageModel.objects.filter(Equation=Equation, Verified=True)
        for EquationImageob in EquationImages:
            ImageData = cv2.imread(EquationImageob.ImageRefined, cv2.IMREAD_GRAYSCALE)
            ImageData = ImageData.reshape(1, 398 * 398)
            print(ImageData.shape)
            Label = EquationImageob.Equation.Standard
            X_Data = numpy.append(X_Data, ImageData, axis=0)
            Y_Data = numpy.append(Y_Data, Label)

    return X_Data, Y_Data

def MakeCharacterDataSetFromDataBase(Types, Verified):
    X_Data  = numpy.empty((0, 28* 28), dtype=object)
    Y_Data = numpy.array([])
    for Set in Types:
        CharactersOfSet = CharacterImage.objects.filter(CharacterSet=Set)
        if Verified:
            CharactersOfSet = CharacterImage.objects.filter(CharacterSet=Set, EquationImage__Verified=True)
        for Character in CharactersOfSet:
            ImageData = cv2.imread(Character.Image, cv2.IMREAD_GRAYSCALE)
            ImageData = ImageData.reshape(1, 28 * 28)
            Label = Character.EncodedLabel
            X_Data = numpy.append(X_Data, ImageData, axis=0)
            Y_Data = numpy.append(Y_Data, Label)

    return X_Data, Y_Data
                    
