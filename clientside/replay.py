import pure_data as pd
import numpy as np
import matplotlib.pyplot as plt

def replay_data(video,actions):
    img = None
    video = np.rollaxis(video[:],1,4)
    for i in range(video.shape[0]):
        frame = video[i]
        if img is None:
            img = plt.imshow(np.squeeze(frame))
        else:
            img.set_data(np.squeeze(frame))
        plt.pause(.0025)
        plt.draw()

        msg = ' '.join(map(str, actions[i])) + ';'
        pd.send2Pd(msg)
    print("Done!")


def replay_encoded(video, model, sess):
    img = None
    max_val = 0.00001
    for i in range(video.shape[0]):
        frame = video[[i]]
        max_val = max(max_val, frame.max())
        if img is None:
            img = plt.imshow(np.squeeze(frame))
        else:
            img.set_data(np.squeeze(frame))
        plt.pause(.0025)
        plt.draw()
        
