import numpy as np
import pprint as pp
import math
from sklearn.utils import shuffle

def sgm(x, der=False):
    """Logistic sigmoid function.
    Use der=True for the derivative."""
    if not der:
        return 1 / (1 + np.exp(-x))
    else:
        simple = 1 / (1 + np.exp(-x))
        return simple * (1 - simple)

class NeuralNetwork:
    """Neural Network class.

    Args:
        shape (list): shape of the network. First element is the input layer, last element
        is the output layer.
        activation (optional): pass the activation function. Defaults to sigmoid. 
        """

    # outputs: output of the layers (before the sigmoid)
    # activations: outputs after the sigmoid
    def _init_weights(self):
        self.weights = [np.random.randn(j , i) for i, j in zip(self.shape[:-1], self.shape[1:])]

    def _init_biases(self):
        self.biases = [np.random.randn(i, 1) for i in self.shape[1:]]
        
    def _init_activations(self):
        self.activations = []

    def _init_outputs(self):
        self.outputs = []

    def _init_deltas(self):
        self.deltas = []

    def __init__(self, shape, activation=sgm):
        self.shape = shape
        self.activation = activation
        self._init_weights()
        self._init_biases()
        self._init_activations()
        self._init_outputs()

    def feed_forward(self, data):
        """Given the input and, return the predicted value according to the current weights."""
        result = data
        self.activations.append(data)
        self.outputs.append(data)

        for w, b  in zip(self.weights, self.biases):
            result = np.dot(w, result) + b
            self.outputs.append(result)
            result = self.activation(result)
            self.activations.append(result)

        # the last level is the activated output
        return result

    def calculate_deltas(self, data, target):
        """ Given the input and the output (typically from a batch),
        it calculates the corresponding deltas.
        """
        # delta for the back propagation
        self._init_deltas()
        self.feed_forward(data)

        # calculate delta for the output level
        delta = np.multiply( \
                    self.activations[-1] - target, \
                    self.activation(self.outputs[-1], der=True) \
                    )
        self.deltas.append(delta)

        # since it's back propagation we start from the end
        steps = len(self.weights) - 1
        for l in range(steps, 0, -1):
            delta = np.multiply(
                        np.dot(
                            self.weights[l].T, 
                            self.deltas[steps-l]
                            ),
                        self.activation(self.outputs[l], der=True)
                        )
            self.deltas.append(delta)

        # delta[i] contains the delta for layer i+1
        self.deltas.reverse()

    def update_weights(self, total, eta):
        """Use backpropagation to update weights"""
        self.weights =  [w - (eta/total) * np.dot(d, a.T) for w, d, a in zip(self.weights, self.deltas, self.activations)]

    def update_biases(self, total, eta):
        """Use backpropagation to update the biases"""
        self.biases = [b - (eta/total)* d.sum(axis=1)[:, None] for b, d  in zip(self.biases, self.deltas)]

    def cost(self, predicted, target):
        """Calculate the cost function using the current weights and biases"""
        return np.linalg.norm(predicted - target) ** 2

    def SGD(self, data, target, batch_size, epochs=20, eta=.3, print_cost=False):
        # maybe remove this in the future?
        if isinstance(data, list):
            data = np.array(data)
        if isinstance(target, list):
            target = np.array(target)

        self.data = data.T
        self.target = target.T

        # sanity / shape checks that input / output respect the desired dimensions
        if self.data.shape[0] != self.shape[0]:
            print('Input and shape of the network not compatible')
            exit()
        if self.target.shape[0] != self.shape[-1]:
            print('Output and shape of the network not compatible')
            exit()

        # normalize inputs?
        #self.input = (np.array(input) / np.amax(input, axis = 0)).T
        #self.target = (np.array(target) / np.amax(target)).T
        
        # number of total examples
        total = self.data.shape[1]
        diff = total % batch_size
        # we discard the last examples for now
        if diff != 0:
            self.data = self.data[: total - diff]
            self.target = self.target[: total - diff]
            total = self.data.shape[1]
        
        for epoch in range(epochs):
            # for each epoch, we reshuffle the data and train the network
            print("***** Starting epoch:", epoch)
            # create a list of batches (input and target)
            self.data, self.target = shuffle(self.data, self.target)
            batches_input = [self.data[:, k:k + batch_size] for k in range(0, total, batch_size)]
            batches_target = [self.target[:, k:k + batch_size] for k in range(0, total, batch_size)]
            for batch_input, batch_target in zip(batches_input, batches_target):
                # reset the status of the internal variables each time
                self._init_outputs()
                self._init_activations()
                
                # output values corresponding to the inputs
                self.feed_forward(batch_input)
                
                # do backpropagation
                # calculate delta for all levels
                self.calculate_deltas(batch_input, batch_target)
                # update internal variables
                self.update_weights(batch_size, eta)
                self.update_biases(batch_size, eta)
            
            if (print_cost):
                print("Error is ",
                    self.cost(self.feed_forward(self.data), self.target)
                    )


    def predict(self, data):
        if isinstance(data, list):
            data = np.array(data).T
        return self.feed_forward(data)


if __name__ == '__main__':

    X = []
    y = []
    X_test = []
    y_test = []
    m = 10000

    # sin
    # for i in range(10):
    #     d = (2 * math.pi)/10
    #     X.append([i*d])
    #     y.append([math.sin(i*d)])

    # x^2
    
    # for i in range(m):
    #     X.append([i/m])
    #     y.append([(i/m) ** 2])
    #     X_test.append([(i+1)/m])
    #     y_test.append([((i+1)/m) ** 2])

    # for xx in np.linspace(-1, 1, 1000):
    #     for yy in np.linspace(-1, 1, 1000):
            
    #         X.append([xx, yy])
    #         y.append([np.sin(xx - yy) + np.cos(xx + yy)])

    for xx in np.linspace(-10, 10, 10000):
        X.append([xx])
        y.append([xx ** 2])
    #NN = NeuralNetwork([4, 6,7,10,3, 2])
    NN = NeuralNetwork([1, 2, 1])


    print("starting sgd")
    NN.SGD(X,y,100, epochs=10, print_cost=True)
    print(NN.predict([[0], [1], [-11]]))