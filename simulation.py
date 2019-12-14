#!/usr/bin/env python
# coding: utf-8

# In[20]:


from PIL import Image
import numpy as np
import random
import math
import matplotlib.pyplot as plt
import time

start = -10
end = 10
step = 5
SNRdb_array = range(start, end+1, step)
base_path = "C:\\YOUR\\IMAGE\\LOCATION\\" # put your image location here.
numberOfSamples = 5
display_samples = 30
carrier = []
x = []


# In[21]:


# read image and return information about it
def read_image(image):
    # check for alpha channel
    alpha = False
    if image.endswith(".png"):
        alpha = True
        
    im = resize_image(Image.open(image), alpha, True)
    pixels = im.load()  # get image pixels (red, green, blue, alpha)
    data = im.getdata()  # get image data (red, green, blue, alpha)
    width, height = im.size  # get image height and width

    original_image_bits = ''  # signal conditioning (TX_data)

    for row in range(height):
        for column in range(width):
            if alpha:
                r, g, b, a = pixels[column, row]  # tuple (red, green, blue, alpha)
            else:
                r, g, b = pixels[column, row]  # tuple (red, green, blue)
                
            red_bits = bin(r)[2:].rjust(8, '0')  # red color bits
            green_bits = bin(g)[2:].rjust(8, '0')  # green color bits
            blue_bits = bin(b)[2:].rjust(8, '0')  # blue color bits
            original_image_bits += red_bits + green_bits + blue_bits  # string containing all bits of all colors

    original_image_bits = [int(bit, 2) for bit in original_image_bits]  # array containing all bits of all colors

    return im, data, pixels, height, width, original_image_bits


# In[22]:


# compress an image
def resize_image(image, alpha, resize):
    if not resize:
        return image
    
    resized_height = 200
    ratio = resized_height / image.size[1]
    resized_width = round(image.size[0] * ratio)
    
    ext = ""
    if alpha: 
        ext = ".png"
    else:
        ext = ".jpg"
    
    resized_image = image.resize((resized_width, resized_height), Image.ANTIALIAS)
    resized_image.save(base_path + "resized" + str(resized_width) + "x" + str(resized_height) + ext)
    
    return resized_image


# In[23]:


# display red, green, blue channels of image
def display_channels(image, data):
    red_channel = [(c[0], 0, 0) for c in data]
    green_channel = [(0, c[1], 0) for c in data]
    blue_channel = [(0, 0, c[2]) for c in data]
    
    # display red channel of image
    image.putdata(red_channel)
    display("Red channel of image")
    display(image)
    # display green channel of image
    image.putdata(green_channel)
    display("Green channel of image")
    display(image)
    # display blue channel of image
    image.putdata(blue_channel)
    display("Blue channel of image")
    display(image)


# In[24]:


# generate noise of given SNRdb
def generate_noise(SNRdb, size):
    noise = np.random.randn(size)
    SNR = 0.5 * 10 ** (-SNRdb / 10)
    chan_noise = noise * math.sqrt(SNR)
        
    display("Plotting noise: ")
    plt.plot(x[:display_samples], chan_noise[:display_samples])
    plt.show()
    
    return chan_noise


# In[25]:


# generate noisy signal adding noise signal to original signal
def generate_noisy_signal(signal, noise):
    temp = []

    for i in range(len(signal)):
        temp.append(signal[i] + noise[i])
    
    display("Plotting noisy signal: ")
    plt.plot(x[:display_samples], temp[:display_samples])
    plt.show()    
        
    return temp


# In[26]:


# modulate original digital signal to analog signal using BPSK (0 => -1, 1 => +1)
def modulate_signal(signal):
    global x
    bpsk = []
    for bit in signal:
        if bit == 0:
            bpsk.append(-1)
        else:
            bpsk.append(1)
    
    result = convert_to_analog(bpsk)
    
    display("Plotting signal with carrier: ")
    plt.plot(x[:display_samples], result[:display_samples])
    plt.show()
    
    return result


# In[27]:


# demodulate received signal from analog to digital using BPSK (0 => -1, 1 => +1)
def demodulate_signal(signal):
    temp = []
    result = signal * carrier
    temp_sum = 0
    for i in range(0, len(result), 5):
        temp_sum = sum(result[i:i+numberOfSamples])
        if temp_sum > 0:
            temp.append(1)
        else:
            temp.append(0)

    return temp


# In[28]:


# convert digital signal to analog signal
def convert_to_analog(signal):
    global carrier, x
    sample_len = 2 * np.pi
    numberOfBits = len(signal)
    sampleRange = np.linspace(0, sample_len, numberOfSamples)
    x = np.linspace(0, sample_len * numberOfBits, numberOfSamples * numberOfBits)
    carrier = np.sin(x)
    
    final_signal = []
    for i in range(numberOfBits):
        for j in sampleRange:
            final_signal.append(signal[i])
    
    return carrier * final_signal


# In[29]:


# generate image from signal
def generate_image_from_signal(signal, height, width, snr_db):
    receiving_bits = ''.join(str(rb) for rb in signal) # convert to string of bits the given channel

    received_image_pixels = [] # final array of pixels

    for i in range(0, len(receiving_bits), 24):
        rgb = receiving_bits[i:i + 24]
        red_bits = int(rgb[0:8], 2)
        green_bits = int(rgb[8:16], 2)
        blue_bits = int(rgb[16:24], 2)

        received_image_pixels.append([red_bits, green_bits, blue_bits])

    y = 0
    x = 0
    resulting_pixels = np.zeros((height, width, 3), dtype=np.uint8)

    for pixel in received_image_pixels:
        resulting_pixels[y, x] = pixel
        if x == width - 1:
            x = 0
            y += 1
        else:
            x += 1

    received_image = Image.fromarray(resulting_pixels)
    display("Original image with noise of {0} db".format(snr_db))
    display(received_image)


# In[30]:


# calculate ber = number of corrupted bits / total number of bits   
def calculate_ber(original, received):
    corrupted = 0
    n = len(original)
    for i in range(n):
        if original[i] != received[i]:
            corrupted += 1

    return corrupted/n


# In[31]:


#####################################################################################
################################## STARTING POINT ###################################
#####################################################################################

    i, d, p, h, w, s = read_image(base_path + "YOUR_IMAGE_NAME.jpg") # specify your image name inside your base_path
display_channels(i, d)
ber_per_snr_db = []

for single_snr_db in SNRdb_array:
    # sending process
    starting_time = time.time()

    modulated = modulate_signal(s)
    noise = generate_noise(single_snr_db, len(modulated))
    noisy_signal = generate_noisy_signal(modulated, noise)
    
    # receiving process
    demodulated = demodulate_signal(noisy_signal)
    generate_image_from_signal(demodulated, h, w, single_snr_db)
   
    ending_time = time.time()
    print("Processing time: {0}".format(ending_time - starting_time))
    
    # analysis
    ber = calculate_ber(s, demodulated)
    ber_per_snr_db.append(ber)
    
    print('*'*50)
    

# ploting ber vs snr db
plt.semilogy(SNRdb_array, ber_per_snr_db)
plt.xlabel('SNR (db)')
plt.ylabel('BER')
plt.grid()
plt.show()


# In[ ]:




