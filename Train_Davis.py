from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np
import argparse
import sys, os

import Davis
import Read_Davis
import scipy.misc

from config import *

def main(argv):
    
    # read current file index
    file_index = 0
    if os.path.exists('./file_index'):
        f = open('./file_index')
        for line in f:
            file_index = int(line)
        f.close()
    f = open('./file_index', 'a+')
    logs = open('./log', 'a+')

    # import data
    #pascal_reader = read_pascal.PascalReader()

    # Create the model
    fcn = Davis.FCN16VGG() 
    x = tf.placeholder(tf.float32) #shape=[batch size, dimemsionality] 
    y_ = tf.placeholder(tf.float32)
    y = fcn.build(x, train=True, num_classes=NUM_CLASSES, 
                random_init_fc8=True, debug=True)

	# Define loss and optimizer
    cross_entropy = tf.reduce_mean(
        tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y))
    train_step = tf.train.GradientDescentOptimizer(LR).minimize(cross_entropy)

    # Session Define
    init = tf.global_variables_initializer()
    sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True,
                                            log_device_placement=False))
    sess.run(init)
    saver = tf.train.Saver()
    if file_index != 0:
        saver.restore(sess, "./models/model%s.ckpt"%MODEL_INDEX)
        print("Model restored ...")
    
    # Training
    print('='*40)
    print('Training ...')
    loss = []
    for i in range(MAX_ITER):
        batch_xs, batch_ys, filename = pascal_reader.next_batch(BATCH_SIZE)
        _, loss_val = sess.run([train_step,cross_entropy], feed_dict={x: batch_xs, y_: batch_ys})
        save_path = saver.save(sess, "./models/model%s.ckpt"%MODEL_INDEX)      
        loss.append(loss_val)
        f.write(str(file_index+i+1)+'\n')
        log = 'Iteration: %s'%str(i) + ' | Filename: %s'%filename + \
                ' | Model saved in file: %s'%save_path + ' | Cross entropy loss: %s'%str(loss_val)
        logs.write(log+'\n')
        print(log)
    log.close()
    f.close()
    np.save('./models/trCrossEntropyLoss%s'%MODEL_INDEX, np.array(loss))


if __name__=='__main__':
    if not os.path.exists('models'):
        os.makedirs('models')
    tf.app.run(main=main, argv=[])


