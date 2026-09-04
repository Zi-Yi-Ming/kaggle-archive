#Requires -Version 5.1
<#
.SYNOPSIS
    Windows Terminal One-Click Setup Script
.DESCRIPTION
    1. Set Windows Terminal as default terminal
    2. Install Cascadia Code font
    3. Beautify Windows Terminal settings.json
    4. Verify all changes
.NOTES
    Author: AtomCode
    Date: 2026-09-03
#>

$ErrorActionPreference = 'Continue'
$successCount = 0
$failCount = 0

function Write-Step {
    param([string]$Step, [string]$Message)
    Write-Host ""
    Write-Host ("=" * 50) -ForegroundColor DarkGray
    Write-Host "  [$Step] $Message" -ForegroundColor Cyan
    Write-Host ("=" * 50) -ForegroundColor DarkGray
}

function Write-OK   { param([string]$Msg) Write-Host "  [OK] $Msg" -ForegroundColor Green }
function Write-Warn { param([string]$Msg) Write-Host "  [WARN] $Msg" -ForegroundColor Yellow }
function Write-Err  { param([string]$Msg) Write-Host "  [FAIL] $Msg" -ForegroundColor Red }

# ============================================================
#  Step 1/4: Set Windows Terminal as Default Terminal
# ============================================================
Write-Step "1/4" "Set Windows Terminal as Default Terminal"

try {
    $consoleGuid  = "{2EACA947-7F5F-4CFA-BA87-8F7FBEEFBE69}"
    $terminalGuid = "{E12CFF52-A866-4C77-936F-DA6DE2EAA2D6}"
    $regPath      = "HKCU:\Console\%%Startup"

    if (-not (Test-Path $regPath)) {
        New-Item -Path $regPath -Force | Out-Null
        Write-Host "  Created registry path: $regPath" -ForegroundColor DarkGray
    }

    Set-ItemProperty -Path $regPath -Name "DelegationConsole"  -Value $consoleGuid  -Type String
    Set-ItemProperty -Path $regPath -Name "DelegationTerminal" -Value $terminalGuid -Type String

    $verifyConsole  = (Get-ItemProperty -Path $regPath -Name "DelegationConsole"  -ErrorAction Stop).DelegationConsole
    $verifyTerminal = (Get-ItemProperty -Path $regPath -Name "DelegationTerminal" -ErrorAction Stop).DelegationTerminal

    if ($verifyConsole -eq $consoleGuid -and $verifyTerminal -eq $terminalGuid) {
        Write-OK "Default terminal set to Windows Terminal"
        $successCount++
    } else {
        Write-Err "Registry verification failed after write"
        $failCount++
    }
} catch {
    Write-Err "Failed to set default terminal: $_"
    $failCount++
}

# ============================================================
#  Step 2/4: Install Cascadia Code Font
# ============================================================
Write-Step "2/4" "Install Cascadia Code Font"

try {
    $fontRegPath = "HKCU:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
    $existingFont = Get-ItemProperty -Path $fontRegPath -Name "Cascadia Code (TrueType)" -ErrorAction SilentlyContinue

    if ($existingFont -and (Test-Path $existingFont."Cascadia Code (TrueType)")) {
        Write-OK "Cascadia Code font already installed, skipping download"
        $successCount++
    } else {
        $fontUrl     = "https://github.com/microsoft/cascadia-code/releases/download/v2407.24/CascadiaCode-2407.24.zip"
        $zipPath     = Join-Path $env:TEMP "CascadiaCode.zip"
        $extractPath = Join-Path $env:TEMP "CascadiaCode_extract"

        if (Test-Path $zipPath)     { Remove-Item $zipPath -Force }
        if (Test-Path $extractPath) { Remove-Item $extractPath -Recurse -Force }

        Write-Host "  Downloading Cascadia Code ..." -ForegroundColor DarkGray

        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($fontUrl, $zipPath)
        $webClient.Dispose()

        if (-not (Test-Path $zipPath)) {
            throw "Download failed. Check network connection."
        }
        Write-Host "  Download complete. Extracting ..." -ForegroundColor DarkGray

        Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

        $ttfDir = Join-Path $extractPath "ttf"
        if (-not (Test-Path $ttfDir)) {
            $subDir = Get-ChildItem -Path $extractPath -Directory | Select-Object -First 1
            if ($subDir) { $ttfDir = Join-Path $subDir.FullName "ttf" }
        }
        if (-not (Test-Path $ttfDir)) {
            throw "ttf directory not found after extraction"
        }

        $userFontDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
        if (-not (Test-Path $userFontDir)) {
            New-Item -ItemType Directory -Path $userFontDir -Force | Out-Null
        }

        $installedCount = 0
        $ttfFiles = Get-ChildItem -Path $ttfDir -Filter "*.ttf"

        foreach ($ttf in $ttfFiles) {
            $destFile = Join-Path $userFontDir $ttf.Name
            Copy-Item -Path $ttf.FullName -Destination $destFile -Force

            $fontDisplayName = $ttf.BaseName
            $regName = "$fontDisplayName (TrueType)"

            Set-ItemProperty -Path $fontRegPath -Name $regName -Value $destFile -Type String
            $installedCount++
        }

        Write-Host "  Installed $installedCount font files" -ForegroundColor DarkGray

        $keyFont = Get-ItemProperty -Path $fontRegPath -Name "Cascadia Code (TrueType)" -ErrorAction SilentlyContinue
        if ($keyFont) {
            Write-OK "Cascadia Code font installed and registered"
            $successCount++
        } else {
            $anyCascadia = Get-ItemProperty -Path $fontRegPath -ErrorAction SilentlyContinue |
                Get-Member -MemberType NoteProperty |
                Where-Object { $_.Name -like "Cascadia*" }
            if ($anyCascadia) {
                Write-OK "Cascadia font registered (name format may differ)"
                $successCount++
            } else {
                Write-Err "Font registration verification failed"
                $failCount++
            }
        }

        Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
        Remove-Item $extractPath -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  Temp files cleaned up" -ForegroundColor DarkGray
    }
} catch {
    Write-Err "Font installation failed: $_"
    Write-Warn "You can manually download from https://github.com/microsoft/cascadia-code/releases"
    $failCount++
}

# ============================================================
#  Step 3/4: Beautify Windows Terminal Settings
# ============================================================
Write-Step "3/4" "Beautify Windows Terminal settings.json"

try {
    $settingsPath = Join-Path $env:LOCALAPPDATA `
        "Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json"

    if (-not (Test-Path $settingsPath)) {
        $settingsPath = Join-Path $env:LOCALAPPDATA `
            "Packages\Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe\LocalState\settings.json"
    }

    if (-not (Test-Path $settingsPath)) {
        throw "Windows Terminal settings.json not found"
    }

    # Backup
    $backupPath = "$settingsPath.bak"
    Copy-Item -Path $settingsPath -Destination $backupPath -Force
    Write-OK "Backup saved to: $backupPath"

    # Read existing config
    $rawContent = Get-Content -Path $settingsPath -Raw -Encoding UTF8
    $existingSettings = $rawContent | ConvertFrom-Json

    $existingProfiles = $null
    if ($existingSettings.profiles -and $existingSettings.profiles.list) {
        $existingProfiles = $existingSettings.profiles.list
    }

    # Detect PowerShell 7
    $pwsh7Guid = "{574e775e-4f2a-5b96-ac1e-a2962a402336}"
    $ps5Guid    = "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}"

    $pwsh7Path = Get-Command pwsh -ErrorAction SilentlyContinue
    if ($pwsh7Path) {
        $defaultGuid = $pwsh7Guid
        Write-Host "  Found PowerShell 7: $($pwsh7Path.Source)" -ForegroundColor DarkGray
    } else {
        $defaultGuid = $ps5Guid
        Write-Host "  PowerShell 7 not found, falling back to Windows PowerShell" -ForegroundColor DarkGray
    }

    # Build new config JSON string
    $newSettingsJson = @"
{
    "`$help": "https://aka.ms/terminal-documentation",
    "`$schema": "https://aka.ms/terminal-profiles-schema",
    "defaultProfile": "$defaultGuid",
    "theme": "dark",
    "copyOnSelect": true,
    "copyFormatting": "none",
    "trimBlockSelection": true,
    "alwaysShowTabs": true,
    "showTabsInTitlebar": true,
    "useAcrylicInTabRow": true,
    "tabWidthMode": "equal",
    "profiles": {
        "defaults": {
            "font": {
                "face": "Cascadia Code",
                "size": 14,
                "weight": "normal"
            },
            "useAcrylic": true,
            "opacity": 80,
            "padding": "8, 8, 8, 8",
            "cursorShape": "bar",
            "colorScheme": "Campbell Powershell"
        },
        "list": [
            {
                "guid": "{574e775e-4f2a-5b96-ac1e-a2962a402336}",
                "name": "PowerShell 7",
                "source": "Windows.Terminal.PowershellCore",
                "icon": "ms-appx:///ProfileIcons/pwsh.png",
                "colorScheme": "Campbell Powershell"
            },
            {
                "guid": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
                "name": "Windows PowerShell",
                "commandline": "powershell.exe",
                "icon": "ms-appx:///ProfileIcons/{61c54bbd-c2c6-5271-96e7-009a87ff44bf}.png",
                "colorScheme": "Campbell"
            },
            {
                "guid": "{0caa0dad-35be-5f56-a8ff-afceeeaa6101}",
                "name": "Command Prompt",
                "commandline": "cmd.exe",
                "icon": "ms-appx:///ProfileIcons/{0caa0dad-35be-5f56-a8ff-afceeeaa6101}.png",
                "colorScheme": "Tango Dark"
            }
        ]
    },
    "schemes": [
        {
            "name": "Campbell Powershell",
            "cursorColor": "#FFFFFF",
            "selectionBackground": "#FFFFFF",
            "background": "#012456",
            "foreground": "#CCCCCC",
            "black": "#0C0C0C",
            "red": "#C50F1F",
            "green": "#13A10E",
            "yellow": "#C19C00",
            "blue": "#0037DA",
            "purple": "#881798",
            "cyan": "#3A96DD",
            "white": "#CCCCCC",
            "brightBlack": "#767676",
            "brightRed": "#E74856",
            "brightGreen": "#16C60C",
            "brightYellow": "#F9F1A5",
            "brightBlue": "#3B78FF",
            "brightPurple": "#B4009E",
            "brightCyan": "#61D6D6",
            "brightWhite": "#F2F2F2"
        },
        {
            "name": "Tango Dark",
            "background": "#000000",
            "foreground": "#D3D7CF",
            "black": "#000000",
            "red": "#CC0000",
            "green": "#4E9A06",
            "yellow": "#C4A000",
            "blue": "#3465A4",
            "purple": "#75507B",
            "cyan": "#06989A",
            "white": "#D3D7CF",
            "brightBlack": "#555753",
            "brightRed": "#EF2929",
            "brightGreen": "#8AE234",
            "brightYellow": "#FCE94F",
            "brightBlue": "#729FCF",
            "brightPurple": "#AD7FA8",
            "brightCyan": "#34E2E2",
            "brightWhite": "#EEEEEC"
        }
    ],
    "actions": [
        { "command": "paste", "keys": "ctrl+v" },
        { "command": "copy",  "keys": "ctrl+c" },
        { "command": "find",  "keys": "ctrl+shift+f" },
        { "command": { "action": "splitPane", "split": "auto" }, "keys": "alt+shift+d" }
    ]
}
"@

    # Merge user custom profiles
    $parsedNew = $newSettingsJson | ConvertFrom-Json

    if ($existingProfiles) {
        $builtInGuids = @(
            "{574e775e-4f2a-5b96-ac1e-a2962a402336}",
            "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
            "{0caa0dad-35be-5f56-a8ff-afceeeaa6101}",
            "{2c4de342-38b7-51cf-b940-2309a097f518}"
        )

        foreach ($profile in $existingProfiles) {
            $profileGuid = $profile.guid
            if ($profileGuid -and ($profileGuid -notin $builtInGuids)) {
                $parsedNew.profiles.list += $profile
                Write-Host "  Kept custom profile: $($profile.name)" -ForegroundColor DarkGray
            }
        }
    }

    # Merge user custom schemes
    if ($existingSettings.schemes) {
        $newSchemeNames = $parsedNew.schemes | ForEach-Object { $_.name }
        foreach ($scheme in $existingSettings.schemes) {
            if ($scheme.name -notin $newSchemeNames) {
                $parsedNew.schemes += $scheme
                Write-Host "  Kept custom scheme: $($scheme.name)" -ForegroundColor DarkGray
            }
        }
    }

    # Merge user custom actions
    if ($existingSettings.actions) {
        $newKeyBindings = $parsedNew.actions | ForEach-Object { $_.keys }
        foreach ($action in $existingSettings.actions) {
            if ($action.keys -and ($action.keys -notin $newKeyBindings)) {
                $parsedNew.actions += $action
            }
        }
    }

    # Write final config
    $finalJson = $parsedNew | ConvertTo-Json -Depth 10
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($settingsPath, $finalJson, $utf8NoBom)

    # Verify
    $verifyContent = Get-Content -Path $settingsPath -Raw -Encoding UTF8
    if ($verifyContent -match '"defaultProfile"' -and $verifyContent -match '"Cascadia Code"') {
        Write-OK "settings.json updated successfully"
        Write-Host "  Path: $settingsPath" -ForegroundColor DarkGray
        $successCount++
    } else {
        Write-Err "settings.json verification failed after write"
        Copy-Item -Path $backupPath -Destination $settingsPath -Force
        Write-Warn "Restored from backup"
        $failCount++
    }

} catch {
    Write-Err "Settings beautification failed: $_"
    if ($backupPath -and (Test-Path $backupPath)) {
        Copy-Item -Path $backupPath -Destination $settingsPath -Force -ErrorAction SilentlyContinue
        Write-Warn "Restored from backup"
    }
    $failCount++
}

# ============================================================
#  Step 4/4: Verify All Configurations
# ============================================================
Write-Step "4/4" "Verify All Configurations"

$allPassed = $true

# Verify 1: Default terminal registry
try {
    $regPath = "HKCU:\Console\%%Startup"
    $vConsole  = (Get-ItemProperty -Path $regPath -Name "DelegationConsole"  -ErrorAction Stop).DelegationConsole
    $vTerminal = (Get-ItemProperty -Path $regPath -Name "DelegationTerminal" -ErrorAction Stop).DelegationTerminal

    if ($vConsole -eq "{2EACA947-7F5F-4CFA-BA87-8F7FBEEFBE69}" -and
        $vTerminal -eq "{E12CFF52-A866-4C77-936F-DA6DE2EAA2D6}") {
        Write-OK "Default Terminal: Windows Terminal"
    } else {
        Write-Err "Default Terminal: verification failed (Console=$vConsole, Terminal=$vTerminal)"
        $allPassed = $false
    }
} catch {
    Write-Err "Default Terminal: registry read failed"
    $allPassed = $false
}

# Verify 2: Cascadia Code font
try {
    $fontRegPath = "HKCU:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
    $fontProps = Get-ItemProperty -Path $fontRegPath -ErrorAction Stop
    $cascadiaFonts = $fontProps.PSObject.Properties | Where-Object { $_.Name -like "Cascadia*" }

    if ($cascadiaFonts) {
        Write-OK "Cascadia Code Font: registered ($($cascadiaFonts.Count) variants)"
    } else {
        Write-Warn "Cascadia Code Font: not found in registry (may be system-installed)"
    }
} catch {
    Write-Err "Font verification: registry read failed"
    $allPassed = $false
}

# Verify 3: settings.json
try {
    $settingsPath = Join-Path $env:LOCALAPPDATA `
        "Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json"
    if (-not (Test-Path $settingsPath)) {
        $settingsPath = Join-Path $env:LOCALAPPDATA `
            "Packages\Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe\LocalState\settings.json"
    }

    $checkContent = Get-Content -Path $settingsPath -Raw -Encoding UTF8
    $checkJson    = $checkContent | ConvertFrom-Json

    $checks = @(
        @{ Name = "defaultProfile";      OK = [bool]$checkJson.defaultProfile },
        @{ Name = "Cascadia Code font";  OK = ($checkJson.profiles.defaults.font.face -eq "Cascadia Code") },
        @{ Name = "Font size 14";        OK = ($checkJson.profiles.defaults.font.size -eq 14) },
        @{ Name = "Acrylic enabled";     OK = ($checkJson.profiles.defaults.useAcrylic -eq $true) },
        @{ Name = "Opacity 80";          OK = ($checkJson.profiles.defaults.opacity -eq 80) },
        @{ Name = "Cursor bar";          OK = ($checkJson.profiles.defaults.cursorShape -eq "bar") },
        @{ Name = "Copy on select";      OK = ($checkJson.copyOnSelect -eq $true) },
        @{ Name = "Tabs in titlebar";    OK = ($checkJson.showTabsInTitlebar -eq $true) },
        @{ Name = "Equal tab width";     OK = ($checkJson.tabWidthMode -eq "equal") },
        @{ Name = "Campbell Powershell"; OK = ($checkJson.profiles.defaults.colorScheme -eq "Campbell Powershell") }
    )

    $passedChecks = ($checks | Where-Object { $_.OK }).Count
    $totalChecks  = $checks.Count

    foreach ($c in $checks) {
        if ($c.OK) {
            Write-Host "    [OK] $($c.Name)" -ForegroundColor Green
        } else {
            Write-Host "    [FAIL] $($c.Name)" -ForegroundColor Red
            $allPassed = $false
        }
    }

    if ($passedChecks -eq $totalChecks) {
        Write-OK "settings.json: all $totalChecks checks passed"
    } else {
        Write-Warn "settings.json: $passedChecks/$totalChecks passed"
    }

    if (Test-Path "$settingsPath.bak") {
        Write-Host "  Backup: $settingsPath.bak" -ForegroundColor DarkGray
    }

} catch {
    Write-Err "settings.json verification failed: $_"
    $allPassed = $false
}

# ============================================================
#  Final Report
# ============================================================
Write-Host ""
Write-Host ("=" * 50) -ForegroundColor DarkGray

if ($allPassed) {
    Write-Host ""
    Write-Host "  ALL DONE! Close and reopen Windows Terminal." -ForegroundColor Green
    Write-Host ""
    Write-Host "  Summary:" -ForegroundColor White
    Write-Host "    - Default Terminal : Windows Terminal" -ForegroundColor Gray
    Write-Host "    - Font             : Cascadia Code 14pt" -ForegroundColor Gray
    Write-Host "    - Background       : Acrylic 80% opacity" -ForegroundColor Gray
    Write-Host "    - Color Scheme     : Campbell Powershell" -ForegroundColor Gray
    Write-Host "    - Cursor           : Bar (blinking)" -ForegroundColor Gray
    if ($pwsh7Path) {
        Write-Host "    - Startup Profile  : PowerShell 7" -ForegroundColor Gray
    } else {
        Write-Host "    - Startup Profile  : Windows PowerShell (PS7 not found)" -ForegroundColor Gray
    }
    Write-Host "    - Backup           : settings.json.bak" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "  DONE with warnings. Check items marked [FAIL] above." -ForegroundColor Yellow
    Write-Host "  Backup: settings.json.bak" -ForegroundColor Yellow
}

Write-Host ""
Write-Host ("=" * 50) -ForegroundColor DarkGray
Write-Host ""

if ($Host.Name -eq "ConsoleHost") {
    Write-Host "Press any key to exit..." -ForegroundColor DarkGray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
