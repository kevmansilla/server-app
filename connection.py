# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

from os import *
from os.path import *
import socket
from telnetlib import STATUS
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

                    if parser_get_file_listing(message):
                        response = get_file_listing(self.directory).encode()
                        self.clientsocket.send(response)

                    elif message.startswith('get_metadata'):
                        print('Se ejecutara: get_metadata')

                    elif message.startswith('get_slice'):
                        print('Se ejecutara: get_slice')
                    
                    elif message.startswith('quit'):
                        print('Se ejecutara: quit')
                        self.closed = True
                    
                    else:
                        print('Comando invalido: Se cerrara la conexión.')
                        self.closed = True

def parser_get_file_listing(message):
    # Dividimos el mensaje en sus palabras.
    tokens = message.split()

    # El comando es correcto si es get_file_listing y no tiene argumentos:
    return (len(tokens) == 1) and (tokens[0] == 'get_file_listing')

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
