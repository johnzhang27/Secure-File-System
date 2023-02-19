import sys
import os

class User:
    __username = ''
    __password = ''
    __group = -1
    __file_list = []
    __path_list = []
    __key_list = []
    __unique_key = ''

    def __init__(self, username = '', password = '', group = -1):
        self.__username = username
        self.__password = password
        self.__group = group
        self.__file_list = []
        self.__path_list = []
        self.__key_list = []


    def setUsername(self, username):
        self.__username = username

    def getUsername(self):
        return self.__username

    def setPassword(self, password):
        self.__password = password

    def getPassword(self):
        return self.__password

    def setGroup(self, group):
        self.__group = group

    def getGroup(self):
        return self.__group

    def getFilelist(self):
        return self.__file_list

    def setFilelist(self, file_list):
        self.__file_list = file_list

    def getPathlist(self):
        return self.__path_list
        
    def setPathlist(self, path_list):
        self.__path_list = path_list

    def getKeylist(self):
        return self.__key_list
        
    def setKeylist(self, key_list):
        self.__key_list = key_list