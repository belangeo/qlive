TODO
----

- Follower applied on transpo and gain parameters of the soundfile player
- MIDI/Key learn pour cues (mode forward-backward and/or key-per-cue) **done**
    - There is no "key learn" yet.
- Software preferences (record options, audio driver setup) 
- Interpolations (global, track, fx, parameter)
- BPF - playback mode, window size
- Automatic fx connection (serial, parallel), GUI conection design
- Handling SoundFilePlayer number of channels and routing to the tracks 
- Record functions for both the input sound and the processed sound
- Reset cue, standby function
- Edit mode versus playing mode
- Floating window to show current cue number
- Master effects for both input and output section
- Spatialisation (partially done with the Pan object)
- Licensing
- Improving effect modules (with categories)
- Warning audio out (?)
- Documentation/archive prototype
- Designing project architecture (save file)
- Need a mecanism to disable play/edit button on the knob (ex. for the 
global interpolation window).

Global Interpolation Window
---------------------------

(.) current cue     () all cues

(.) current track   () all tracks  


        (interpKnob)
        
      [Apply] [Close] <-- only apply when pressing the "apply" button


