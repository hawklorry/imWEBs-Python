#define MyAppName "imWEBs Desktop"
#ifndef AppVersion
  #define AppVersion "0.1.1"
#endif
#ifndef SourceDir
  #error SourceDir must be provided: /DSourceDir=...
#endif
#ifndef OutputDir
  #define OutputDir "."
#endif
#ifndef CompressionMode
  #define CompressionMode "lzma"
#endif
#ifndef InstallerIconFile
  #define InstallerIconFile "{#SourceDir}\\imWEBs-Desktop.exe"
#endif

[Setup]
AppId={{E4A99AA4-2FB6-4CD7-B553-9744E0B3E3C7}
AppName={#MyAppName}
AppVersion={#AppVersion}
AppPublisher=University of Guelph
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir={#OutputDir}
OutputBaseFilename=imwebs-desktop-{#AppVersion}-setup
Compression={#CompressionMode}
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
SetupIconFile={#InstallerIconFile}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\imWEBs-Desktop.exe"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\imWEBs-Desktop.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\imWEBs-Desktop.exe"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
