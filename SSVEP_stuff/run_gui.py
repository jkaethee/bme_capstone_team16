import PySimpleGUIQt as sg
from explorepy.explore import Explore
from explorepy.stream_processor import TOPICS
from ssvep_stimulation import OnlineSSVEP
import math

device_name = 'Explore_84A1'
refresh_rate = 60
arduino_flag = False
explore = Explore()
explore.connect(device_name=device_name)
explore.set_channels(channel_mask='11001111')

sg.theme('Reddit')
# Everything inside the window
layout = [  [sg.Text(f'Mentalab Explore Device: {device_name}', font=('MS Sans Serif', 17, 'italics'))],
            [sg.Button('Check Impedance')],
            [sg.Button('Arduino Test?', key='-Arduino-', button_color = ('white', 'red'))],
            [sg.Text('SSVEP simulation window', font=('MS Sans Serif', 15, 'bold'))],
            [sg.Text('How long should the simulation be (seconds)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='30')],
            [sg.Text('EEG signal length to be analyzed (seconds)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='3')],
            [sg.Text('EEG sampling rate (Hz)?', font=('MS Sans Serif', 11)), sg.Combo(['250', '500', '1000'], default_value='250')],
            [sg.Text('Top left frequency (Hz)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='12', key='top_left')],
            [sg.Text('Bottom left frequency (Hz)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='10', key='bottom_left')],
            [sg.Text('Top right frame frequency (Hz)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='8.5', key='top_right')],
            [sg.Text('Bottom right frame frequency (Hz)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='7.5', key='bottom_right')],
            [sg.Text('Classification Method', font=('MS Sans Serif', 11)), sg.Combo(['CCA'], default_value='CCA', key='analysis')],
            [sg.Text('EEG File Name?', font=('MS Sans Serif', 11)), sg.InputText(default_text='example', key='eeg_name')],
            [sg.Button('Start'), sg.Button('Cancel')] ]

# Create the Window
window = sg.Window('SSVEP simulation', layout, size=(800, 300), return_keyboard_events=True)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break

    if event == 'Check Impedance':
        explore.measure_imp()

    if event == '-Arduino-':
        
        if not arduino_flag:
            window['-Arduino-'].update(button_color =('white', 'green'))
            arduino_flag = True
        else:
            arduino_flag = False
            window['-Arduino-'].update(button_color =('white', 'red'))
    
    # If the user clicks Start or uses the 'Enter' button on their keyboard
    if event == 'Start' or event == 'special 16777220':
        ssvep_duration = int(values[0])
        signal_len = int(values[1])
        eeg_s_rate = int(values[2])
        explore.set_sampling_rate(sampling_rate=eeg_s_rate)

        freq_keys = ['top_left', 'bottom_left', 'top_right', 'bottom_right']
        fr_rates = []
        for freq_key in freq_keys:
            fr_rates.append(round(refresh_rate/float(values[freq_key])))
        analysis_type = values['analysis']
        experiment = OnlineSSVEP(refresh_rate, signal_len, eeg_s_rate, fr_rates, analysis_type, arduino_flag)

        # subscribe the experiment buffer to the EEG data stream
        explore.stream_processor.subscribe(callback=experiment.update_buffer, topic=TOPICS.raw_ExG)
        explore.record_data(file_name=values['eeg_name'], duration=ssvep_duration, file_type='csv', do_overwrite=True)
        experiment.run_ssvep(ssvep_duration)

window.close()