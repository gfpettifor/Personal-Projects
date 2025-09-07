#!/usr/bin/env python
# coding: utf-8

# # Unit Converter with UI

# This unit converter uses the same linear array approach with the back end code as the other unit converter in this repository, but it has a UI designed to prevent the user from inputting unaccaptable or incompatible units. It also prevents the user from selecting the same input and output unit. With the drop down menus, you first choose the unit type (weight, distance or volume) which changes the other menu options, and then you can choose the original unit and the desired unit from two more drop down menus. If in one menu, you choose the unit the other menu already has selected, the other menu's unit will be changed.

# #### Importing necessary libraries

# Since math, tkinter and logging all come installed with python, they will deffinitely be installed locally. However, numpy and matplotlib do not come downloaded as standard so if they cant be imported, the program asks the user to download them. The program could run "pip install numpy matplotlib" but this is unwise as it can cause issue depending on where the program is run.

# In[1]:


try:
    import numpy as np
    import matplotlib.pyplot as plt
except ImportError as e:
    print("Missing a required package. Please run:")
    print("    pip install numpy matplotlib")
    raise
import math
import tkinter as tk
import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logging.getLogger().setLevel(logging.INFO)


# #### Deffining the units

# Here are the units available, along with their conversion rates.

# In[2]:


#defining units and their conversion rates
Weights = ["tonne","kg","g","st","lb","oz"]
Distances = ["km","m","cm","mm","mi","yd","ft","in"]
Volumes = ["m3","l","cc","ml","yd3","ft3","in3","gal","qt","pt","c","floz","tbsp","tsp"]
Units = [Weights,Distances,Volumes]
Unittypes = ["Weights","Distances","Volumes"]
Weightsconv = [1000.0,1000.0,0.0001574730901,14.0,16.0]
Distancesconv = [1000.0,100.0,10.0,0.0000006213711922,1760.0,3.0,12.0]
Volumesconv = [1000.0,1000.0,1.0,0.000001307950619,27.0,1728.0,0.004329004329,4.0,2.0,2.0,8.0,2.0,3.0]
Conversions = [Weightsconv,Distancesconv,Volumesconv]


# #### Defining reusable functions I have developed previously

# In[3]:


#defining a function that will calculate the significant figures of a number given as a string
def sigfigs_str(string):
    if "." in string:
        digits = string.replace(".", "").lstrip("0")
    else:
        digits = string.lstrip("0")
    logging.debug(f"sigfigs_str called with string = '{string}' digits = '{digits}'")
    if not digits:
        return 0
    return len(digits)

#defining a function that will round based on significant figures rather than decimals
def round_sf(x, sf):
    
    if x == 0:
        return 0
    else:
        rounded = round(x, sf - int(math.floor(math.log10(abs(x)))+1))
        logging.debug(f"round_sf called with x = '{x}' sf = '{sf}' giving rounded = '{rounded}'")
        return rounded

#defining a float conversion function to take string input and return a float or an error
def floatconv(instr):
    decimal_seen = False
    out = 0.0
    for i, char in enumerate(instr):
        if char.isdigit():
            continue
        elif char == '.':
            if decimal_seen:
                raise ValueError(f"Error: too many decimals in input '{instr}'")
            decimal_seen = True
        else:
            raise ValueError(f"Error: non-numerical character '{char}' in input '{instr}'")
    logging.debug(f"floatconv called with instr = '{instr}' giving out = '{float(instr)}'")
    return float(instr)

#defining a find function to find a target in an array that may have arrays in it
def find(array, target, path=None, top=True):
    if path is None:
        path = []
    for i, item in enumerate(array):
        if isinstance(item, list):
            result = find(item, target, path + [i], top=False)
            if result is not None:
                return result
        elif item == target:
            path += [i]
            logging.debug(f"find called with array = '{array}' target = '{target}' giving path = '{path}'")
            return path
    if top:
        raise IndexError(f"Error: input unit not found array = '{array}' target = '{target}'")
    return None


# #### Defining the unit conversion function

# This function actually computes the conversion of the given value from the original unit to the desired unit. It calls all of the functions in the previous cell appropriately and returns the output value along with the significant figures it is rounded to, to the UI.

# In[4]:


#defining a convert function to convert the input value from the input units to the output units
def convert(invalstr,inunit,outunit):

    #defining the internal calculation function
    def cal(inval,inunitpos,outunitpos):
        fac = 1.0
        x = 0
        while x < abs(outunitpos[1]-inunitpos[1]):
            array = Conversions[inunitpos[0]]
            if inunitpos[1]<outunitpos[1]:
                fac = fac*array[inunitpos[1]+x]
            elif inunitpos[1]>outunitpos[1]:
                fac = fac/array[outunitpos[1]+x]
            x = x + 1
        outval = inval * fac
        logging.debug(f"cal called with inval = '{inval}' inunitpos = '{inunitpos}' outunitpos = '{outunitpos}' giving outval = '{outval}'")
        return outval
    
    #processing inputs
    inval = floatconv(invalstr)
    sigfig = sigfigs_str(invalstr)
    #allowing minimum sigfig of 3 even if fewer were given
    if sigfig<3:
        sigfig = 3
    #finding units
    inunitpos = find(Units,inunit)
    outunitpos = find(Units,outunit)

    #comparing units for compatibility
    if inunitpos[0] != outunitpos[0]:
        raise KeyError(f"Error: incompatible units '{inunit}' and '{outunit}'")
    #avoiding processing if input unit and output unit are the same
    elif inunitpos == outunitpos:
        print("You have entered the same units.")
        outval = inval
    #processing everything else
    else:
        outval = round_sf(cal(inval,inunitpos,outunitpos),sigfig)

    #giving the final output
    return outval,sigfig


# #### Making a UI

# This UI has three drop down menus, for the unit type, the original unit and the desired unit. It also has an entry box for the user to enter the original value, and a button to calculate the output value. It finally has appropriate labels denoting everything in an easily interpretable way. This was my first time using Tkinter so it may not be as efficient as possible but I'm sure my skills will improve as I use it more. Towards the bottom of the cell is a commented line that can be un-commented to run debugging.

# In[7]:


root = tk.Tk()
root.title("Unit Converter")
#root.geometry("400x300")
root.resizable(False, False)

#defining a function that updates the assumed value and optional values in each menu
def updateoptions(menu,string,options):
    logging.debug(f"updateoptions called")
    menu = menu["menu"]
    menu.delete(0, "end")
    for option in options:
        menu.add_command(label=option, command=tk._setit(string, option))
    logging.debug(f"updateoptions called and completed")

#defining a function that changes the unit menus when the unit type menu is changed
def typeonselection(*args):
    logging.debug(f"typeonselection called")
    #using the find function to determine the position of the selected unit type in the unittype array
    unittypepos = find(Unittypes,unittypestr.get())
    #changing the inunit menu
    inoptions = Units[unittypepos[0]].copy()
    logging.debug(f"inoptions = '{inoptions}'")
    updateoptions(inmenu,inunitstr,inoptions)
    inunitstr.set(inoptions[0])
    #changing the outunit menu
    outoptions = Units[unittypepos[0]].copy()
    logging.debug(f"outoptions = '{outoptions}'")
    updateoptions(outmenu,outunitstr,outoptions)
    outunitstr.set(outoptions[1])
    logging.debug(f"typeonselection called and completed")

#defining a function that runs when the in-menu has an option selected
def inmenuonselection(*args):
    logging.debug(f"inmenuonselection called")
    #using an if statement to check if the in-menu and out-menu values are the same
    if inunitstr.get() == outunitstr.get():
        unittypepos = find(Unittypes,unittypestr.get())
        inoptions = Units[unittypepos[0]].copy()
        outoptions = Units[unittypepos[0]].copy()
        #using an if statement to make sure when we change the out-menu value, we dont change it to the same as the in-menu value
        if find(inoptions,inunitstr.get())[0] == 0:
            logging.debug(f"menu options identical")
            outunitstr.set(outoptions[1])
        else:
            outunitstr.set(outoptions[0])
        logging.debug(f"inmenuonselection called and changes made giving outunitstr = '{outunitstr.get()}'")
    else:
        logging.debug(f"inmenuonselection called and completed without changes")

#defining a function that runs when the out-menu has an option selected
def outmenuonselection(*args):
    logging.debug(f"outmenuonselection called")
    #using an if statement to check if the in-menu and out-menu values are the same
    if inunitstr.get() == outunitstr.get():
        unittypepos = find(Unittypes,unittypestr.get())
        inoptions = Units[unittypepos[0]].copy()
        outoptions = Units[unittypepos[0]].copy()
        #using an if statement to make sure when we change the in-menu value, we dont change it to the same as the out-menu value
        if find(outoptions,outunitstr.get())[0] == 0:
            logging.debug(f"menu options identical")
            inunitstr.set(inoptions[1])
        else:
            inunitstr.set(inoptions[0])
        logging.debug(f"outmenuonselection called and changes made giving inunitstr = '{inunitstr.get()}'")
    else:
        logging.debug(f"outmenuonselection called and completed without changes")
    
#using a function that is called when the calculate button is pressed that takes the value given and the units given and passes them to the convert function
def calculate():
    invalstr = invalbox.get()
    inunit = inunitstr.get()
    outunit = outunitstr.get()
    newtxt,sigfig = convert(invalstr,inunit,outunit)
    outlabel.config(text=newtxt)
    sigfigval.config(text=sigfig)

#configuring the unit type selection
unittypelabel = tk.Label(root, text="Unit type:")
unittypelabel.grid(row=0, column=0,)
unittypestr = tk.StringVar(value="Distances")
unittypestr.trace_add("write", typeonselection)
unittypemenu = tk.OptionMenu(root, unittypestr, *Unittypes)
unittypemenu.grid(row=0, column=1)

#configuring the entry box for inval
invallabel = tk.Label(root, text="Value:")
invallabel.grid(row=1, column=0)
invalbox = tk.Entry(root)
invalbox.grid(row=1, column=1)

#configuring the menu for the inunit
inmenulabel = tk.Label(root, text="From unit:")
inmenulabel.grid(row=2, column=0)
inunitstr = tk.StringVar(value="m")
inunitstr.trace_add("write", inmenuonselection)
inoptions = Distances.copy()
inmenu = tk.OptionMenu(root, inunitstr, *inoptions)
inmenu.grid(row=2, column=1)

#configuring the menu for the outunit
outmenulabel = tk.Label(root, text="To unit:")
outmenulabel.grid(row=3, column=0)
outunitstr = tk.StringVar(value="ft")
outunitstr.trace_add("write", outmenuonselection)
outoptions = Distances.copy()
outmenu = tk.OptionMenu(root, outunitstr, *outoptions)
outmenu.grid(row=3, column=1)

#configuring the calculate button and the label that will show the converted value
calcbutton = tk.Button(root, text="Calculate",command=calculate)
calcbutton.grid(row=4,column=0)
outlabel = tk.Label(root, text="")
outlabel.grid(row=4,column=1)

#configuring the labels to denote the significant figures the output value was rounded to
sigfigtxt = tk.Label(root, text="Significant figures round to:")
sigfigtxt.grid(row=5,column=0)
sigfigval = tk.Label(root, text="")
sigfigval.grid(row=5,column=1)

#adding padding to each widget
for widget in (unittypelabel,unittypemenu,invallabel,invalbox,inmenulabel,inmenu,outmenulabel,outmenu,calcbutton,outlabel,sigfigtxt,sigfigval):
    widget.grid_configure(padx=20, pady=20)

#logging.getLogger().setLevel(logging.DEBUG)
root.mainloop()

