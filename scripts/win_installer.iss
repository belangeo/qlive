; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{A54A6BE9-9A15-49D6-B31F-4D71E2488297}
AppName=QLive
AppVersion=0.1.4
AppPublisher=iACT.umontreal.ca
; AppPublisherURL=http://ajaxsoundstudio.com/software/soundgrain
; AppSupportURL=http://ajaxsoundstudio.com/software/soundgrain
; AppUpdatesURL=http://ajaxsoundstudio.com/software/soundgrain
DefaultDirName={pf}\QLive
DisableDirPage=yes
DefaultGroupName=QLive
AllowNoIcons=yes
OutputBaseFilename=QLive_0.1.4_setup
Compression=lzma
SolidCompression=yes
ChangesAssociations=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\olivier\git\qlive\QLive_Win\QLive.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\olivier\git\qlive\QLive_Win\Resources\*"; DestDir: "{app}\Resources"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Registry]
Root: HKCR; Subkey: ".sg"; ValueType: string; ValueName: ""; ValueData: "QLiveFile"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "QLiveFile"; ValueType: string; ValueName: ""; ValueData: "QLive File"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "QLiveFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\Resources\QLive-Icon.ico"
Root: HKCR; Subkey: "QLiveFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\QLive.exe"" ""%1"""

[Icons]
Name: "{group}\QLive"; Filename: "{app}\QLive.exe"; WorkingDir: "{app}"
Name: "{commondesktop}\QLive"; Filename: "{app}\QLive.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\QLive.exe"; Description: "{cm:LaunchProgram,QLive}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\QLive Uninstall"








