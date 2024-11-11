
from rest_framework import status
from rest_framework.views import APIView # import the base class that my custom views will inherit from
from rest_framework.response import Response
from PIL import Image # this is used to save images and resize them
from .utils import * # import all the functions from utils.py
from .Characters import * # import all the functions and classes from Characters.py
from .FirstProcessing import * # import all the functions and classes from FirstProcessing.py
from .ImageRecognition import * # import all the functions and classes from ImageRecognition.py
from .models import * # import all the models from models.py
import numpy as np # numpy will be used to handle matrices
import io, csv
# Create your views here.

class UploadAndProcess(APIView): # this view is used when the user uploads an image
    def post(self, request, format=None): # this function is called then the request type is POST
        print(request.data["Image"][:100])
        image = FormatImageData(request.data["Image"])# use the Utils.py function to convert the url in the request to a PIL image 

        img = np.asarray(image) # convert the PIL image to a numpy array so that it can be processed
        Map, Blended, URL, Refined = Blend(img, 5, 2)
        FileName = CreateFileName() # create a unique file name for the image
        image.save("media/images/Raw" + FileName + ".png") # save the image to the media folder

        Refined = Refined.astype(np.uint8) # convert the numpy array to a numpy array of unsigned integers
        BlendedImage = Image.fromarray(Refined) # convert the numpy array back to a PIL image so that it can be saved
        BlendedImage.save("media/images/Refined" + FileName + ".png") # save the image to the media folder
        # create a new EquationImageModel object containing the file paths to the images
        NewEquationImage = EquationImageModel(ImageRaw="media/images/Raw" + FileName + ".png", ImageRefined="media/images/Refined" + FileName + ".png") 
 
        NewEquationImage.save() # save the EquationImageModel object to the database so that it becomes a record
        # SQL equivalent INSERT INTO EquationImageModel (ImageRaw, ImageRefined) VALUES ("media/images/Raw" + FileName + ".png", "media/images/Refined" + FileName + ".png")
        self.request.session["EquationImageId"] = NewEquationImage.Id # save the id of the EquationImageModel object to the session so that it can be accessed later

        return Response({'Map': Map, 'Blended': Blended, 'URL': URL}, status=status.HTTP_200_OK) # return the map and blended image to the client/front end
    
class SubmitDescription(APIView): # this view is used when the user submits a description for an equation
    def post(self, request, format=None):# this function is called then the request type is POST
        EquationOfDesc = Equation.objects.get(Standard=request.data["Standard"]) # get the equation that the description was submitted for
        # SQL equivalent SELECT * FROM Equation WHERE Standard = request.data["Standard"]
        descrip = request.data["Description"]
        if len(descrip) <= 500: # if the description is longer than 500 characters then return an error
            NewDescription = Description(Equation=EquationOfDesc, Description=request.data["Description"] , Votes=0) # create a new Description object
            NewDescription.save() # save the Description object to the database so that it becomes a record
        # SQL equivalent INSERT INTO Description (Equation, Description, Votes) VALUES (EquationOfDesc, request.data["Description"], 0)
        # get all the descriptions for the equation that the description was submitted for so that they can be returned to the client/front end
        Descriptions = Description.objects.filter(Equation=EquationOfDesc).order_by("-Votes") #acts as SQL query to get all the descriptions for the equation
        # in SQL this would be SELECT * FROM Description WHERE Equation = EquationOfDesc ORDER BY Votes 
        # unpack the description objects into a list of dictionaries so that they can be returned to the client/front end
        DescriptionsSerialized = []
        for i in range(len(Descriptions)):
            DescriptionsSerialized.append({"Id": Descriptions[i].IdCode, "Description": Descriptions[i].Description, "Votes": Descriptions[i].Votes})

        return Response({"Descriptions": DescriptionsSerialized}, status.HTTP_200_OK) # return the descriptions to the client/front end
    
class VoteDescription(APIView): # this view is used when the user clicks the up or down vote button on the display page
    def post(self, request, format=None): # this function is called then the request type is POST
        DescriptionToChange = Description.objects.get(IdCode=request.data["Id"]) # get the description that the vote is for
        DescriptionToChange.Votes += request.data["UpOrDown"] # add to the Votes attribute of the description, UpOrDown will be 1 or -1 depending on whether the vote was up or down
        DescriptionToChange.save() # Update the description in the database
        # The SQL equivalent of the above is UPDATE Description SET Votes = Votes + UpOrDown WHERE IdCode = request.data["Id"]
        EquationOfDescription = DescriptionToChange.Equation # get the equation that the description is for, this is an example of an object foreign key being used to emulate a SQL join
        Descriptions = Description.objects.filter(Equation=EquationOfDescription).order_by("-Votes") 
        # The SQL equivalent of the above is SELECT * FROM Description WHERE Equation = EquationOfDescription ORDER BY Votes
        # unpack the description objects into a list of dictionaries so that they can be returned to the client/front end
        DescriptionsSerialized = []
        for i in range(len(Descriptions)):
            DescriptionsSerialized.append({"Id": Descriptions[i].IdCode, "Description": Descriptions[i].Description, "Votes": Descriptions[i].Votes})

        return Response({"Descriptions": DescriptionsSerialized}, status.HTTP_200_OK) # return the descriptions to the client/front end

class VerifyCharacter(APIView): # this view is called when the user clicks the verify button on the display page
    def post(self, request, format=None):
        UsersEquation = self.request.session["EquationImageId"]# use session to get the EquationImage is to find the equation that the user is working on
        EquationImage = EquationImageModel.objects.get(Id=UsersEquation) # get the EquationImage object from the database
        EquationImage.Verified = True # set the Verified attribute of the EquationImage object to True
        EquationImage.save()
        # The SQL equivalent of the above is UPDATE EquationImageModel SET Verified = True WHERE Id = UsersEquation
        return Response({}, status.HTTP_204_NO_CONTENT) # there is no content to return for this view, so send a 204 response to indicate that the request was successful

class ReceiveSelect(APIView):
    def post(self, request, format=None):
        Selected = request.data["Selected"] # get the selected list of dictonaries from the request
        print(Selected)
        #return Response({}, status.HTTP_204_NO_CONTENT)
        SelectedKeys = [list(elm.keys())[0] for elm in Selected] # get the keys from the selected list of dictionaries and put them in a list
        Map = np.array(request.data["Map"])[1:-1, 1:-1].astype(np.float32) # get the map from the request and convert it to a numpy array, the [1:-1, 1:-1] is to remove the extra padding that was added to the map for the mapping algorithm


        Characters, Dividers, Roots = MakePredictions(Selected, SelectedKeys, Map, self)  # utilise a convolutional neural network to make predictions about the characters in the image, it will return a list of characters, dividers and roots as each needs to be processed differently
    
        Latex, Standard = OrderCharacters(Characters, Dividers, Roots, Map.shape[0], Map.shape[1])[-1].PrintContentInOrder() 
        # the OrderCharacters function will create zones and assign characters to them, it will then order the characters in each zone, then return the zones
        # the last zone in the list will be the base zone, which contains all other zones, so the PrintContentInOrder function will be called on the base zone
        # the PrintContentInOrder function will return a list of the latex and standard form of the equation

        LatexString = "".join(Latex) # convert the latex list to a string
        StandardString = "".join(Standard) # convert the standard form list to a string
        Count = Equation.objects.filter(Standard=StandardString).count() # check if the equation already exists in the database
        # To check the count in SQL you would use SELECT COUNT(*) FROM Equation WHERE Standard = StandardString

        SerialisedDescriptions = []
        if Count == 0: # if the equation does not exist in the database then create a new equation object and save it to the database
            NewEquation = Equation(Standard=StandardString, Latex=LatexString, Instanses=1) # create a new equation object
            NewEquation.save() # save the equation object to the database so that it becomes a record
            # The SQL equivalent of the above is INSERT INTO Equation (Standard, Latex, Instanses) VALUES (StandardString, LatexString, 1)
            EquationImage = EquationImageModel.objects.get(Id=self.request.session["EquationImageId"]) # get the EquationImage object that the user is working on from the database
            EquationImage.Equation = NewEquation # set the Equation attribute of the EquationImage object to the new equation object
            EquationImage.save() # save the EquationImage object to the database so that the changes are saved
            # The SQL equivalent of the above is UPDATE EquationImageModel SET Equation = NewEquationId WHERE Id = self.request.session["EquationImageId"]
            # NewEquation.Id is the primary key of the equation object, so it is used to link the equation object to the EquationImage object
            # to get NewEquationId in SQL  use SELECT Id FROM Equation WHERE Standard = StandardString
        else:
            ExistingEquation = Equation.objects.get(Standard=StandardString) # get the existing equation object from the database
            # The SQL equivalent of the above is SELECT * FROM Equation WHERE Standard = StandardString
            EquationImage = EquationImageModel.objects.get(Id=self.request.session["EquationImageId"]) # get the EquationImage object that the user is working on from the database
            # The SQL equivalent of the above is SELECT * FROM EquationImageModel WHERE Id = self.request.session["EquationImageId"]
            EquationImage.Equation = ExistingEquation # set the Equation attribute of the EquationImage object to the existing equation object
            EquationImage.save()
            # The SQL equivalent of the above is UPDATE EquationImageModel SET Equation = ExistingEquationId WHERE Id = self.request.session["EquationImageId"]
            # ExistingEquation.Id is the primary key of the equation object, so it is used to link the equation object to the EquationImage object
            # to get ExistingEquationId in SQL  use SELECT Id FROM Equation WHERE Standard = StandardString

            # as this equation already exists in the database it may have some descriptions associated with it, so get the descriptions from the database
            Descriptions = Description.objects.filter(Equation=ExistingEquation).order_by("-Votes") # get the descriptions for the existing equation object
            # The SQL equivalent of the above is SELECT * FROM Description WHERE Equation = ExistingEquationId ORDER BY Votes
            for DescriptionLoop in Descriptions:
                SerialisedDescriptions.append({"Description": DescriptionLoop.Description, "Votes": DescriptionLoop.Votes, "Id": DescriptionLoop.IdCode})

            # Next increment the Instanses attribute of the equation object
            ExistingEquation.Instanses += 1 # increment the Instanses attribute of the equation object
            ExistingEquation.save() # save the equation object to the database so that the changes are saved
            # The SQL equivalent of the above is UPDATE Equation SET Instanses = Instanses + 1 WHERE Id = ExistingEquationId
        return Response({'Equation': LatexString, 'StandardForm': StandardString, 'Descriptions':SerialisedDescriptions}, status=status.HTTP_200_OK)
    

class RequestDataSetBuild(APIView):
    def post(self, request, format=None):
        PotentialCharacterSet = ["number", "A - J", "K - T", "U - Z", "Greek", "+-x/)"]
        EquationsBool = request.data["EquationsBool"]
        Verified = request.data["Verified"]
        
        if EquationsBool:
            Equations = Equation.objects.filter(Standard__in=request.data["Equations"])
            print(len(Equations))
            X_train, Y_train = MakeEquationDataSetFromDataBase(Equations, Verified)
            # convert the numpy arrays so that they can be sent to the client
            print(X_train.shape)
            X_train = X_train.tolist()
            Ytrain = Y_train.tolist()


            return Response({'X_train': X_train, 'Y_train': Ytrain}, status=status.HTTP_200_OK)
        else:
            Types = []
            print(request.data)
            for index in range(len(request.data["Types"])):
                if request.data["Types"][index]:
                    Types.append(PotentialCharacterSet[index])

            X_train, Y_train = MakeCharacterDataSetFromDataBase(Types, Verified)
            # convert the numpy arrays so that they can be sent to the client
            X_train = X_train.tolist()
            Y_train = Y_train.tolist()
            return Response({'X_train': X_train, 'Y_train': Y_train}, status=status.HTTP_200_OK)
        
class TrainDataSet(APIView):
    def post(self, request, format=None):
        TrainNetworks()
        # no content
        return Response(status=status.HTTP_200_OK)
        
        

