class Habito:
    def __init__(self, nombre):
        self.nombre = nombre
        self.historial = []

    def agregar_registro(self, cumplido):
        self.historial.append(1 if cumplido else 0)

    def racha_exito(self):
        racha = 0
        for h in reversed(self.historial):
            if h == 1:
                racha += 1
            else:
                break
        return racha

    def racha_fallo(self):
        racha = 0
        for h in reversed(self.historial):
            if h == 0:
                racha += 1
            else:
                break
        return racha