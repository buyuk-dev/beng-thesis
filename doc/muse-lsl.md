# About muse-lsl

## MuseLSL command line client usage

    muselsl list
    muselsl stream
    muselsl stream --name Muse-7E45             // For some reason auto discovery of visible Muse devices didnt work for me.
    muselsl stream -a "00:55:DA:B5:7E:45"

    muselsl view
    muselsl view --version 2                    // if segfault without --version
    muselsl view --version 2 --window 10


In case bluetooth refuses to turn on after attempted restart:

    sudo rmmod btusb && sudo modprobe btusb && sudo rfkill unblock


## Muse LSL stream info in xml format (StreamInlet info as xml)

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

