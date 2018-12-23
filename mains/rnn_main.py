import tensorflow as tf

from models.rnn_model import RNNModel
from trainers.rnn_trainer import RNNTrainer
from data_loader.rnn_data import RNNData
from utils.config import process_config
from utils.dirs import create_dirs
from utils.logger import Logger
from utils.utils import get_args

def main():
    try:
        args = get_args()
        config = process_config(args.config)

    except:
        print("Missing or invalid arguments")
        exit(0)

    create_dirs([config.summary_dir,config.checkpoint_dir])
    sess = tf.Session()
    data = RNNData(config)
    model = RNNModel(config)
    logger = Logger(sess,config)
    trainer = RNNTrainer(sess,model,data,config,logger)
    sess.run(tf.global_variables_initializer())
    model.load(sess)
    trainer.train()

if __name__ == '__main__':
    main()
