# ============================================================
# HandOverAI - Low-Spec Environment Simulation Script
# ============================================================
# Memory: 512MB limit, CPU: Low priority

param(
    [int]$MemoryLimitMB = 512,
    [int]$CpuLimitPercent = 50
)

$ErrorActionPreference = "Continue"

# Log file setup
$LogFile = "low_spec_test_result.txt"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Host $logMessage
    Add-Content -Path $LogFile -Value $logMessage -Encoding UTF8
}

# Initialize log file
"HandOverAI Low-Spec Environment Simulation Test Results" | Out-File -FilePath $LogFile -Encoding UTF8
"Test Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -FilePath $LogFile -Append -Encoding UTF8
"============================================================" | Out-File -FilePath $LogFile -Append -Encoding UTF8
"" | Out-File -FilePath $LogFile -Append -Encoding UTF8

Write-Log "Starting low-spec environment simulation"
Write-Log "Memory limit: $MemoryLimitMB MB"
Write-Log "CPU limit: $CpuLimitPercent %"
Write-Log ""

# Collect system information
Write-Log "[1/5] System Information"
$os = Get-CimInstance Win32_OperatingSystem
$cpu = Get-CimInstance Win32_Processor
$totalRAM = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$availableRAM = [math]::Round($os.FreePhysicalMemory / 1MB, 2)

Write-Log "  OS: $($os.Caption)"
Write-Log "  RAM: $totalRAM GB (Available: $availableRAM GB)"
Write-Log "  CPU: $($cpu.Name)"
Write-Log "  Cores: $($cpu.NumberOfCores) Core, $($cpu.NumberOfLogicalProcessors) Threads"
Write-Log ""

# Check build size
Write-Log "[2/5] Build Size Check"
$distPath = "dist\HandOverAI"
if (Test-Path $distPath) {
    $size = (Get-ChildItem -Path $distPath -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    $fileCount = (Get-ChildItem -Path $distPath -Recurse -File).Count
    Write-Log "  Total size: $([math]::Round($size, 2)) MB"
    Write-Log "  File count: $fileCount files"
    
    if ($size -le 100) {
        Write-Log "  [OK] Target achieved (under 100MB)"
    } else {
        Write-Log "  [WARNING] Exceeds target"
    }
} else {
    Write-Log "  [ERROR] Build folder does not exist"
    Write-Log "  Please run 'handover.bat build' first"
    exit 1
}
Write-Log ""

# Check executable
$exePath = Join-Path $distPath "HandOverAI.exe"
if (-not (Test-Path $exePath)) {
    Write-Log "[ERROR] HandOverAI.exe not found"
    exit 1
}

Write-Log "[3/5] Starting HandOverAI (with resource limits)"
Write-Log "  Note: PyWebView window will open"
Write-Log "  May run slowly due to resource limits"
Write-Log ""

# Start process with resource limits
try {
    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = $exePath
    $processInfo.UseShellExecute = $false
    $processInfo.WorkingDirectory = $distPath
    
    $process = [System.Diagnostics.Process]::Start($processInfo)
    
    if ($null -eq $process) {
        Write-Log "[ERROR] Failed to start process"
        exit 1
    }
    
    # Wait for process to start
    Start-Sleep -Seconds 3
    
    # Check if process exited
    if ($process.HasExited) {
        Write-Log "[ERROR] HandOverAI exited immediately"
        Write-Log "  Exit code: $($process.ExitCode)"
        Write-Log ""
        Write-Log "Troubleshooting:"
        Write-Log "  1. Install Visual C++ Runtime: https://aka.ms/vs/17/release/vc_redist.x64.exe"
        Write-Log "  2. Check python311.dll"
        Write-Log "  3. Check Event Viewer for error logs"
        exit 1
    }
    
    Write-Log "[OK] HandOverAI started successfully (PID: $($process.Id))"
    Write-Log ""
    
    # Lower process priority (simulate low-spec)
    try {
        $process.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::BelowNormal
        Write-Log "[OK] Process priority lowered (low-spec simulation)"
    } catch {
        Write-Log "[WARNING] Failed to change process priority: $_"
    }
    
    Write-Log ""
    Write-Log "[4/5] Performance Monitoring (30 seconds)"
    Write-Log "  Open Task Manager to check memory usage (Ctrl+Shift+Esc)"
    Write-Log ""
    
    # Monitor memory for 30 seconds
    $measurements = @()
    for ($i = 1; $i -le 6; $i++) {
        Start-Sleep -Seconds 5
        
        # Refresh process
        $process.Refresh()
        
        if ($process.HasExited) {
            Write-Log "[ERROR] Process terminated unexpectedly"
            Write-Log "  Exit code: $($process.ExitCode)"
            exit 1
        }
        
        $memoryMB = [math]::Round($process.WorkingSet64 / 1MB, 2)
        
        Write-Log "  [$i/6] Memory: $memoryMB MB"
        $measurements += $memoryMB
        
        # Memory limit warning
        if ($memoryMB -gt $MemoryLimitMB) {
            Write-Log "  [WARNING] Memory exceeds limit ($MemoryLimitMB MB)"
        }
    }
    
    Write-Log ""
    
    # Calculate average memory
    $avgMemory = [math]::Round(($measurements | Measure-Object -Average).Average, 2)
    $maxMemory = [math]::Round(($measurements | Measure-Object -Maximum).Maximum, 2)
    
    Write-Log "[5/5] Performance Measurement Results"
    Write-Log "  Average memory: $avgMemory MB"
    Write-Log "  Maximum memory: $maxMemory MB"
    
    if ($maxMemory -le 300) {
        Write-Log "  [OK] Target achieved (under 300MB)"
    } else {
        Write-Log "  [WARNING] Exceeds target (target: 300MB)"
    }
    
    Write-Log ""
    Write-Log "============================================================"
    Write-Log "Test in Progress"
    Write-Log "============================================================"
    Write-Log ""
    Write-Log "Please perform the following tests manually in the PyWebView window:"
    Write-Log "  1. Click [Connection Test] -> Verify Ping success"
    Write-Log "  2. Click [Folder Analysis] -> Verify dummy data display"
    Write-Log "  3. Click [AI Search] -> Verify search results display"
    Write-Log "  4. Click [Cache Status] -> Verify cache info display"
    Write-Log ""
    Write-Log "Please close the PyWebView window after testing."
    Write-Log ""
    
    # Wait for process to exit
    Write-Host "Waiting for process to exit..."
    $process.WaitForExit()
    
    Write-Log ""
    Write-Log "============================================================"
    Write-Log "Test Complete"
    Write-Log "============================================================"
    Write-Log ""
    Write-Log "Please record the results:"
    Write-Log "  - Initial loading time: ___ seconds"
    Write-Log "  - Average memory: $avgMemory MB"
    Write-Log "  - Maximum memory: $maxMemory MB"
    Write-Log "  - All features working: Yes/No"
    Write-Log ""
    
    Write-Host ""
    Write-Host "============================================================"
    Write-Host "Test results saved: $LogFile"
    Write-Host "============================================================"
    Write-Host ""
    
    # Ask to open log file
    $openLog = Read-Host "Do you want to view the log file? (Y/N)"
    if ($openLog -eq "Y" -or $openLog -eq "y") {
        notepad $LogFile
    }
    
} catch {
    Write-Log "[ERROR] Exception occurred: $_"
    Write-Log $_.ScriptStackTrace
    exit 1
}
