import tensorflow as tf
import numpy as np
import utils.pure_data as pd
import time

from models.dance_rnn_model import RNNModel
from models.cae_l_high import CAEModel
from models.actions_model import ActionsModel
from utils.config import process_config
from utils.utils import get_args
import matplotlib.pyplot as plt
import cv2

def load_models(c_c, r_c, a_c):
    # Load the models on separate sessions
    c_g = tf.Graph()
    with c_g.as_default():
        cae = CAEModel(c_c)

    c_s = tf.Session(graph=c_g)
    with c_s.as_default():
        with c_g.as_default():
            cae.load(c_s)

    a_g = tf.Graph()
    with a_g.as_default():
        action = ActionsModel(a_c)

    a_s = tf.Session(graph=a_g)
    with a_s.as_default():
        with c_g.as_default():
            action.load(a_s)

    r_g = tf.Graph()
    with r_g.as_default():
        rnn = RNNModel(r_c)

    r_s = tf.Session(graph=r_g)
    with r_s.as_default():
        with r_g.as_default():
            rnn.load(r_s)

    return cae, c_s, rnn, r_s, action, a_s

def dream(cae, c_s, rnn, r_s, action, a_s, pred=np.zeros((1,1,128)), state=np.zeros((2,2,1,512)), length=300, randomize=True):
    img = None
    prediction = np.copy(pred)
    init_state = np.copy(state)
    randomness = prediction
    influence = False
    influence_duration = 20
    influence_count = 0
    print("Dreaming")
    while True:
        rythm = np.random.randint(length-1)+1
        prev_pred = np.random.rand(1,1,128)
        for i in range(length):
            prediction, init_state = r_s.run([rnn.prediction, rnn.state], feed_dict={rnn.x: prediction, rnn.init_state: init_state})
            # init_state = init_state + np.random.rand(2,2,1,256)*0.2
            # encoded = prediction.squeeze().reshape((1,2,2,4))
            encoded = prediction.reshape((1,1,1,-1))
            decoded = c_s.run(cae.decoded, feed_dict={cae.encoded: encoded})
            encoded = encoded.reshape((8,4,4))
            encoded = cv2.resize(encoded/encoded.max(), (500,500))
            decoded = cv2.resize(decoded.squeeze()/decoded.max(), (500,500))
            decoded = np.stack((decoded,)*3)
            decoded = np.vstack((decoded, np.ones((1,500,500))))
            decoded = np.rollaxis(decoded, 0, 3)
            show_img = np.concatenate((encoded, decoded), axis=1)
            actions = a_s.run(action.prediction, feed_dict={action.x: np.asarray(init_state).reshape((1,-1))})
            cv2.imshow('dream', show_img)
            cv2.waitKey(40)
            msg = ' '.join(map(str, actions.squeeze())) + ';'
            pd.send2Pd(msg)
            if np.abs(np.sum(prev_pred - prediction)) < 0.01:
                # if the dream has become static then gie it a little push
                print("adding external influence")
                randomness = (np.random.rand(1,1,128) - 0.5)*2
                influence = True
            if influence and influence_count < influence_duration:
                prediction += randomness/influence_duration
                influence_count += 1
            else:
                influence_count = 0
                influence = False
            prev_pred = prediction

        prediction = np.random.rand(1,1,128)*0.3
        init_state = np.random.rand(2,2,1,512)


def main():
    try:
        args = get_args()
        c_c = process_config(args.caeconfig)
        r_c = process_config(args.rnnconfig)
        a_c = process_config(args.actionsconfig)
        length = int(args.length)
    except:
        print("Missing or invalid arguments")
        exit(0)

    cae, c_s, rnn, r_s, action, a_s = load_models(c_c, r_c, a_c)
    pred = np.random.rand(1,1,128)*0.7
    state = np.random.rand(2,2,1,512)*5
    dream(cae,c_s,rnn,r_s,action,a_s,pred,state,length)

if __name__ == '__main__':
    main()