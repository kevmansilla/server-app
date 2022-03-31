# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

from os import listdir
from os.path import getsize
import socket
from constants import *
from base64 import b64encode

class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        self.clientsocket = socket
        self.directory = directory
        self.status = 0
        self.closed = False

    def handle(self):
            """
            Atiende eventos de la conexión hasta que termina.
            """
            while not self.closed:
                message = self.clientsocket.recv(1024).decode() 
                if message != '':

                    print('Mensaje obtenido:', message)
                    tokens = message.split()
                    
                    if tokens[0] == 'get_file_listing':
                        response = get_file_listing(self.directory).encode()
                        self.clientsocket.send(response)
                    
                    elif tokens[0] == 'get_metadata':
                        name = tokens[1]
                        response = get_metadata(self.directory, name).encode()
                        self.clientsocket.send(response)

                    elif tokens[0] == 'get_slice':
                        response = get_slice(self.directory, tokens[1], tokens[2], tokens[3]).encode()
                        self.clientsocket.send(response)
                            
                    elif tokens[0] == 'quit':
                        header = str(CODE_OK) + ' ' + error_messages[CODE_OK] + EOL
                        self.clientsocket.send(header.encode())
                        self.clientsocket.close()
                        self.closed = True
                    else:
                        print('Comando invalido, intente nuevamente')

def get_file_listing(directory):
    # Obtenemos los archivos del directorio testdata:
    files = listdir(directory)

    # Armamos la cabecera del mensaje:
    header = str(CODE_OK) + ' ' + error_messages[CODE_OK] + EOL

    # Armamos el mensaje de respuesta:
    response = ''
    for file in files:
        response += file + EOL
    response += EOL

    return(header + response)

def get_metadata(directory, filename):
    # Obtenemos el tamaño del archivo:
    path = directory + '/' + filename
    size = getsize(path)

    # Armamos la cabecera del mensaje:
    header = str(CODE_OK) + ' ' + error_messages[CODE_OK] + EOL

    # Armamos el mensaje de respuesta:
    response = header + str(size) + EOL

    return(header + response)

def get_slice(directory, filename, offset, size):
    # Creamos la ruta del archivo:
    path = directory +  '/' + filename

    # Abrimos el archivo:
    file = open(path, 'r')
    
    # Apuntamos el puntero de lectura al offset:
    file.seek(int(offset))

    #Leemos size-bytes del archivo:
    content = file.read(int(size)).encode()

    # Lo codificamoos:
    cont_decode = b64encode(content).decode()
    
    # Armamos la cabecera del mensaje:
    header = str(CODE_OK) + ' ' + error_messages[CODE_OK] + EOL

    # Armamos el mensaje de respuesta:
    response = cont_decode + EOL

    return header + response
