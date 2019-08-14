import sys
import os
path_file = "./configure_files/history_path.info"
path_dics = {}
dic_notes = {}

def getConfig():
    config = "./configure_files/config.cfg"
    symbol_notes = "#"
    width = 0 
    height = 0 
    dic = {}
    global dic_notes
    notes = None
    with open(config) as f:
        for line in f:
            if line[0] == "#":
                notes = line.rstrip('\r\n').split("#")
            else:
                tmp = (line.rstrip('\r\n').split(":->"))
                if len(tmp) <2:
                    tmp.append("Undefined")
                dic.update({tmp[0]:tmp[1]})
                if notes is not None:
                    dic_notes[tmp[0]] = notes[1]
                notes = None
    return dic,dic_notes

def setConfig(dic,key,value):
    global dic_notes
    config = "./configure_files/config.cfg"
    dic[key] = value
    with open(config,'w') as f:
        for k,v in dic.items():
            if k in dic_notes:
                txt_notes = dic_notes[k]
                f.write("#"+txt_notes+"\n")
            f.write(k+":->"+v+"\n")
            
def getLabelDic():
    config = "./configure_files/label_dic.cfg"
    dic = {}
    with open(config) as f:
        for line in f:
            tmp = (line.rstrip('\r\n').split(":->"))
            if len(tmp) <2:
                tmp.append("Undefined")
            dic.update({tmp[0]:tmp[1]})
    return dic




def getLastDialogue():
    global path_file
    global path_dics
    with open(path_file,'r') as f:
        for line in f:
            tmp = (line.rstrip('\r\n').split(":->"))
            path_dics.update({tmp[0]:tmp[1]})
    return path_dics 


def setPath(keyword,value):
    global path_file
    global path_dics
    path_dics.update({keyword:value})
    with open(path_file,'w') as f:
        for k,p in path_dics.items():
            f.write(k+":->"+p+"\n")

def getParameters():
    config = "./parameters/parameters.dat"
    dic = {}
    with open(config) as f:
        for line in f:
            try:
                tmp = (line.rstrip('\r\n').split(":->"))
                dic.update({tmp[0]:tmp[1]})
            except:
                pass
    return dic
