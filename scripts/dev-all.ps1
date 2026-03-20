$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
& (Join-Path $root "start.ps1")
