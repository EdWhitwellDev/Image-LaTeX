class Character: # this class is used to neatly store a character's data
    def __init__(self, Type, Left, Right, Top, Botom, Value):
        self.Value = Value

        self.Type = Type
        self.Left = Left
        self.Right = Right
        self.Top = Top
        self.Botom = Botom
        self.Width = Right - Left
        self.Height = Botom - Top

        self.Center = (Left + Right) / 2, (Top + Botom) / 2


class Divider: # this class is used to neatly store a divider's data
    def __init__(self, Left, Right, Top, Botom):
        self.Left = Left
        self.Right = Right
        self.Top = Top
        self.Botom = Botom
        self.Width = Right - Left
        self.Center = (Right + Left) / 2
        self.Level = (Top + Botom) / 2

class Root: # this class is used to neatly store a root's data
    def __init__(self, Left, Right, Top, Botom):
        self.Left = Left
        self.Right = Right
        self.Top = Top
        self.Botom = Botom
        self.Width = Right - Left
        self.Height = Botom - Top
        self.Center = (Top + Botom) / 2
        self.Area = self.Width * self.Height

class Zone: 
    def __init__(self, Left, Right, Top, Botom, Type):
        self.Value = Type
        self.Type = Type
        self.Left = Left
        self.Right = Right
        self.Top = Top
        self.Botom = Botom
        self.Width = Right - Left
        self.Height = Botom - Top
        self.Area = self.Width * self.Height
        self.Center = (Left + Right) / 2, (Top + Botom) / 2
        self.Content = []
        # each different type of zone has a different wrapper for the output, for both latex and standard
        self.OutputBase = ""
        self.OutputEnd = ""
        self.OutputBaseStandard = ""
        self.OutputEndStandard = ""
        if Type == "x/": 
            self.OutputBase = "\\frac{"
            self.OutputEnd = "}"
            self.OutputBaseStandard = "("
            self.OutputEndStandard = ")"
        if Type == "/x":
            self.OutputBase = "{"
            self.OutputEnd = "}"
            self.OutputBaseStandard = "/("
            self.OutputEndStandard = ")"
        if Type == "Root":
            self.OutputBase = "\\sqrt{"
            self.OutputEnd = "}"
            self.OutputBaseStandard = "sqrt("
            self.OutputEndStandard = ")"


    def ChangeBounds(self, NewTop, NewBottom): # in the event that a divider is a sub divider this is used to change the bounds of the zone to fit into the super divider/root
        self.Top = NewTop
        self.Botom = NewBottom
        self.Height = NewBottom - NewTop
        self.Area = self.Width * self.Height
        self.Center = (self.Left + self.Right) / 2, (self.Top + self.Botom) / 2

    def PlaceCharacter(self, Character): # this function is used to place a character into the zone 
        if Character.Center[0] > self.Left and Character.Center[0] < self.Right and Character.Center[1] > self.Top and Character.Center[1] < self.Botom:
            self.Content.append(Character) # if the character is within the bounds of the zone it is placed into the zone
            return True # the function returns true to indicate that the character was placed so the loop can break, so that the character is not placed into multiple zones
        return False 
    
    def PlaceZone(self, Zone): # zones can be within other zones, and therefore needs to be included within the wrapper, this function is used to place a zone within a zone
        if Zone.Center[0] > self.Left and Zone.Center[0] < self.Right and Zone.Center[1] > self.Top and Zone.Center[1] < self.Botom: # if the zone is within the bounds of the zone
            self.Content.append(Zone) # python polymorphism allows for the same list to be used for both characters and zones
            return True # this indicates the loop needs to break
        return False
    
    def OrderContents(self): # this function is used to order the contents of the zone, this is done by bubble sorting the characters by their center x position
        Top = self.Botom
        Bottom = self.Top
        for Index in range(len(self.Content)):
            for Indexer in range(len(self.Content)-Index-1):
                Top = min(Top, self.Content[Index].Top) # is this the top of the zone
                Bottom = max(Bottom, self.Content[Index].Botom) # is this the bottom of the zone
                if self.Content[Indexer].Center[0] > self.Content[Indexer+1].Center[0]:
                    self.Content[Indexer], self.Content[Indexer+1] = self.Content[Indexer+1], self.Content[Indexer] # swap the characters

        self.ChangeBounds(Top, Bottom) # at the end the bounds are changed to fit the characters, this makes placing zones within the zone more accurate


    def PrintContentInOrder(self):

        #print(self.Content)

        if len(self.Content) == 1: # if there is only one character in the zone, then the brackets are not needed for the standard wrapper
            if self.Type == "x/":
                self.OutputBaseStandard = ""
                self.OutputEndStandard = ""
            if self.Type == "/x":
                self.OutputBaseStandard = "/"
                self.OutputEndStandard = ""
            

        Valueslatex = [self.OutputBase] # start the latex output with the wrapper
        ValuesStandard = [self.OutputBaseStandard] # do the same for the standard output
        SkipUntil = 0 # this is used to skip items that were exponents
        for Index in range(len(self.Content)):
            if Index < SkipUntil:  # if the index is less than the skip until, then the index is an exponent and should be skipped
                print("skipped" + str(Index))
                continue
            if isinstance(self.Content[Index], Zone): # if the item is a zone, then the zone's contents need to be wrapped and added to the output
                SubZoneValuesLatex, SubZoneValuesStandard = self.Content[Index].PrintContentInOrder() # get the output from the zone by calling the function recursively
                Valueslatex += SubZoneValuesLatex # add the output to the current output
                ValuesStandard += SubZoneValuesStandard # do the same for the standard output
            else: # if the item is just a character
                if self.Content[Index].Type == "Greek": # if the character is a greek letter, then it needs to be converted to latex
                    Valueslatex.append("\\") # add the latex version of the character to the output
                    Valueslatex.append(self.Content[Index].Value) 
                    ValuesStandard.append(self.Content[Index].Value) # add the character to the output
                    ValuesStandard.append(" ") # add a space to the output
                    Valueslatex.append(" ") # add a space to the output
                else:
                    Valueslatex.append(self.Content[Index].Value)
                    ValuesStandard.append(self.Content[Index].Value)
                CurrentCenter = self.Content[Index].Center[1] # get the y center of the character, this is used to determine if the next character is an exponent
                CurrentTop = self.Content[Index].Top # get the top of the character to determine if the next zone is an exponent
                Exponents = ["^"]
                ExponentsStandard = ["^"] # these are used to store the exponents, they start with the ^ symbol to indicate that the next character is an exponent
                Flag = False # the flag is used to determine if the next character was an exponent and so if the exponents lists should be added to the output
                skip = 0 # this is used to skip the next character as it is an exponent
                for Indexer in range(Index+1, len(self.Content)): # loop through the rest of the characters in the zone
                    # going forward i have tried to determin rules as to whether a character is an exponent, this is not a perfect system, but it works for most cases
                    #if skip > 0: # this handles the denominator as an exponent
                    #    if Indexer == len(self.Content)-1:
                    #        continue # if the index is the last character in the zone
                    #    skip -= 1
                    #    print("skipping" + str(Indexer))
                    #    continue

                    print("Indexer: ", Indexer)
                    if isinstance(self.Content[Indexer], Character):

                        if  self.Content[Indexer].Botom < CurrentCenter: # the rule for other characters is that if the bottom of the character is higher than the y center of the current character, then it is an exponent
                            if self.Content[Indexer].Type == "Greek":
                                Exponents.append("\\")
                                Exponents.append(self.Content[Indexer].Value) # add the character to the exponents list
                                ExponentsStandard.append(self.Content[Indexer].Value) # add the character to the exponents list
                                ExponentsStandard.append(" ") # add the character to the exponents list
                                Exponents.append(" ")
                            else:
                                Exponents.append(self.Content[Indexer].Value) 
                                ExponentsStandard.append(self.Content[Indexer].Value) # add the character to the exponents list
                            Flag = True # set the flag to true to indicate that there are exponents
                        else:
                            break # if the character is not an exponent, then the loop can break as the rest of the characters are not exponents
                    elif self.Content[Indexer].Type == "x/": # if the zone is a fraction, then only the numerator is checked#

                        #the algorithm can always assume the numerator comes before the denominator as that was the order they were added and the sorts would not have switched them as they have == width
                        if self.Content[Indexer].Center[1] < CurrentTop: # the rule for fractions is that if the y center of the numerator is higher than the top of the current character, then it is an exponent
                            SubZoneValuesLatex, SubZoneValuesStandard = self.Content[Indexer].PrintContentInOrder() # again the zone's contents are wrapped by calling the function recursively
                            Exponents += SubZoneValuesLatex 
                            ExponentsStandard += SubZoneValuesStandard # add the output to the exponents list
                            SubZoneValuesLatex, SubZoneValuesStandard = self.Content[Indexer+1].PrintContentInOrder() # the denominator is also an exponent, so it is also added to the exponents list
                            Exponents += SubZoneValuesLatex
                            ExponentsStandard += SubZoneValuesStandard
                            skip += 1 # the skip is incremented by one as the next character is the denominator
                            Flag = True # the flag is set to true to indicate that there are exponents
                        else:
                            break
                    elif self.Content[Indexer].Type == "Root": 
                        if self.Content[Indexer].Botom < CurrentCenter: # the rule for roots is that if the bottom of the root is higher than the y center of the current character, then it is an exponent
                            SubZoneValuesLatex, SubZoneValuesStandard = self.Content[Indexer].PrintContentInOrder() # the root is wrapped by calling the function recursively

                            Exponents += SubZoneValuesLatex
                            ExponentsStandard += SubZoneValuesStandard # the output is added to the exponents list
                            Flag = True
                        else:
                            break

                if Flag:
                    if len(Exponents) > 2: # if there are more than two characters in the exponents list, then the list needs to be wrapped in brackets
                        Exponents.insert(1, "{")
                        Exponents.append("}")
                        ExponentsStandard.insert(1, "(")
                        ExponentsStandard.append(")")
                    Valueslatex += Exponents 
                    ValuesStandard += ExponentsStandard # the exponents list is added to the output
                    SkipUntil = Indexer + skip  # the skip until is set to the index of the last character that was an exponent, this is used to skip the exponents when looping through the characters
        Valueslatex.append(self.OutputEnd) 
        ValuesStandard.append(self.OutputEndStandard) # the end of the wrapper is added to the output
        #print(ValuesStandard)
        return Valueslatex, ValuesStandard # the output is returned
                        

                    

                


    

