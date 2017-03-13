TODO
----

- Need to document how things work right now (shortcut,
  key bindings, mouse bindings, buttons, etc.).
- Software preferences (record options, audio driver setup)
    - partially done
- Master effects for both input and output section
- Spatialisation (partially done with the Pan object) Need more work.
- Do we offer synthesis algorithms as input boxes (as midi synths)?
- ~~Improving effect modules (add spectral category)~~
- ~~BPF - playback mode, window size~~
- ~~Automators on fx parameters.~~
- ~~AudioIn, one gain per input~~ ~~(do we do the same for AudioOut?)~~
- ~~On tracks canvas: Double-click to open the FxView.~~ 
- ~~On tracks canvas: Click+drag to move FxBoxes.~~
- ~~Remember app pos and size in saved file.~~
- ~~Automatic fx connection (serial, parallel), GUI conection design.~~
- ~~Edit mode versus playing mode.~~
- ~~Live update of changes on a track.~~
- ~~SaveAs should copy the entire project, not just create a new .qlp file.~~

- BusIn - BusOut
- Insert cue after selection
- colour Chooser on cue
- saveas snapshot (only a .qlp file in the same project folder)

- Documentation/archive prototype
- META data framework
- Arbitrary interpolation between two cues
- Record functions for both the input sound and the processed sound

- global interpolation time does not affect automators.
- Track mute?
- If we jump to a cue for which a soundfile is set to "Through" but it is
  not already playing, shouldn't we start it?

TODO / Meeting on 18/09/2015
---------------------

- autoremove config/project file if not valid
    - Need a sanity function to check loaded prefs...
- add symbols to make it more intuitive

TODO / Meeting on 05/10/2015
---------------------

- ~~MIDI-learn: use a global MIDI-learn state instead of the current
  individual process.~~
- ~~Use 'del' key for unassigning MIDI.~~
- ~~Add Cut/copy/paste options for Cues.~~
- ~~**urgent** fix crash when closing the audio server.~~
- ~~fix 'new project' option in the menu.~~
- ~~parameters values for soundfiles should update in 'realtime'.~~

- macro task: conceive a monitor module, which will provide realtime
  visualization of automations and other parameters (probably using OSC).

TODO / Play mode (frozen session)
---------
- ~~Background colour darker.~~
- ~~No "saveCue()" before loading a new cue.~~
- ~~Can't add or delete a soundfile.~~
- ~~Can't add or delete a cue.~~
- ~~Can't add, delete, move or replace an fxbox or a track.~~
- ~~Disable menu items.~~
- ~~Ask for saving when switching in play mode.~~

Recently done
-------------
- ~~Follower applied on transpo and gain parameters of the soundfile player.~~
- ~~Add 'recent projects' in the intro dialog.~~
- ~~**urgent** Set input/output devices from preferences panel.~~
- ~~Fix: replacing a new project with same name doesn't work.~~
- ~~No more clicks pop-up for loading sounds -> single dialog.~~
- ~~MIDI learn for each effect.~~
- ~~Push 'play' to the first column in soundfiles panel.~~
- ~~Replace play/record with a toggle.~~
- ~~Default interpolation time option for future cues.~~
- ~~Overwrite option for interpolation time.~~
- ~~Reset cue, standby function.~~
- ~~Interpolations (global, track, fx, parameter).~~
- ~~Handling SoundFilePlayer number of channels and routing to the tracks.~~
- ~~Need a mecanism to disable play/edit button on the knob (ex. for the global
  interpolation window). (just give nothing to playFunction and 
  editFunction arguments)~~
- ~~Add a current selected soundfile.~~
- ~~Floating window to show current cue number.~~
- ~~Add Soundfile transpo and gain attributes to cue and interpolation design.~~
- ~~MIDI/Key learn pour cues (mode forward-backward and/or key-per-cue).~~
- ~~Fix: harmonizer mutes the output when activated.~~
- ~~Use shift+crtl+c for Cue windows instead of ctrl+c.~~
- ~~Classer les effets par categorie (filtres, delay, reverb...).~~
- ~~Automatically clean up sounds folder on close/quit.~~
- ~~Licensing.~~
