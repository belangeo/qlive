TODO
----

- Follower applied on transpo and gain parameters of the soundfile player
- Do we offer synthesis algorithms as input boxes?
- Software preferences (record options, audio driver setup)
    - partially done, missing nchnls and inchnls
- BPF - playback mode, window size
- Automatic fx connection (serial, parallel), GUI conection design
- Record functions for both the input sound and the processed sound
- Edit mode versus playing mode
- Master effects for both input and output section
- Spatialisation (partially done with the Pan object)
- Licensing
- Improving effect modules (with categories)
- Documentation/archive prototype
- Designing project architecture (save file)

Meeting on 18/09/2015
---------------------
    - **urgent** set input/output devices from preferences panel **done**
    - fix: replacing a new project with same name doesn't work **done**
    - no more clicks pop-up for loading sounds -> single dialog **done**
    - MIDI learn for each effect **done**
    - push 'play' to the first column in soundfiles panel **done**
    - replace play/record with a toggle **done**

    - autoremove config/project file if not valid
        - Need a sanity function to check loaded prefs...
    - default interpolation time option for future cues
    - overwrite option for interpolation time
    - add symbols to make it more intuitive
    - all available effects should be there for Master input/output
    - classer les effets par categorie (filtres, delay, reverb...)
        - regarder dans fxbox_def, doit être modifié pour ça
        - référence: les categories dans logic pro
        - phase vocoder: dans une categorie "spectrale"

Play mode
---------
- No "saveCue()" before loading a new cue
- Can't add or delete a soundfile
- Can't add or delete a cue
- Can't add, delete or replace an fxbox or a track

Recently done
-------------
- Reset cue, standby function **done**
- Interpolations (global, track, fx, parameter) **done**
- Handling SoundFilePlayer number of channels and routing to the tracks **done**
- Need a mecanism to disable play/edit button on the knob (ex. for the global 
interpolation window). **done** (just give nothing to playFunction and editFunction arguments)
- Add a current selected soundfile **done**
- Floating window to show current cue number **done**
- Add Soundfile transpo and gain attributes to cue and interpolation design. **done**
- MIDI/Key learn pour cues (mode forward-backward and/or key-per-cue) **done**
    - There is no "key learn" yet.
