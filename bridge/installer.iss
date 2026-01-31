; HandOverAI Installer Script for Inno Setup 6

#define MyAppName "HandOverAI"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "SSAFY-Hackathon"
#define MyAppExeName "HandOverAI.exe"
#define MyAppDistDir "dist\HandOverAI"

[Setup]
; AppId: {C3F46574-884A-4C2E-BB55-2763DEB5A0B1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; 아이콘 설정 (추후 아이콘 추가 시 사용)
; SetupIconFile=resources\app.ico
OutputDir=.
OutputBaseFilename=HandOverAI-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; 빌드된 모든 파일 포함
Source: "{#MyAppDistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// WebView2 Runtime 체크 로직
function IsWebView2RuntimeInstalled: Boolean;
var
  Version: String;
begin
  Result := RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-99D5-4226-BE4E-7281AEBD6561}', 'pv', Version);
  if not Result then
    Result := RegQueryStringValue(HKEY_CURRENT_USER, 'Software\Microsoft\EdgeUpdate\Clients\{F3017226-99D5-4226-BE4E-7281AEBD6561}', 'pv', Version);
end;

function InitializeSetup: Boolean;
begin
  Result := True;
  if not IsWebView2RuntimeInstalled then
  begin
    if MsgBox('HandOverAI 실행을 위해 Microsoft Edge WebView2 런타임이 필요합니다.' #13#10 #13#10 '런타임이 설치되지 않은 경우 프로그램이 정상 작동하지 않을 수 있습니다. 설치를 계속하시겠습니까?', mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
    end;
  end;
end;
