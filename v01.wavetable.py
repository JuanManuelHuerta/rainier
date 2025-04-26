import simpleaudio as sa

import numpy as np

import scipy.io.wavfile as wav
from collections import namedtuple

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
	

Note = namedtuple('Note','sample_rate f t gain fade_length')
Wavetable = namedtuple('Wavetable','waveform wavetable_len wave_table')
Motif = namedtuple('Motif','bpm beats_per_compass num_compassess sample_rate wav_motif')

		


def main():
	
	basic_note =Note(44100,110,0.2,-5,500)

	sine_wavetable =Wavetable(np.sin,64,None)

	basic_motif = Motif(240,4,4,44100,None)
	#basic_motif._replace(wav_motif=np.zeros((int(basic_motif.num_compassess*basic_motif.bpm*60*basic_motif.sample_rate),)))
	


	working_wave_table=np.zeros((sine_wavetable.wavetable_len,))
	for n in range(sine_wavetable.wavetable_len):
		working_wave_table[n]=sine_wavetable.waveform(2*np.pi* n /sine_wavetable.wavetable_len)
	output = np.zeros((int(basic_note.t*basic_note.sample_rate),))
	index = 0
	index_increment = basic_note.f * sine_wavetable.wavetable_len  / basic_note.sample_rate
	for n in range(output.shape[0]):
		output[n]=interpolate_linearly(working_wave_table,index)
		index += index_increment
		index %= sine_wavetable.wavetable_len
	amplitude = 32767*10**(basic_note.gain/20)
	output *= amplitude
	output = fade_in_out(output,fade_length=basic_note.fade_length)
	sine_wavetable._replace(wave_table=output)


	working_motif_wave = np.zeros(int(basic_motif.num_compassess*basic_motif.beats_per_compass*60.0*basic_motif.sample_rate/(basic_motif.bpm)))
	samples_per_beat = basic_motif.sample_rate*60/basic_motif.bpm
	l = output.shape[0]
	for n in range(basic_motif.beats_per_compass*basic_motif.num_compassess):
		working_motif_wave[int(samples_per_beat*n):int(samples_per_beat*n)+l]=np.add(working_motif_wave[int(samples_per_beat*n):int(samples_per_beat*n)+l], output)
	basic_motif._replace(wav_motif=working_motif_wave.astype(np.int16))


	play_obj=sa.play_buffer(working_motif_wave.astype(np.int16),1,2,basic_note.sample_rate)
	play_obj.wait_done()

if __name__=="__main__":
	main()


