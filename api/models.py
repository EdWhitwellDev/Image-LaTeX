from django.db import models

class Equation(models.Model): # this class represents the table for equations in the database, it inherits from the models.Model class which allows classes to be converted to tables in the database
    Standard = models.CharField(max_length=200) # primary key 
    Latex = models.CharField(max_length=200)
    Instanses = models.IntegerField( default=0)
    # the SQL equivalent of this class is:
    # CREATE TABLE Equation (
    #     Standard VARCHAR(200) PRIMARY KEY,
    #     Standard VARCHAR(200),
    #     Latex VARCHAR(200),
    #     Instanses INT
    # );

class Description(models.Model): # this class represents the table for descriptions in the database
    IdCode = models.AutoField(primary_key=True)
    Equation = models.ForeignKey('Equation', on_delete=models.SET_NULL, null=True) # takes an equation object as a foreign key, in sql you could use the equation's Standard as a foreign key
    # an added bounus of having an object as a foreign key is that you can access the equation object's attributes from the description object
    # in sql you could use a join to get the equation's attributes
    Description = models.CharField(max_length=500)
    Votes = models.IntegerField( default=0)
    # the SQL equivalent of this class is:
    # CREATE TABLE Description (
    #     IdCode int NOT NULL AUTO_INCREMENT,
    #     Foreign Key (Standard) REFERENCES Equation(Standard),
    #     Description VARCHAR(500),
    #     Votes INT
    # );
    # in order to gain acces to the equation's attributes from the description object, you could use a join in sql
    # so the sql equivalent of this would be:
    # SELECT Description.IdCode, Equation.Standard, Equation.Latex, Equation.Instanses, Description.Description, Description.Votes
    # FROM Description
    # INNER JOIN Equation ON Description.Equation = Equation.Standard;
    

class EquationImageModel(models.Model): # this class represents the table for equation images in the database
    Id = models.AutoField(primary_key=True)
    Equation = models.ForeignKey('Equation', on_delete=models.SET_NULL, null=True)
    ImageRaw = models.CharField(max_length=200) # the path to the image uploaded by the user
    ImageRefined = models.CharField(max_length=200, default=None, null=True) # the path to the image after it has been processed
    Verified = models.BooleanField(default=False, null=True)
    # the SQL equivalent of this class is:
    # CREATE TABLE EquationImageModel (
    #     Id int NOT NULL AUTO_INCREMENT,
    #     Foreign Key (IDcode) REFERENCES Equation(IDcode),
    #     ImageRaw VARCHAR(200),
    #     ImageRefined VARCHAR(200),
    #     Verified BOOLEAN
    # );

class CharacterImage(models.Model): # this class represents the table for character images in the database
    Image= models.CharField(max_length=200)
    EquationImage = models.ForeignKey('EquationImageModel', on_delete=models.CASCADE)
    CharacterSet = models.CharField(max_length=200)
    Value = models.CharField(max_length=1)
    EncodedLabel = models.IntegerField()
    # the SQL equivalent of this class is:
    # CREATE TABLE CharacterImage (
    #     Image VARCHAR(200),
    #     Foreign Key (Id) REFERENCES EquationImageModel(Id),
    #     CharacterSet VARCHAR(200),
    #     Value VARCHAR(1),
    #     EncodedLabel INT
    # );


