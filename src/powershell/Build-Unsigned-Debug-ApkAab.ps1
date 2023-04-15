
function WriteLog ([string]$LogString){
    $Stamp = (Get-Date).toString("yyyy/MM/dd HH:mm:ss")
    $LogMessage = "$Stamp - $LogString"
    Write-Host $LogMessage
}

function Build-Unsigned-Debug-ApkAab ([string]$Name = '*') {
    # Enviroment Constants
    $java_home = $Env:JAVA_HOME

    WriteLog "Executando download do template react native..."
}

Build-Unsigned-Debug-ApkAab