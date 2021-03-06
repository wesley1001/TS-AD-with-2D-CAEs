import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pyts.image import GramianAngularField
from skimage.measure import block_reduce
import os

# Functions
##############################################

def import_data(path_dataset):
    """Import data from hdf5 file"""

    X=np.array(pd.read_hdf(path_dataset))

    print('Data set shape:',np.shape(X))
    print('#####################################')
    
    return X

def slice_timeseries(n_slices,dataset):
    """ Cut each time series in the dataset into equally sized slices of size -> Length of time series/n_slices.
    The function returns a matrix with shape (nr. of slices, slice length)"""

    n,l=np.shape(dataset)

    X = np.reshape(dataset,(n*n_slices,l//n_slices))

    print('sliced data shape (nr. of slices, slice length):',np.shape(X))
    print('#####################################')
    
    return X

def encode_dataset(batch_size,downscale_factor,dataset, pooling_function):
    """ Computation of encodings has to be done in batches due to the large size of the dataset.
        Otherwise the kernel will die!
        
        For downscaling pick np.mean (average pooling) or np.max (max pooling) respectively.
        If downscaling is not required choose downscale_factor=1.
        Keep in mind the network expects an input image size of 64x64.
        
        The function returns a 3D matrix.
        The new 3D matrix contains several 2D matrices, which correspond to the time series encodings/images.
        The order of the objects does not change, which means for example that the 23rd slice of the 
        input dataset corresponds to the 23rd encoding in the 3D Matrix."""
    
    n,l=np.shape(dataset)
    f=downscale_factor
    n_batches=n//batch_size
    batches=np.linspace(1,n_batches,n_batches, dtype=int) * batch_size

    gaf = GramianAngularField(image_size=1., method='summation')
    
    print('Encoding started...')
    for p in range(n_batches):
        if p==0:
            X_gaf = gaf.transform(dataset[0:batches[p],:])
            sample=block_reduce(X_gaf[0], block_size=(f, f), func=pooling_function)
            l_red = sample.shape[0]
            X_gaf_red = np.zeros((n,l_red,l_red))
            print('output 3D Matrix shape: ', np.shape(X_gaf_red))

            j=0
            for i in range(0,batches[p]):
                X_gaf_red[i] = block_reduce(X_gaf[j], block_size=(f, f) , func=pooling_function)
                j+=1

        else:                          
            X_gaf = gaf.transform(X[batches[p-1]:batches[p],:])

            j=0
            for i in range(batches[p-1],batches[p]):
                X_gaf_red[i] = block_reduce(X_gaf[j], block_size=(f, f) , func=pooling_function)
                j+=1
                
    print('Encoding successful!')
    print('#####################################')
    
    return X_gaf_red

def save_data(directory,dataset_name,dataset):
    """ The datasets are simply saved as numpy matrices
        To import the numpy matrix again use np.load("<path_to_file>")"""
    
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    print('Saving data...')
    np.save(os.path.join(directory,dataset_name),dataset)
    print(dataset_name,' saved at: ',os.path.join(directory,dataset_name))



# Create encodings
##############################################

if __name__=='__main__':
    
    X=import_data(path_dataset='../Input_Data/dftrain.h5')
    X_test=import_data(path_dataset='../Input_Data/dfvalid.h5')
    
    X=slice_timeseries(n_slices=120,dataset=X)
    X_test=slice_timeseries(n_slices=120,dataset=X_test)
    
    X_gaf=encode_dataset(batch_size=172,downscale_factor=8,dataset=X, pooling_function=np.mean)
    X_test_gaf=encode_dataset(batch_size=60,downscale_factor=8,dataset=X_test, pooling_function=np.mean)
    
    save_data(directory='GAF_Images',dataset_name='X_gaf.npy',dataset=X_gaf)
    save_data(directory='GAF_Images',dataset_name='X_test_gaf.npy',dataset=X_test_gaf)



# Display Images
##############################################
X_gaf=np.load('GAF_Images/X_gaf.npy')
sample_image=X_gaf[0] 
plt.figure(figsize=(5, 5))
plt.imshow(sample_image,cmap='jet')
plt.colorbar(fraction=0.0457, pad=0.04)
plt.clim(-1,1)
plt.show()

