""" Implementation of the Shape Discrimination task described in
    "Coleman - Evolving Neural Networks for Visual Processing" 
"""

import random

import numpy as np

### HELPER FUNCTION

def line(im, x0, y0, x1, y1):
    """ Bresenham """
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0  
        x1, y1 = y1, x1
        
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0
        
    if y0 < y1: 
        ystep = 1
    else:
        ystep = -1
            
    deltax = x1 - x0
    deltay = abs(y1 - y0)
    error = 0
    y = y0
        
    for x in range(x0, x1 + 1): # We add 1 to x1 so that the range includes x1
        if steep:
            im[y, x] = 1
        else:
            im[x, y] = 1
            
        error = error + deltay
        if (error << 1) >= deltax:
            y = y + ystep
            error = error - deltax


class ShapeDiscriminationTask(object):
    
    def __init__(self, setup, size=15, trials=200):
        """ Constructor """
        self.size = size
        self.trials = trials
        setup = setup.lower()
        
        if setup == 'scx':
            target = 'square'
            distractors = ['circle', 'x']
        else:
            raise Exception("Unknown Setup")
            
        self.target = self.makeshape(target, size//3)
        self.distractors = [self.makeshape(d, size//3) for d in distractors]
        
    def makeshape(self, shape, size=5):
        """ Create an image of the given shape.
        """
        im = np.zeros((size, size))
        xx, yy = np.mgrid[-1:1:size*1j, -1:1:size*1j]
        
        if shape == 'square':
            im[:,0] = 1;
            im[0,:] = 1;
            im[:,-1] = 1;
            im[-1,:] = 1;
            
        elif shape == 'circle':                
            d = np.sqrt(xx * xx + yy * yy)
            im[ np.logical_and(0.65 <= d, d <= 1.01) ] = 1
            
        elif shape == 'x':
            line(im, 0, 0, size-1, size-1)
            line(im, 0, size-1, size-1, 0)
         
        else:
            raise Exception("Shape Unknown.")  
        
        return im
        
    def evaluate(self, network):
        if not network.sandwich:
            raise Exception("Object Discrimination task should be performed by a sandwich net.")
        
        dist = 0.0
        for _ in xrange(self.trials):
            pattern = np.zeros((self.size, self.size))
            targetsize = self.target.shape[0]
            distractor = random.choice(self.distractors)
            distsize = distractor.shape[0]
            x, y = np.random.randint(self.size - targetsize, size=2)
        
            pattern[x:x+targetsize, y:y+targetsize] = self.target
            cx, cy = x + targetsize // 2, y + targetsize // 2
        
            for i in xrange(100):
                x, y = np.random.randint(self.size - distsize, size=2)
                if not np.any(pattern[x:x+distsize, y:y+distsize]):
                    pattern[x:x+distsize, y:y+distsize] = distractor
                    break
                if i == 99:
                    raise Exception("No position found")

            network.flush()
            output = network.feed(pattern, add_bias=False)
            mx = output.argmax()
            (x_, y_) = mx // self.size, mx % self.size
            # WSOSE = (1 - output[cx, cy]) ** 2
            dist += ((x_ - cx) ** 2) + ((y_ - cy) ** 2)
            
        dist = dist / self.trials
        score = 1. / (1. + dist)
        return {'fitness':score}
        
if __name__ == '__main__':
    a = ShapeDiscriminationTask('scx')
    a.evaluate(None)