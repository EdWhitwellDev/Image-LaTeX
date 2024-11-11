import cv2
from matplotlib import pyplot as plt
import numpy
from .Characters import *
from scipy import ndimage
from .models import *
class ConvolutionLayer:
    def __init__(self, NumberOfKernals, KernelSize, type):
        self.NumberOfKernals = NumberOfKernals
        self.KernelSize = KernelSize
        self.type = type
        self.Kernals = numpy.loadtxt("D:\\DjangoProjects\\EquationTextNEA\\NeaAI\\api\\Kernals"+type+".txt", delimiter=",").reshape(16, 3, 3)# as this is using a pre trained model it will load the kernels from a file

    def SaveKernals(self, type):
        numpy.savetxt("D:\\DjangoProjects\\EquationTextNEA\\NeaAI\\api\\Kernals"+type+".txt", self.Kernals.reshape(self.Kernals.shape[0], self.KernelSize**2), delimiter=',') # if doing any training on the server this can be used to update the kernels

    def KernalOverlays(self, Input): # as both forward loop through the image in the same way a seperate function for the loop is used
        self.Input = Input # store the Input for use in the backward function
        #loop through each pixel in the image
        for i in range(Input.shape[1] - self.KernelSize + 1):
            for j in range(Input.shape[2] - self.KernelSize + 1):
                KernalOverlay = Input[:, i:i+self.KernelSize, j:j+self.KernelSize] # get the 3x3 sub section of each image, the : means that it takes all subsections for that dimension, here it is applied to the first dimension as that is the dimension that stores individual images
                yield KernalOverlay, i, j # use yeild else it will ablsutly destory the memory when batch training (alternatively you can use a list and append to it)

    def forward(self, Input):
        Output = numpy.zeros((Input.shape[0], self.NumberOfKernals, Input.shape[1] - self.KernelSize + 1, Input.shape[2] - self.KernelSize + 1)) # creates an empty array with the shape that will be the output
        Area = self.KernelSize**2 # the area of the kernal is used a lot to reshape the patch so it is stored in a variable
        for Kernal, i, j in self.KernalOverlays(Input):
            Result = numpy.dot(Kernal.reshape(Kernal.shape[0], Area), self.Kernals.reshape(self.Kernals.shape[0], Area).T) # the kernals are reshaped to be 2D and then the dot product is taken with the input image patch, the result will be of shape (batch size, number of kernals)

            Output[:, :, i, j] = Result # using numpy broadcasting the result is added to the output array, this means that at each i,j postion for all the first two dimensions the corresponding result is added

        return Output

    def backward(self, OutputGradient, LearnRate):
        DerivCostKernal = numpy.zeros(self.Kernals.shape) # creates an empty array with the shape of the kernals and with the number of kernals
        for Patch, i, j in self.KernalOverlays(self.Input): # calls the function that returns each valid kernal overlay
            Gradient = OutputGradient[:, :, i, j]# gets the Derivatives for the current patch
            Product = numpy.tensordot(Gradient, Patch, axes=([0], [0])) # perform a tensor dot, this multiplies the gradient with every value in the patch element wise (gradient one for patch one and gradient two for patch two, ect) and sums over the batch (dimension 0)

            Product = Product / self.Input.shape[0] # divide by the batch size to get the average
            DerivCostKernal += Product # as the kernels are shared over multiple patches, the gradient at this patch is added to the total gradient for the kernal

        self.Kernals -= LearnRate * DerivCostKernal # update the kernals
        return DerivCostKernal 

class PoolingLayer:
    # this just reduces the size of the image by taking the max value of each kernal
    def __init__(self, KernalSize):
        self.KernalSize = KernalSize
        self.Area = KernalSize**2

    def Relu(self, Z):
        self.Z = Z # store the input for use in the Relu Deriv function
        return numpy.maximum(Z, 0) # this uses numpy to return either the input or 0, whichever is greater for each element

    def ReluDeriv(self):
        Z = self.Z
        return Z > 0 # this returns a boolean array, where the value is true if the input was greater than 0

    def forward(self, Input):
        self.Input = Input # store the input for use in the backward function
        Map = numpy.zeros(Input.shape) # creates an empty array with the shape of the input for the map which will be used in the backward function
        Output = numpy.zeros((Input.shape[0], Input.shape[1],  Input.shape[2] // self.KernalSize, Input.shape[3] // self.KernalSize)) # creates an empty array with the shape that will be the output
        Area = self.Area # the area of the kernal is used a lot to reshape the patch so it is stored in a variable
        for i in range(Input.shape[2] // self.KernalSize):
            StartI = i * self.KernalSize 
            for j in range(Input.shape[3] // self.KernalSize):
                StartJ = j * self.KernalSize
                Kernal = Input[:, :, StartI : (StartI+self.KernalSize), StartJ:(StartJ+self.KernalSize)] # gets a subsection of the input for each image in the batch and each kernal in the image
                
                KernalFlat = Kernal.reshape(Kernal.shape[0], Kernal.shape[1], Area) # reshapes the patchs to be one dimensional for each image and kernal 
                MaxIndex = numpy.argmax(KernalFlat, axis = 2) # gets the index of the max value for each patch
                MaxValues = numpy.max(KernalFlat, axis = 2) # gets the max value for each patch
                Output[:, :, i, j] = MaxValues # adds the max value for each patch to the output
                Mapped = numpy.zeros(KernalFlat.shape) # creates an empty array with the shape of the patchs
                Mapped[numpy.arange(Kernal.shape[0])[:, None], numpy.arange(Kernal.shape[1]), MaxIndex] = 1 # sets the index of the max value for each patch to 1
                Mapped = Mapped.reshape(Kernal.shape) # reshapes the map so that it is broadcastable with the main map
                Map[:, :, StartI : (StartI+2), StartJ:(StartJ+2)] = Mapped # adds the map for this patch to the main map
        self.Map = Map # stores the map for use in the backward function
        return Output


    def forwardLite(self, Input): # this is a lite version of the forward function that is used when not backpropagating as it has no map.
        self.Input = Input
        Output = numpy.zeros((Input.shape[0], Input.shape[1],  Input.shape[2] // self.KernalSize, Input.shape[3] // self.KernalSize))

        StartI = - self.KernalSize
        for i in range(Input.shape[2] // self.KernalSize):
            StartI += self.KernalSize
            StartJ = - self.KernalSize
            for j in range(Input.shape[3] // self.KernalSize):
                StartJ += self.KernalSize
                Kernal = Input[:, :, StartI : (StartI+self.KernalSize), StartJ:(StartJ+self.KernalSize)]
                MaxValues = numpy.amax(Kernal, axis = (2, 3))
                Output[:, :, i, j] = MaxValues

        Output = self.Relu(Output)
        return Output

    def backward(self, OutputGradient): # this uses the map to backpropagate the gradient
        # there are no multipications on this layer so the gradient is just passed back through the map
        # however the gradient needs to be assinged to the correct inputs
        Map = self.Map
        shape = Map.shape
        MapFlat = Map.flatten() # flattens the map so that it is easier to broadcast the gradient
        OutputGradientFlat = OutputGradient.flatten() # flattens the gradient so that it is easier to broadcast with the map
        MapFlat[MapFlat == 1] = OutputGradientFlat # this broadcasts the gradient with the map, think of it as looping through the map and when it finds a 1 it pops the value of the gradient (which in this analogy is a queue) and assigns it to the map
        MapFlat = MapFlat.reshape(shape) # reshapes the map so that it is the same shape as the input

        return MapFlat # returns the gradient
    
class SoftMax:
    def __init__(self, InputSize, OutputSize, type):
        # as this is a pre trained network, the weights and bias are loaded from a file
        self.Weights = numpy.loadtxt("D:\\DjangoProjects\\EquationTextNEA\\NeaAI\\api\\Weights"+type+".txt", delimiter=",") # loads the weights from a file
        self.Bias = numpy.loadtxt("D:\\DjangoProjects\\EquationTextNEA\\NeaAI\\api\\Bias"+type+".txt", delimiter=",") # loads the bias from a file

    def Save(self, type):
        # if further training is required, the updated weights and bias can be saved to a file
        numpy.savetxt("D:\\DjangoProjects\\EquationTextNEA\\NeaAI\\api\\Weights"+type+".txt", self.Weights, delimiter = ",") # saves the weights to a file
        numpy.savetxt("D:\\DjangoProjects\\EquationTextNEA\\NeaAI\\api\\Bias"+type+".txt", self.Bias, delimiter = ",") # saves the bias to a file

    def forward(self, Input):
        self.Shape = Input.shape 

        Input = numpy.rollaxis(Input, 1, 4) 
        FlattenedInput = Input.reshape((self.Shape[0], self.Shape[1] * self.Shape[2] * self.Shape[3])) # flattens each image in the batch so that a dot product can be used

        self.VectorInput = FlattenedInput # stores the flattened input for use in the backward function
        Weights = self.Weights
        Net = numpy.dot(FlattenedInput, Weights.T) + self.Bias # calculates the net input for each neuron
        # it does this by multiplying the input by the weights element wise and adding the bias
        # the returned array is a 2d array with the first dimension being the batch and the second being the outputs
        Eed = numpy.exp(Net.T) # creates and array of e^net of each neuron in the batch
        Sum = numpy.sum(Eed, axis = 0) # sums the e^net of each neuron for each image in the batch

        SoftMaxed = (Eed / Sum).T # divides each e^net by the sum of the e^net for each image in the batch to get the softmaxed output
        return SoftMaxed # returns the softmaxed output

    def backward(self, CostGradient, LearnRate):
        Inputs = self.VectorInput

        self.Bias -= (numpy.sum(CostGradient.copy(), axis=1) / (CostGradient.shape[1] / LearnRate)) # as the bias is just added to the net input, the dnet/dbias is 1 so the gradient is just the cost gradient
        # as neural networks are trained in batches, the gradient is averaged over the batch

        DerivWeights = CostGradient.dot(Inputs) / Inputs.shape[0] # calculates the derivative of the cost with respect to the weights and averages it over the batch
        # the derivative of the cost with respect to the weights is the cost gradient multiplied by the input to the neuron
        DerivWeights = DerivWeights * LearnRate 

        DerivInputs = self.Weights.T.dot(CostGradient) # calculates the derivative of the cost with respect to the inputs
        # the derivative of the cost with respect to the inputs is the cost gradient multiplied by the weights the inputs were multiplied by in the forward pass
        # as inputs effect output neurons the dcost/dnets are multiplied by the respective weights and then summed to get the dcost/dinput

        self.Weights -= DerivWeights # updates the weights for gradient descent

        return DerivInputs
 
class Network:

    def get_predictions(self, Output):
        Predictions = numpy.argmax(Output, 0) # gets the index of the highest value in the output, this is the predicted class
        return Predictions
        
    def Forward(self, Input):
        self.Load()
        for Layer in self.layers: # loops through each layer in the network
            Input = Layer.forward(Input) # uses polymorphism to call the forward function of the layer

        output = self.get_predictions(Input.T) # gets the predicted index
        Result = self.Decode(output) # gets the predicted class
        return Result, output, Input
    
    def Backward(self, CostGradient, LearnRate):
        for Layer in self.layers[::-1]:
            if type(Layer) == SoftMax or type(Layer) == ConvolutionLayer:
                CostGradient = Layer.backward(CostGradient, LearnRate)
            elif type(Layer) == PoolingLayer:
                CostGradient = Layer.backward(CostGradient)

        return CostGradient
    
    def ExtractImage(self, Maped, Target):

        X, Y = Maped.shape
        Canvas = numpy.full(shape = (X, Y), fill_value = self.Background) # create an empty matrix to act as a canvas
        Canvas[Maped == float(Target)] = self.Foreground # sets the pixels that are the target to white, doing it like this means that only pixels of this group are moved to the canvas
        Canvas = Canvas.astype(numpy.float32) # converts the canvas to an unsigned 8 bit integer
        # save the canvas to a file
        #cv2.imwrite("D:\\DjangoProjects\\EquationTextNEA\\NeaAI\\api\\Canvas.png", Canvas)

        return Canvas
    
    def Normalize(self, Data):
        Y, X = Data.shape
        if X * (3/5) > Y: # if the image is too wide, i've found the 3/5 ratio to be the best for the network
            Amount = int((X * (3/5) - Y) // 2) # calculates the amount of padding needed
            Data = numpy.pad(Data, ((Amount,Amount),(0,0)), 'constant', constant_values=self.Background) # pads the image with 0s
        elif Y * (3/5) > X: # same as above but for if the image is too tall
            Amount = int((Y * (3/5) - X) // 2)
            Data = numpy.pad(Data, ((0,0),(Amount,Amount)), 'constant', constant_values=self.Background)
        return Data
    
    def Resize(self, Data):
        Data = cv2.resize(Data, (self.CenterBox, self.CenterBox), interpolation = cv2.INTER_AREA) # resizes the image to 20x20, this is in line with the dataset normalisation, that centers the image in a 20x20 box
        return Data
    
    def Pad(self, Data):
        Data = numpy.pad(Data, pad_width=((self.InputDimension-self.CenterBox)//2), mode='constant', constant_values=self.Background)  # pads the image with 0s to make it 28x28
        Data = Data.astype(numpy.uint8) # converts the data to a float32
        #cv2.imwrite("D:\\DjangoProjects\\EquationTextNEA\\NeaAI\\api\\Canvas.png", Data)
        return Data

    def PrepareData(self, Map, Target):

        Data = self.ExtractImage(Map, Target) # extracts the image from the map
        Data = self.Normalize(Data) # add padding to maintain the aspect ratio
        Data = self.Resize(Data) # resizes the image to 20x20
        Data = self.Pad(Data) # pads the image to make it 28x28
        Data = Data[numpy.newaxis] # adds a dimension to the array so that it can be used in the network
        Data = Data.astype(numpy.float32) # converts the data to a float32
        Data = Data / 255 # normalises the data
        Data = self.AddNoise(Data, 0.001) # adds noise to the image
        Data = Data.reshape(Data.shape[0], self.InputDimension, self.InputDimension) # reshapes the data to be in the correct format for the network
        return Data

    def Decode(self, Output):
        return self.Classes[Output[0]] # returns the actual value not just the index
    
    def BuildDataSet(self):
        BaseTrainX = numpy.empty((0, self.InputDimension*self.InputDimension), dtype=object)
        BaseTrainY = numpy.array([])
        PotentialCharactersImages = CharacterImage.objects.filter(CharacterSet=self.Set, EquationImage__Verified=True) # gets all the images of the characters that are in the training set
        for CharacterImageob in PotentialCharactersImages:
            BaseTrainX = numpy.append(BaseTrainX, cv2.imread(CharacterImageob.Image, cv2.IMREAD_GRAYSCALE).reshape(1, self.InputDimension*self.InputDimension), axis=0)
            BaseTrainY = numpy.append(BaseTrainY, CharacterImageob.EncodedLabel)

        return BaseTrainX, BaseTrainY
    
    def AddNoise(self, image, var):
      mean = 0
      sigma = var**0.5
      gauss = numpy.random.normal(mean,sigma,(image.shape))
      gauss = gauss.reshape(image.shape)
      noisy = image + gauss
      return noisy.reshape(image.shape[0], self.InputDimension * self.InputDimension)

    def Rotate(self, images, var):
        rotated = []
        for image in images:
            angle = numpy.random.uniform(-var, var)
            image = image.reshape(self.InputDimension, self.InputDimension)
            image = image.astype(numpy.uint8)
            rotated.append(ndimage.rotate(image, angle, reshape=False, mode='nearest'))
        return numpy.array(rotated).reshape(images.shape[0], self.InputDimension * self.InputDimension)

    def Translate(self, images, var):
        translated = []
        for image in images:
            image = image.reshape(self.InputDimension, self.InputDimension)
            x = numpy.random.randint(-var, var)
            y = numpy.random.randint(-var, var)
            image = image.astype(numpy.uint8)

            translated.append(ndimage.shift(image, (x, y), mode='nearest'))
        return numpy.array(translated).reshape(images.shape[0], self.InputDimension * self.InputDimension)

    def EncodeLable(self, Y):
        Y = Y.astype(numpy.uint8)
        Desired = numpy.zeros((Y.size, len(self.Classes)))
        Desired[numpy.arange(Y.size), Y] = 1 # Dersired is a 2d array the first dimension is covered by the numpy.arange(Y.size) which does the equivilent to the Indexer in a for loop, 
        #the 2nd d is dictated by that index in Y
        return Desired

    def TrainBatch(self, XTrain, YTrain):
        _, _, Output = self.Forward(XTrain) # gets the output of the network
        Labels = self.EncodeLable(YTrain) # encodes the labels

        Gradient = Output - Labels # calculates the gradient
        Gradient = Gradient.T # transposes the gradient
        _ = self.Backward(Gradient, 0.5)

    def SaveWeightsECT(self):
        self.layers[0].SaveKernals(self.Type())
        self.layers[2].Save(self.Type())
        print("saved")

    def Train(self, Epochs):
        XTrain, YTrain = self.BuildDataSet() # loads the training data
        # augments the training data to increase the size of the dataset to make the network more robust
        XTrain_Noise = self.AddNoise(XTrain, 0.001) # adds noise to the training data
        XTrain_Rotated = self.Rotate(XTrain, 20) # rotates the training data
        XTrain_Translated = self.Translate(XTrain, 2) # translates the training data
        XTrain_Noise_Rotated = self.Rotate(XTrain_Noise.copy(), 20) # rotates the noisy training data
        XTrain_Noise_Translated = self.Translate(XTrain_Noise.copy(), 2) # translates the noisy training data
        XTrain_Rotated_Translated = self.Translate(XTrain_Rotated.copy(), 2) # translates the rotated training data
        XTrain_Rotated_Translated_Noise = self.AddNoise(XTrain_Rotated_Translated.copy(), 0.001) # adds noise to the rotated and translated training data

        XTrain = numpy.stack([XTrain, XTrain_Noise, XTrain_Noise_Rotated, XTrain_Noise_Translated, XTrain_Rotated, XTrain_Rotated_Translated, XTrain_Rotated_Translated_Noise, XTrain_Translated]) # stacks the training data together
        XTrain = XTrain.reshape(XTrain.shape[0] * XTrain.shape[1], XTrain.shape[2]) # reshapes the training data to be in the correct format
        YTrain = numpy.tile(YTrain, 8) # repeats the labels 8 times to match the training data

        permutation = numpy.random.permutation(len(XTrain))
        XTrain = XTrain[permutation]
        YTrain = YTrain[permutation]

        XTrain = XTrain.astype(numpy.float32) # converts the training data to a float32
        XTrain = XTrain / 255 # normalises the training data
        XTrain = XTrain.reshape(XTrain.shape[0], self.InputDimension, self.InputDimension) # reshapes the training data to be in the correct format

        BatchSize = 16
        for index in range(Epochs): # loops through the epochs
            for i in range(0, len(XTrain), BatchSize): # loops through the training data in batches
                XTrainBatch = XTrain[i:i+BatchSize] # gets the batch of training data
                YTrainBatch = YTrain[i:i+BatchSize] # gets the batch of labels
                self.TrainBatch(XTrainBatch, YTrainBatch) # trains the network on the batch

        self.SaveWeightsECT()



class Numbers(Network): # inherits from the network class so that it can use the universal functions
    def __init__(self):
        self.InputDimension = 28 # the input dimension of the network, this is used to reshape the input to the correct size
        self.CenterBox = 20
        self.Background = 0
        self.Foreground = 255
        self.Set = "numbers" # the name of the dataset that the network is trained on
    def Type(self):
        return ""
    
    def Load(self):
        # this is the network architecture
        print("Loading Network Numbers")
        self.layers = [
            ConvolutionLayer(16,3, ""), # layer with 16 3x3 filters, output (26,26,16)
            PoolingLayer(2), # pooling layer 2x2, output (13,13,16)
            SoftMax(13*13*16, 10, "") # softmax layer with 13*13*16 input and 10 output 
        ]
        self.Classes = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"] # the classes that the network can predict

class LettersAJ(Network):

    def __init__(self):
        self.InputDimension = 28
        self.CenterBox = 20
        self.Background = 0
        self.Foreground = 255
        self.Set = "A - J"
    def Type(self):
        return "LAJ"

    def Load(self):
        self.layers = [
            ConvolutionLayer(16,3, "LAJ"), # layer with 16 3x3 filters, output (26,26,16), the string is used to load the correct weights and bias
            PoolingLayer(2), # pooling layer 2x2, output (13,13,16)

            SoftMax(13*13*16, 10, "LAJ") # softmax layer with 13*13*16 input and 10 output
        ]

        self.Classes = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]

    


class LettersKT(Network):
    def __init__(self):
        self.InputDimension = 28
        self.CenterBox = 20
        self.Background = 0
        self.Foreground = 255
        self.Set = "K - T"
    def Type(self):
        return "LKT"

    def Load(self):
        self.layers = [
            ConvolutionLayer(16,3, "LKT"), # layer with 16 3x3 filters, output (26,26,16)
            PoolingLayer(2), # pooling layer 2x2, output (13,13,16)
            SoftMax(13*13*16, 10, "LKT") # softmax layer with 13*13*16 input and 10 output
        ]
        self.Classes = ["K", "L", "M", "N", "O", "P", "Q", "R", "S", "T"]

class LettersUZ(Network):
    def __init__(self):
        self.InputDimension = 28
        self.CenterBox = 20
        self.Background = 0
        self.Foreground = 255
        self.Set = "U - Z"
    def Type(self):
        return "LUZ"

    def Load(self):
        self.layers = [
            ConvolutionLayer(16,3, "LUZ"), # layer with 16 3x3 filters, output (26,26,16)
            PoolingLayer(2), # pooling layer 2x2, output (13,13,16)

            SoftMax(13*13*16, 6, "LUZ") # softmax layer with 13*13*16 input and 10 output 
        ]
        self.Classes = ["U", "V", "W", "X", "Y", "Z"]

class Greek(Network):
    def __init__(self):
        self.InputDimension = 14
        self.CenterBox = 10
        self.Background = 255
        self.Foreground = 0
        self.Set = "Greek"
    def Type(self):
        return "G"
    def Load(self):
        self.layers = [
            ConvolutionLayer(16,3, "G"), # layer with 16 3x3 filters, output (26,26,16)
            PoolingLayer(2), # pooling layer 2x2, output (13,13,16)
            SoftMax(6*6*16, 10, "G") # softmax layer with 13*13*16 input and 10 output
        ]

        self.Classes = ['alpha','beta','gamma','delta','epsilon','theta', 'lambda','mu','pi', 'sigma']

    def BuildDataSet(self):
        BaseTrainX = numpy.loadtxt("Data/Operator/Train.txt", delimiter=",") # loads the training data
        BaseTrainY = numpy.loadtxt("Data/Operator/TrainLabels.txt", delimiter=",") # loads the training labels

        PotentialCharactersImages = CharacterImage.objects.filter(CharacterSet="Greek", EquationImage__Verified=True) # gets all the images of the characters that are in the training set
        for CharacterImage in PotentialCharactersImages:
            BaseTrainX = numpy.append(BaseTrainX, cv2.imread(CharacterImage.Image, cv2.IMREAD_GRAYSCALE).reshape(1, 196), axis=0)
            BaseTrainY = numpy.append(BaseTrainY, CharacterImage.EncodedLabel)

        return BaseTrainX, BaseTrainY

class Operator(Network):
    def __init__(self):
        self.InputDimension = 28
        self.CenterBox = 20
        self.Background = 0
        self.Foreground = 255
        self.Set = "+-x/)"
    def Type(self):
        return "O"
    def Load(self):
        self.layers = [
            ConvolutionLayer(16,3, "O"), # layer with 16 3x3 filters, output (26,26,16)
            PoolingLayer(2), # pooling layer 2x2, output (13,13,16)
            SoftMax(13*13*16, 7, "O") # softmax layer with 13*13*16 input and 10 output 
        ]
        self.Classes = ["+", "-", "*", "/", "(", ")", "root"]





