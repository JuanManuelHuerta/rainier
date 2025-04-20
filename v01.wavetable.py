import numpy as np

import scipy.io.wavfile as wav

def interpolate_linearly(wave_table,index):
	truncated_index = int(np.floor(index))
	next_index = (truncated_index + 1)%wave_table.shape[0]
	next_index_weight = index - truncated_index
	truncated_index_weight = 1 - next_index_weight
	return truncated_index_weight * wave_table[truncated_index] + \
		next_index_weight * wave_table[next_index]	


def fade_in_out(signal, fade_length = 1000):
	fade_in = (1- np.cos(np.linspace(0, np.pi, fade_length)))*0.5
	fade_out = np.flip(fade_in)
	signal[:fade_length]=np.multiply(fade_in,signal[:fade_length])
	signal[-fade_length:]=np.multiply(fade_out,signal[-fade_length:])
	return (signal)
	



def main():
	sample_rate = 44100
	f = 440
	t = 3
	waveform = np.sin

	wavetable_len = 64
	wave_table =np.zeros((wavetable_len,))

	for n in range(wavetable_len):
		wave_table[n]=waveform(2*np.pi* n /wavetable_len)

	output = np.zeros((t*sample_rate,))
	index = 0
	index_increment = f * wavetable_len  / sample_rate

	for n in range(output.shape[0]):
		output[n]=interpolate_linearly(wave_table,index)
		index += index_increment
		index %= wavetable_len

	gain = -20
	amplitude = 10**(gain/20)
	output *= amplitude
	output = fade_in_out(output,fade_length=100000)


	wav.write('sine440.wav', sample_rate, output.astype(np.float32))

if __name__=="__main__":
	main()


