# Notes on EEG processing with Muse EEG headset

## Lab Streaming Layer or LSL
is a system designed to unify the collection of time
series data for research experiments. It has become standard in the field of
EEG-based brain-computer interfaces for its ability to make seperate streams of
data available on a network with time synchronization and near real-time
access. For more information, check out this lecture from Modern Brain-Computer
Interface Design or the LSL repository

https://github.com/sccn/labstreaminglayer
https://www.youtube.com/watch?v=Y1at7yrcFW0


## Interesting research papers

https://www.nature.com/articles/s41598-020-75379-w
https://www.researchgate.net/publication/338186731_Consumer_grade_EEG_Measuring_Sensors_as_Research_Tools_A_Review


## Other online resources

https://eegedu.com/


## Installing MuseLSL python library

https://github.com/alexandrebarachant/muse-lsl
https://github.com/alexandrebarachant/muse-lsl/blob/master/examples/neurofeedback.py

    sudo apt install libpcap-dev libpcap0.8 libpcap0.8-dev
    sudo apt install python3-tk
    sudo apt install python3-vispy

    pip install muselsl
    pip install pygatt==3.1.1
    pip install mne


## MuseLSL command line client usage

    muselsl list
    muselsl stream
    muselsl stream --name Muse-7E45             // For some reason auto discovery of visible Muse devices didnt work for me.
    muselsl stream -a "00:55:DA:B5:7E:45"

    muselsl view
    muselsl view --version 2
    muselsl view --version 2 --window 10


## Muse usage:

https://hackaday.io/project/162169-muse-eeg-headset-making-extra-electrode


### Muse LSL stream info in xml format (StreamInlet info as xml)

    <?xml version="1.0"?>
    <info>
        <name>Muse</name>
        <type>EEG</type>
        <channel_count>5</channel_count>
        <nominal_srate>256</nominal_srate>
        <channel_format>float32</channel_format>
        <source_id>Muse00:55:DA:B5:7E:45</source_id>
        <version>1.1000000000000001</version>
        <created_at>19359.296126331999</created_at>
        <uid>0f337a34-37d6-4cd2-acba-278dddd9a507</uid>
        <session_id>default</session_id>
        <hostname>avdevbox</hostname>
        <v4address />
        <v4data_port>16572</v4data_port>
        <v4service_port>16572</v4service_port>
        <v6address />
        <v6data_port>16573</v6data_port>
        <v6service_port>16573</v6service_port>
        <desc>
            <manufacturer>Muse</manufacturer>
            <channels>
                <channel>
                    <label>TP9</label>
                    <unit>microvolts</unit>
                    <type>EEG</type>
                </channel>
                <channel>
                    <label>AF7</label>
                    <unit>microvolts</unit>
                    <type>EEG</type>
                </channel>
                <channel>
                    <label>AF8</label>
                    <unit>microvolts</unit>
                    <type>EEG</type>
                </channel>
                <channel>
                    <label>TP10</label>
                    <unit>microvolts</unit>
                    <type>EEG</type>
                </channel>
                <channel>
                    <label>Right AUX</label>
                    <unit>microvolts</unit>
                    <type>EEG</type>
                </channel>
            </channels>
        </desc>
    </info>


