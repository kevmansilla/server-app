# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

from os import listdir
from os.path import getsize, exists
import queue
import socket
from constants import *
from base64 import b64encode

BUFFER_SIZE = 4096

class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        self.clientsocket = socket
        self.directory = directory
        self.status = CODE_OK
        self.closed = False

    def quit(self):
        response = get_response_message(CODE_OK, '')
        self.clientsocket.send(response)
        self.closed = True

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """

        # Inicializamos la queue de eventos:
        events_queue = ''
        while not self.closed:
                            
            message = self.clientsocket.recv(1024).decode()
            
            if message == '':
                # No se recibieron datos.
                self.closed = True
            else:
                # Añadimos el mensaje a la cola de eventos:
                events_queue += message

            # Si EOL no esta in la cola de eventos significa que no se ha terminado de recibir el comando.
            # Entonces esperamos a que se termine de formar el comando.
            if not (EOL in events_queue):
                continue

            # Una vez que se recibieron comandos completos, tomamos el primer comando de la cola y lo sacamos:
            simple_command, events_queue = events_queue.split(EOL, 1)

            # Comprobamos que el comando este bien formado. Caso contrario envamos mensaje de error y cerramos conexión:
            if '\n' in simple_command:
                self.status = BAD_EOL
                response = get_response_message(BAD_EOL, '')
                self.clientsocket.send(response)
                break

            # Dividimos el comando en sus argumentos:    
            tokens = simple_command.split()

            # El primer elemento de tokens es el comando, los demas elementos son los argumentos:
            if tokens[0] == 'get_file_listing':
                body = ''
                if len(tokens) != 1:
                    self.status = INVALID_ARGUMENTS
                body = get_file_listing(self.directory)
                response = get_response_message(self.status, body)
                self.clientsocket.send(response)
            
            elif tokens[0] == 'get_metadata':
                body = ''                          
                if len(tokens) != 2:
                    self.status = INVALID_ARGUMENTS
                else:
                    filename = tokens[1]
                    path = self.directory + '/' + filename
                    if not exists(path) or len(filename) > 80:
                        self.status = FILE_NOT_FOUND
                    else:
                        body = get_metadata(path)
                response = get_response_message(self.status, body)
                self.clientsocket.send(response)

            elif tokens[0] == 'get_slice':
                body = ''                          
                if len(tokens) != 4:
                    self.status = INVALID_ARGUMENTS
                else:
                    filename = tokens[1]
                    offset = tokens[2]
                    size = tokens[3]
                    if not(offset.isnumeric() and size.isnumeric()):
                        self.status = INVALID_ARGUMENTS
                    else:
                        path = self.directory + '/' + filename
                        if not exists(path) or len(filename) > 80:
                            self.status = FILE_NOT_FOUND
                        else:
                            body = get_slice(self.directory, filename, offset, size)
                response = get_response_message(self.status, body)
                self.clientsocket.send(response)
                        
            elif tokens[0] == 'quit':
                if len(tokens) != 1:
                    self.status = INVALID_ARGUMENTS
                    response = get_response_message(self.status, '')
                    self.clientsocket.send(response)
                else:
                    self.quit()
            else:
                self.status = INVALID_COMMAND
                response = get_response_message(self.status, '')
                self.clientsocket.send(response)
        
        # Si la conexión esta cerrada, cerramos el socket.
        self.clientsocket.close()

def get_file_listing(directory):
    files = listdir(directory)
    response = ''
    for file in files:
        response += file + EOL
    return response

def get_metadata(filename):
    size = getsize(filename)
    response = str(size)
    return response

def get_slice(directory, filename, offset, size):
    path = directory +  '/' + filename
    file = open(path, 'r')
    file.seek(int(offset))
    content = file.read(int(size)).encode()
    file.close()
    cont_decode = b64encode(content).decode()
    return cont_decode

def get_response_message(code_error, message):
    """
    Se encarga de formar el encabezado y concatenarlo 
    con el mensaje de respuesta.
    """
    header = str(code_error) + ' ' + error_messages[code_error] + EOL
    response = header
    if code_error == CODE_OK:
        body = message + EOL
        response += body
        
    return response.encode()

