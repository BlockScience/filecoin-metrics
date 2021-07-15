import pandas as pd
import scipy.stats as stats


'''

"Blockchain Economics Signal Processing" - EDA starter kit - Rai + Filecoin learnings. Write-up with generalized methodology
'''

import numpy as np
import matplotlib.pyplot as plt




def time_analysis(df,timestamp_column):
    '''
    '''
    
    df['timestampDiff'] = df[timestamp_column].diff()
    df['timestampDiff'].fillna(0,inplace=True)
    
    # convert from minutes to hours
    data = df.timestampDiff.apply(lambda x: x/3600)

    # Fit a normal distribution to the data:
    mu, std = stats.norm.fit(data)
    plt.figure(figsize=(10, 8))
    # Plot the histogram.
    plt.hist(data, bins=100, density=True, alpha=0.6, color='g',label='Histogram of timestamp differences in hours')

    # Plot the PDF.
    x = np.linspace(0, 3, 100)
    p = stats.norm.pdf(x, mu, std)
    plt.plot(x, p, 'k', linewidth=2, color = 'b',label ='Normal distrbution')
    title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
    plt.title(title)
    plt.legend()

    plt.show()
    
    

def fourier_transform(df,column,components):
    '''
    Definition:
    Performs Fourier Transform off of a pandas dataframe
    
    Parameters:
    df: pandas dataframe containing a signal and a timestamp column
    column: string of signal column name
    components: int of number of components to decompose to.
    
    Example:
    fourier_transform(derived_gas_outputs,'mean_gas_fee_cap',20)
    
    Returns:
    
    Three plots and updated df with decomposed signal, and an array of the decomposed signal
    
    '''

    print('Fourier Transform of {} with {} components.'.format(column,components))
    # calculate fourier transform
    fft = np.fft.fft(np.asarray(df[column].tolist()))
    fft_df = pd.DataFrame({'fft':fft})
    fft_df['absolute'] = fft_df['fft'].apply(lambda x: np.abs(x))
    fft_df['angle'] = fft_df['fft'].apply(lambda x: np.angle(x))
    
    # plot frequencies
    t = np.linspace(0, 0.5, len(df))
    s = df[column]
    fft = np.fft.fft(s)
    T = t[1] - t[0]  # sampling interval 
    N = s.size

    # 1/T = frequency
    f = np.linspace(0, 1 / T, N)
    plt.figure(figsize=(10, 4))
    ax1 = plt.subplot( 1, 2, 1 )
    ax1.bar(f[:N // 2], np.abs(fft)[:N // 2] * 1 / N, width=1.5,log=True)  # 1 / N is a normalization factor

    ax1.set_title('{} logged in Frequency Domain'.format(column))
    ax1.set_ylabel("Amplitude")
    ax1.set_xlabel("Frequency")
    
    # Decompose signal into components
    components_scaled = int(components/2)
    fft_list = np.asarray(fft_df['fft'].tolist())
    fft_list[components_scaled:-components_scaled] = 0

    #plot decomposition
    ax2 = plt.subplot( 1, 2, 2 )
    ax2.plot(df['timestamp'], np.fft.ifft(fft_list))
    ax2.set_title('{} Components in Time Domain'.format(components))
    ax2.set_ylabel(column)
    ax2.set_xlabel('Time')

    plt.tight_layout()
    plt.xticks(rotation=90)

    plt.show()
    
    new_column = column + '_decomposed'
    df[new_column] = np.fft.ifft(fft_list)
    
    df.plot(x='timestamp',y=[column,new_column],title='Original Signal and Smoothed Signal',
            kind='line',grid=True)

    return df, np.fft.ifft(fft_list)



def phase_shift_overlay(timestamps,signal1,signal2,signal1label,signal2label):
    '''
    '''
    
    fig, ax = plt.subplots()

    ax.plot(timestamps,signal1, color='red',label=signal1label)
    ax.tick_params(axis='y', labelcolor='red')
    ax.tick_params(axis='x', labelrotation=90)
    ax.legend(bbox_to_anchor=(1, 1), loc='upper right', ncol=1)
    # Generate a new Axes instance, on the twin-X axes (same position)
    ax2 = ax.twinx()

    ax2.plot(timestamps,signal2, color='green',label=signal2label)
    ax2.tick_params(axis='y', labelcolor='green')
    ax2.tick_params(axis='x', labelrotation=90)
    ax2.legend(bbox_to_anchor=(1, .9), loc='upper right', ncol=1)
    plt.title('Fourier decomposed signals in Time Domain')
    plt.show()