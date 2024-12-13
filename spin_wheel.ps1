# Script: spinWheelOfFortune.ps1
# Настройки
$minEnergy = 10000 # Мин. энергия для продолжения
$multiplier = 10 # Множитель для spinWheelOfFortune

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$tokenFile = Join-Path $scriptPath "token.txt"
$token = Get-Content -Path $tokenFile -Raw

$headers = @{
    "accept" = "application/json, text/plain, */*"
    "accept-language" = "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7"
    "authorization" = "$token"
    "content-type" = "application/json"
    "origin" = "https://boink.boinkers.co"
    "priority" = "u=1, i"
    "referer" = "https://boink.boinkers.co/daily-wheel"
    "sec-ch-ua" = "`"Microsoft Edge`";v=`"131`", `"Chromium`";v=`"131`", `"Not_A Brand`";v=`"24`", `"Microsoft Edge WebView2`";v=`"131`""
    "sec-ch-ua-mobile" = "?0"
    "sec-ch-ua-platform" = "`"Windows`""
    "sec-fetch-dest" = "empty"
    "sec-fetch-mode" = "cors"
    "sec-fetch-site" = "same-origin"
    "user-agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
}

function Get-LiveOpId {
    $url = "https://boink.boinkers.co/public/data/config"
	
	$headers = @{
		"accept" = "application/json, text/plain, */*"
		"accept-language" = "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7"
		"content-type" = "application/json"
		"origin" = "https://boink.boinkers.co"
		"priority" = "u=1, i"
		"referer" = "https://boink.boinkers.co/daily-wheel"
		"sec-ch-ua" = '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24", "Microsoft Edge WebView2";v="131"'
		"sec-ch-ua-mobile" = "?0"
		"sec-ch-ua-platform" = '"Windows"'
		"sec-fetch-dest" = "empty"
		"sec-fetch-mode" = "cors"
		"sec-fetch-site" = "same-origin"
		"user-agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
	}
    $response = Invoke-RestMethod -Uri $url -Method Get -Headers $headers
     $configId = $response.liveOps | Where-Object { 
            $_.mainButtonOverrides -and 
            ($_.mainButtonOverrides.PSObject.Properties.Name -contains "wheelOfFortune") 
        } | Select-Object -ExpandProperty _id -First 1
    return $configId
}

# Получение liveOpId
$liveOpId = Get-LiveOpId
Write-Output "$liveOpId"

$body = @"
{"liveOpId":"$liveOpId"}
"@
Write-Output "$body"

while ($true) {
    try {
        $response = Invoke-RestMethod -Uri "https://boink.boinkers.co/api/play/spinWheelOfFortune/$multiplier" -Method Post -Headers $headers -Body $body
        if ($response -and $response.userGameEnergy -and $response.userGameEnergy.energy) {
            if ($response.userGameEnergy.energy -lt $minEnergy) {
                Write-Output "Energy left $minEnergy. stop."
                break
            }
            Write-Output "$($response.prize.prizeTypeName): $($response.prize.prizeValue) Energy Left $($response.userGameEnergy.energy)"
        } else {
            Write-Output "Ответ сервера не содержит ожидаемой структуры данных: $($response | ConvertTo-Json -Depth 100)"
        }
    } catch {
        Write-Output "Erorr response: $_"
    }
    Start-Sleep -Seconds 1
}
