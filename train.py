import os
import tensorflow as tf
import keras 
import cv2
import numpy as np
from math import cos, pi
import keras.backend as K
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, TensorBoard,LearningRateScheduler
from keras.utils import multi_gpu_model
import time

from resnet_model import create_Model
from loss import modelLoss
from generator import segmentationGenerator

print("**************************************\nTensorFlow detected the following GPU(s):")
tf.test.gpu_device_name()

print("\n\nSetup start: {}\n".format(time.ctime()))

# define these
batchSize = 12
trainingRunTime = time.ctime().replace(':', '_')
resnet_type = 50
Notes = 'KITTI_Road'

# build loss
lossClass = modelLoss(0.001,0.85,640,192,batchSize)
loss = lossClass.applyLoss 

# build data generators
train_generator = segmentationGenerator('data/data_road/training/image_2','data/data_road/training/gt_image_2', batch_size=batchSize, shuffle=True)
test_generator = segmentationGenerator('data/data_road/training/image_2','data/data_road/training/gt_image_2', batch_size=batchSize, shuffle=True, test=True)

# build model
model = create_Model(input_shape=(640,192,3), encoder_type=resnet_type)
model.compile(optimizer=Adam(lr=1e-3),loss=loss, metrics=['accuracy'])

# callbacks
if not os.path.exists('models/' + Notes + '_' + trainingRunTime + '_batchsize_' + str(batchSize) + '_resnet_' + str(resnet_type) + '/'):
    os.makedirs('models/' + Notes + '_' + trainingRunTime + '_batchsize_' + str(batchSize) + '_resnet_' + str(resnet_type) + '/')
mc = ModelCheckpoint('models/' + Notes + '_' + trainingRunTime +  '_batchsize_' + str(batchSize) + '_resnet_' + str(resnet_type) + '/_weights_epoch{epoch:02d}_val_loss_{val_loss:.4f}_train_loss_{loss:.4f}.hdf5', monitor='val_loss')
mc1 = ModelCheckpoint('models/' + Notes + '_' + trainingRunTime +  '_batchsize_' + str(batchSize) + '_resnet_' + str(resnet_type) + '/_weights_epoch{epoch:02d}_val_loss_{val_loss:.4f}_train_loss_{loss:.4f}.hdf5', monitor='loss')
rl = ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=2, verbose=1) # not used
tb = TensorBoard(log_dir='logs/' + Notes + '_' + trainingRunTime + '_batchsize_' + str(batchSize) + '_resnet_' + str(resnet_type), update_freq=250)

# Schedule Learning rate Callback
def lr_schedule(epoch):
    if epoch < 15:
        return 1e-3 
    else:
        return 1e-4

lr = LearningRateScheduler(schedule=lr_schedule,verbose=1)

print("\n\nTraining start: {}\n".format(time.ctime()))

model.fit_generator(train_generator, epochs = 20, validation_data=test_generator, callbacks=[mc,mc1,lr,tb], initial_epoch=0)

print("\n\nTraining end: {}\n".format(time.ctime()))