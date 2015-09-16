TODO
----

- Follower applied on transpo and gain parameters of the soundfile player
- MIDI/Key learn pour cues (mode forward-backward and/or key-per-cue) **done**
    - There is no "key learn" yet.
- Software preferences (record options, audio driver setup) 
    - partially done, missing nchnls and inchnls
- Interpolations (global, track, fx, parameter) **done**
- BPF - playback mode, window size
- Automatic fx connection (serial, parallel), GUI conection design
- Handling SoundFilePlayer number of channels and routing to the tracks **done**
- Add a current selected soundfile **done**
- Add Soundfile transpo and gain attributes to cue and interpolation design. **done**
- Record functions for both the input sound and the processed sound
- Reset cue, standby function **done**
- Edit mode versus playing mode
- Floating window to show current cue number **done**
- Master effects for both input and output section
- Spatialisation (partially done with the Pan object)
- Licensing
- Improving effect modules (with categories)
- Warning audio out (?)
- Documentation/archive prototype
- Designing project architecture (save file)
- Need a mecanism to disable play/edit button on the knob (ex. for the global 
interpolation window). **done** (just give nothing to playFunction and editFunction arguments)

Automation Panel Design
=======================
Need to design the possible couplings (add, mul, avg, ...)
---------------------------------------------------------------
[ ] BPF

[ ] LFO

[ ] RANDOM

[ ] ENVELOPE FOLLOWER

                                    Active : []
                    
    -- Input Selection ----------------
        1   2   3   4   5   6   7   8
        
    -- Input Interpolation Time : 0.01 sec.
        
    [] Slider Values    [] Interpolation Times

        LPCUTOFF -- OUTMIN -- OUTMAX
    
[ ] PITCH FOLLOWER

[ ] ZERO-CROSSING

[ ] CENTROID
