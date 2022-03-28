# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

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
        self.closed = False

    def handle(self):
            """
            Atiende eventos de la conexión hasta que termina.
            """

            while not self.closed:

                message = self.clientsocket.recv(1024).decode() 

                if message != '':
                    print('Mensaje obtenido:', message)

                    if message.startswith('get_file_listing'):
                        print('Se ejecutara: get_file_listing')

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