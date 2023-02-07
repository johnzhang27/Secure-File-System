import sys
import os

class User:
    __username = ''
    __password = ''
    __group = -1

    def __init__(self, username, password, group):
        self.__username = username
        self.__password = password
        self.__group = group


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