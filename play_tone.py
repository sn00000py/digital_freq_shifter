import numpy as np
#import pyaudio
import argparse
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(
                    prog='play_tone',
                    description='sandbox for discovery on digital_freq shifter',
                    epilog='IDK')
parser.add_argument('--tone_file', help='raw adc file to be used')
parser.add_argument('--arb_tone', default=None, type=float, help='freq of tone in kHz')
parser.add_argument('--multi_tone', nargs='+', type=float, help='provide a list of frequencies to be in the tone as floats')
parser.add_argument('--shift_by', type=float, help='how much the data should be shifted by in kHz. Use positive to shift up (higher pitch) and negative to shift down (lower pitch)')
parser.add_argument('--play', default=False, help='When this flag is set, the tone will be played over the speakers')
parser.add_argument('--tone_length', default=5, type=float, help='duration of tone. Should only be used with arb_tone flag')
parser.add_argument('--graph', default=False, action='store_true', help='graphs the tone generated and any shifting')
parser.add_argument('--amplitude', nargs='+', type=float, default=[1.0], help='Amplitude of the generated tone')
parser.add_argument('--offset', nargs='+', type=float, default=[0], help='offset of the generated tone')
parser.add_argument('--save_to', help='file_path for tone to be saved to')
parser.add_argument('--sample_rate', type=float, default=40.0, help='Sample rate of tone in KHz')
args = parser.parse_args()

data = None
shifted_data = None
time_axis = None
amp = args.amplitude
offset = args.offset
sample_rate = args.sample_rate
num_samples = 0
xf = None

def gen_single_tone(freq, dur, sample_rate = 40, amp=1, offset=0):
    '''
    Generates a sinosoidal tone sampled @ 40KHZ
    freq: frequency of the tone in KHz
    dur: length of the tone in seconds
    sample_rate: sample rate in KHz
    '''
    freq = freq*1000
    num_samples = int(sample_rate * 1000 * dur)
    data = np.full(num_samples, 0, dtype=float)
    #sine equation = amp * sine(2pi * freq t)
    time = 0
    time_axis = np.full(num_samples, 0, dtype=float)
    inc_amount = 1/(sample_rate * 1000)
    for i in range(num_samples):
        data[i] = amp*np.sin(2*np.pi*time*freq)
        time_axis[i] = time
        time += inc_amount
    xf = np.linspace(0.0, 1.0/(2.0*inc_amount), num_samples//2)
    return data, time_axis, xf, num_samples

def gen_multi_tone(freqs, dur, sample_rate=40, amp=[1], offset=[0]):
    '''
    generates a tone with multiple frequencies
    freqs: list of frequencies to build the tone
    dur: length of tone in seconds
    sample_rate: the rate the data was 'sampled' at
    '''
    if len(amp) != len(freqs):
        print('Amplitude list length must be equal to freqs')
        exit()

    if len(offset) != len(freqs):
        print('Offset list length must be equal to freqs')
        exit()

    num_samples = int(sample_rate * 1000 * dur)
    data = np.full(num_samples, 0, dtype=float)
    time = 0
    time_axis = np.full(num_samples, 0, dtype=float)
    inc_amount = 1/(sample_rate * 1000)

    for ii, f in enumerate(freqs):
        freq = f * 1000
        for i in range(num_samples):
            data[i] += amp[ii]*np.sin(2*np.pi*time*freq)
            time_axis[i] = time
            time += inc_amount
    xf = np.linspace(0.0, 1.0/(2.0*inc_amount), num_samples//2)
    return data, time_axis, xf, num_samples

    

if args.arb_tone is not None:
    data, time_axis, xf, num_samples = gen_single_tone(args.arb_tone, args.tone_length, args.sample_rate, args.amplitude, args.offset)

if args.multi_tone is not None:
    if len(amp) == 1:
        amp = amp*len(args.multi_tone)
    
    if len(amp) != len(args.multi_tone):
        print('ERROR, Not a valid amplitude value/list')
        exit()

    if len(offset) == 1:
        offset = offset*len(args.multi_tone)

    if len(amp) != len(args.multi_tone):
        print('ERROR, Not a valid offset value/list')
        exit()

    data, time_axis, xf, num_samples = gen_multi_tone(args.multi_tone, args.tone_length, args.sample_rate, amp, offset)

if args.shift_by is not None:
    if data is None:
        print('Error: No input data supplied. Exiting...')
        exit()
    fft_data = np.fft.fft(data)
    plt.plot(xf, 2/num_samples*np.abs(fft_data[:num_samples//2]))
    plt.show()

if args.graph:
    if shifted_data is not None:
        pass
    else:
        plt.plot(time_axis, data)       
    plt.show()