import numpy as np

class RedNeuronal:

    def __init__(self):
        np.random.seed(0)

        self.W1 = np.random.randn(3, 4)
        self.b1 = np.zeros((1, 4))

        self.W2 = np.random.randn(4, 1)
        self.b2 = np.zeros((1, 1))

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoid_deriv(self, x):
        return self.sigmoid(x) * (1 - self.sigmoid(x))

    def relu(self, x):
        return np.maximum(0, x)

    def relu_deriv(self, x):
        return (x > 0).astype(float)

    def entrenar(self, historial, epochs=5000, lr=0.1):

        X = []
        y = []

        # Crear dataset tipo ventana deslizante
        for i in range(len(historial) - 3):
            X.append(historial[i:i+3])
            y.append([historial[i+3]])

        if len(X) == 0:
            return  # no hay suficientes datos

        X = np.array(X)
        y = np.array(y)

        for _ in range(epochs):

            Z1 = np.dot(X, self.W1) + self.b1
            A1 = self.relu(Z1)

            Z2 = np.dot(A1, self.W2) + self.b2
            A2 = self.sigmoid(Z2)

            error = y - A2

            dA2 = error * self.sigmoid_deriv(Z2)

            dW2 = np.dot(A1.T, dA2)
            db2 = np.sum(dA2, axis=0, keepdims=True)

            dA1 = np.dot(dA2, self.W2.T) * self.relu_deriv(Z1)

            dW1 = np.dot(X.T, dA1)
            db1 = np.sum(dA1, axis=0, keepdims=True)

            self.W2 += lr * dW2
            self.b2 += lr * db2

            self.W1 += lr * dW1
            self.b1 += lr * db1

    def predecir(self, ultimos_dias):

        X = np.array([ultimos_dias])

        Z1 = np.dot(X, self.W1) + self.b1
        A1 = self.relu(Z1)

        Z2 = np.dot(A1, self.W2) + self.b2
        A2 = self.sigmoid(Z2)

        return A2[0][0]