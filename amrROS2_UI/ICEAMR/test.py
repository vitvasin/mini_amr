import requests
import json
from collections import namedtuple

datas =[{ 'Name':"A", 'BoxNumber':1},
       { 'Name':"B", 'BoxNumber':1},
       { 'Name':"C", 'BoxNumber':1},
       { 'Name':"D", 'BoxNumber':1},
       { 'Name':"E", 'BoxNumber':2},
       { 'Name':"F", 'BoxNumber':3},
       { 'Name':"G", 'BoxNumber':2},
       { 'Name':"H", 'BoxNumber':4},       
       ]

def set_door_color(boxNumber):
    color='black'
    if boxNumber == 1:
        color = 'background-color: rgb(143, 240, 164);'
    elif boxNumber == 2:
        color = 'background-color: rgb(153, 193, 241);'
    elif boxNumber == 3:
        color = 'background-color: rgb(249, 240, 107);'
    elif boxNumber == 4:
        color = 'background-color: rgb(246, 97, 81);'
    elif boxNumber == 5:
        color = 'background-color: rgb(220, 138, 221);'
    elif boxNumber == 6:
        color = 'background-color: rgb(255, 190, 111);'
    elif boxNumber == 7:
        color = 'background-color: rgb(242, 37, 141);'        
    elif boxNumber == 8:
        color = 'background-color: rgb(222, 221, 218);'
    return color
        
        
def door_clicked(name):
    currentBox = 0
    for data in datas:
        if data['Name'] == name:
            # print(data['BoxNumber'])
            currentBox = data['BoxNumber']
            
    for data in datas:
        if data['BoxNumber'] == currentBox:
            print('Open door ', data['Name'])
            
    print()
        
def get_num_box():
    numBoxValue = 0
    for data in datas:
        if data['BoxNumber'] > numBoxValue:
            numBoxValue = data['BoxNumber']
    print('numBoxValue = ',numBoxValue)
    
    print(len(datas)/len(datas[0]))
    

# print(datas[0])
# print(set_door_color(6))
# door_clicked('A')
# door_clicked('B')
# door_clicked('C')
# door_clicked('D')
# door_clicked('E')
# door_clicked('F')
# door_clicked('G')
# door_clicked('H')

get_num_box()
