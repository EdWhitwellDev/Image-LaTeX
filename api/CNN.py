import numpy

def CNNMain(Data):
    Conv = Convolve(Data)
    Pool = PoolForward(Conv)
    Softmax = SoftMax(Pool)
    Prediction = GetPrediction(Softmax.T)
    return Prediction

def ConvPatcher(Input, KernalSize):
    for i in range(Input.shape[1] - KernalSize + 1):
        for j in range(Input.shape[2] - KernalSize + 1):
            Patch = Input[:, i:i+KernalSize, j:j+KernalSize]
            yield Patch, i, j

def Convolve(Input):
    Kernals = numpy.loadtxt("D:\\DjangoProjects\\EquationTextNEA\\NeaAI\\api\\Kernals.txt", delimiter=",").reshape(16, 3, 3)
    Output = numpy.zeros((Input.shape[0], 16, Input.shape[1]-2, Input.shape[2]-2))
    for Patch, i, j in ConvPatcher(Input, 3):
        Result = numpy.dot(Patch.reshape(Patch.shape[0], 3**2), Kernals.reshape(Kernals.shape[0], 3**2).T)
        Output[:, :, i,j] = Result
    return Output

def PoolForward(Input):
    Output = numpy.zeros((Input.shape[0], Input.shape[1], Input.shape[2] // 2, Input.shape[3] // 2))
    for i in range(Input.shape[2] // 2):
        for j in range(Input.shape[3] // 2):  
            StartI = i * 2
            StartJ = j * 2
            Patch = Input[:, :, StartI:StartI+2, StartJ:StartJ+2]
            MaxValues = numpy.amax(Patch, axis=(2,3))
            Output[:, :, i, j] = MaxValues

    return Output

def Relu(Input):
    return numpy.maximum(Input, 0)

def GetPrediction(Softmax):
    return numpy.argmax(Softmax, 0)

def SoftMax(Input):
    Weight = numpy.loadtxt("D:\\DjangoProjects\\EquationTextNEA\\NeaAI\\api\\Weights.txt", delimiter=",")
    Bias = numpy.loadtxt("D:\\DjangoProjects\\EquationTextNEA\\NeaAI\\api\\Bias.txt", delimiter=",")
    Shape = Input.shape
    Input = numpy.rollaxis(Input, 1, 4)
    FlattenedInput = Input.reshape(Shape[0], Shape[1] * Shape[2] * Shape[3])
    FlattenedInput = Relu(FlattenedInput)
    Net = numpy.dot(FlattenedInput, Weight.T) + Bias
    Eed = numpy.exp(Net.T)
    Sum = numpy.sum(Eed, axis=0)
    Softmax = (Eed / Sum).T
    return Softmax
