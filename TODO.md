TODO
----

- Need to document how things work right now (shortcut,
  key bindings, mouse bindings, buttons, etc.).
- Software preferences (record options, audio driver setup)
    - partially done
- Master effects for both input and output section
- Spatialisation (partially done with the Pan object) Need more work.
- Improving effect modules (add spectral category)
- Do we offer synthesis algorithms as input boxes?
- BPF - playback mode, window size **done**
- Automators on fx parameters. **done**
- AudioIn, one gain per input **done** (do we do the same for AudioOut?) **done**
- On tracks canvas: Double-click to open the FxView. **done** 
- On tracks canvas: Click+drag to move FxBoxes. **done**
- Remember app pos and size in saved file. **done**
- Automatic fx connection (serial, parallel), GUI conection design **done**
- Edit mode versus playing mode **done**
- Live update of changes on a track. **done**
- SaveAs should copy the entire project, not just create a new .qlp file. **done**
- BusIn - BusOut
- Insert cue after selection
- colour Chooser on cue
- saveas snapshot (only a .qlp file in the same project folder)

- Documentation/archive prototype
- META data framework
- Arbitrary interpolation between two cues
- Record functions for both the input sound and the processed sound

- global interpolation time does not affect automators.

TODO / Meeting on 18/09/2015
---------------------

    - autoremove config/project file if not valid
        - Need a sanity function to check loaded prefs...
    - add symbols to make it more intuitive

TODO / Meeting on 05/10/2015
---------------------

    - MIDI-learn: use a global MIDI-learn state instead of the current
      individual process **done**
    - Use 'del' key for unassigning MIDI **done**
    - Add Cut/copy/paste options for Cues **done**
    - **urgent** fix crash when closing the audio server **done**
    - fix 'new project' option in the menu **done**
    - parameters values for soundfiles should update in 'realtime' **done**

    - macro task: conceive a monitor module, which will provide realtime
      visualization of automations and other parameters (probably using OSC).

TODO / Play mode (frozen session)
---------
- Background colour darker **done**
- No "saveCue()" before loading a new cue **done**
- Can't add or delete a soundfile **done**
- Can't add or delete a cue **done**
- Can't add, delete, move or replace an fxbox or a track **done**
- disable menu items **done**
- ask for saving when switching in play mode **done**

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
  interpolation window). **done** (just give nothing to playFunction and 
  editFunction arguments)
- Add a current selected soundfile **done**
- Floating window to show current cue number **done**
- Add Soundfile transpo and gain attributes to cue and interpolation design. **done**
- MIDI/Key learn pour cues (mode forward-backward and/or key-per-cue) **done**
- fix: harmonizer mutes the output when activated **done**
- Use shift+crtl+c for Cue windows instead of ctrl+c **done**
- classer les effets par categorie (filtres, delay, reverb...) **done**
- Automatically clean up sounds folder on close/quit. **done**
- Licensing **done**
