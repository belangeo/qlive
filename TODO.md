TODO
----

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

TODO / Meeting on 18/09/2015
---------------------

    - autoremove config/project file if not valid
        - Need a sanity function to check loaded prefs...
    - add symbols to make it more intuitive
    - all available effects should be there for Master input/output
    - classer les effets par categorie (filtres, delay, reverb...)
        - regarder dans fxbox_def, doit être modifié pour ça
        - référence: les categories dans logic pro
        - phase vocoder: dans une categorie "spectrale"

TODO / Meeting on 05/10/2015
---------------------

    - MIDI-learn: use a global MIDI-learn state instead of the current
      individual process
    - Use 'del' key for unassigning MIDI
    - Add Cut/copy/paste options for Cues
    - Use shift+crtl+c for Cue windows instead of ctrl+c
    - **urgent** fix crash when closing the audio server
    - fix: harmonizer mutes the output when activated
    - fix 'new project' option in the menu
    - parameters values for soundfiles should update in 'realtime'
    - macro task: conceive a monitor modulo, which will provide realtime
      visualization of automations and other parameters (probably using OSC).

TODO / Play mode
---------
- No "saveCue()" before loading a new cue
- Can't add or delete a soundfile
- Can't add or delete a cue
- Can't add, delete or replace an fxbox or a track

Recently done
-------------
- Follower applied on transpo and gain parameters of the soundfile player **done**
- add 'recent projects' in the intro dialog **done**
- **urgent** set input/output devices from preferences panel **done**
- fix: replacing a new project with same name doesn't work **done**
- no more clicks pop-up for loading sounds -> single dialog **done**
- MIDI learn for each effect **done**
- push 'play' to the first column in soundfiles panel **done**
- replace play/record with a toggle **done**
- default interpolation time option for future cues **done**
- overwrite option for interpolation time **done**
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
