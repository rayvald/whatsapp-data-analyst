import pandas as pd
import re

class ChatProcessor:

    def __init__(self):
        self.df = self.procesar_chat()

    def starWithDateAndTime(self, s):
        patron = '^\[([0-9]{1,2}\/[0-9]{1,2}\/[0-9]{2}), ([0-9]{2}:[0-9]{2}:[0-9]{2})\] '
        result = re.match(patron, s)
        if result:
            return True
        else:
            return False


    def findMembers(self, s):
        patterns = [
            '([\w]+):',  # Nombre
            '([\w]+[\s]+[\(]+[\w]+[\)]+):',  # Nombre (Apodo)
            '([\w]+[\s]+[\w]+):',  # Nombre + Apellido
            '([\w]+[\s]+[\w]+[\s]+[\w]+):',  # Nombre 1 + Nombre 2 + Apellido
            '([+]\d{2} \d{3} \d{3} \d{4}):',  # Número de teléfono (Peru)
            '([\w]+[\s])[\u263a-\U0001f999]+:',  # Nombre + Emoji
        ]

        pattern = '^' + '|'.join(patterns)
        result = re.match(pattern, s)
        if result:
            return True
        else:
            return False


    def GetParts(self, linea):
        # Ejemplo: '21/2/2021 11:27 a. m. - Sandro: Todos debemos aprender a analizar datos'
        splitLinea = linea.split(']', 1)
        fechaHora = splitLinea[0] + ']'  # '21/2/2021 11:27 a. m.'
        splitFechaHora = fechaHora.split(', ')
        fecha = splitFechaHora[0][1:]  # '21/2/2021'
        hora = ' '.join(splitFechaHora[1:])[:-1]  # '11:27 a. m.'
        mensaje = splitLinea[1].strip()  # 'Sandro: Todos debemos aprender a analizar datos'
        if self.findMembers(mensaje):
            splitMensaje = mensaje.split(': ')
            miembro = splitMensaje[0]  # 'Sandro'
            mensaje = ' '.join(splitMensaje[1:])  # 'Todos debemos aprender a analizar datos'
        else:
            miembro = None
        return fecha, hora, miembro, mensaje

    def procesar_chat(self):

        chatRoute = '/Users/raynier/Documents/data-analyst/data-analyst-python/whatsapp/chat.txt'
        chatList = []

        with open(chatRoute, encoding="utf-8") as fp:
            fp.readline()  # Eliminar primera fila relacionada al cifrado de extremo a extremo
            VerificarMensaje = []  # Lista para verificar que no existan mensajes vacíos
            Fecha, Hora, Miembro = None, None, None
            while True:
                linea = fp.readline()
                if not linea:
                    break
                linea = linea.strip()
                if self.starWithDateAndTime(linea):  # Si cada línea del txt coincide con el patrón fecha y hora
                    if len(VerificarMensaje) > 0:
                        # Añadir un elemento lista que contendrá los datos a la lista 'DatosLista'
                        chatList.append([Fecha, Hora, Miembro, ' '.join(VerificarMensaje)])
                    VerificarMensaje.clear()
                    Fecha, Hora, Miembro, Mensaje = self.GetParts(linea)  # Obtener datos de cada línea del txt
                    VerificarMensaje.append(Mensaje)
                else:
                    VerificarMensaje.append(linea)

            # Convertir la lista con los datos a dataframe
        df = pd.DataFrame(chatList, columns=['Fecha', 'Hora', 'Miembro', 'Mensaje'])

        # Cambiar la columna Fecha a formato datetime
        df['Fecha'] = pd.to_datetime(df['Fecha'], format="%d/%m/%y")

        # Eliminar los posibles campos vacíos del dataframe
        # y lo que no son mensajes como cambiar el asunto del grupo o agregar a alguien
        df = df.dropna()

        # Rester el índice
        # df.reset_index(drop=True, inplace=True)
        # print(df)
        return df

procesador = ChatProcessor()

