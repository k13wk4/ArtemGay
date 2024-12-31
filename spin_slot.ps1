# Script: spin_wheel.ps1
# Настройки
$minEnergy = 2000 # Мин. энергия для продолжения
$multiplier = 5000 # Множитель для spinWheelOfFortune

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$tokenFile = Join-Path $scriptPath "query.txt"
$query = Get-Content -Path $tokenFile -Raw

$headers = @{
    "accept" = "application/json, text/plain, */*"
    "accept-language" = "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7"
    "content-type" = "application/json"
    "origin" = "https://boink.boinkers.co"
    "priority" = "u=1, i"
    "referer" = "https://boink.boinkers.co/sluts"
    "sec-ch-ua" = '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24", "Microsoft Edge WebView2";v="131"'
    "sec-ch-ua-mobile" = "?0"
    "sec-ch-ua-platform" = '"Windows"'
    "sec-fetch-dest" = "empty"
    "sec-fetch-mode" = "cors"
    "sec-fetch-site" = "same-origin"
    "user-agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
}

function Get-token {
    $url = "https://boink.boinkers.co/public/users/loginByTelegram?tgWebAppStartParam=boink241967995&p=android"
    $data = @{
        initDataString = $query
        sessionParams = @{}
    }
    $jsonData = $data | ConvertTo-Json
    $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $jsonData
    return $response.token
}

$ErrorActionPreference = 'Stop'

$token = Get-token
Write-Output "Token received successfully"

$headers["authorization"] = "$token"

while ($true) {
    try {
        $body = "{}"
        $response = Invoke-RestMethod -Uri "https://boink.boinkers.co/api/play/spinSlotMachine/$multiplier" -Method Post -Headers $headers -Body $body
        if ($response.userGameEnergy.energy) {
            if ($response.userGameEnergy.energy -lt $minEnergy) {
                Write-Output "Energy is minimally less $minEnergy. STOP."
                break
            }
            Write-Output "$($response.prize.prizeTypeName): $($response.prize.prizeValue). Energy Left: $($response.userGameEnergy.energy)"
        } else {
            Write-Output "The server response does not contain the expected data structure: $($response | ConvertTo-Json -Depth 100)"
        }
    } catch {
        Write-Output "Error response: $_"
    }
    Start-Sleep -Seconds 1
}