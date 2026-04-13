$ErrorActionPreference = 'Stop'
$tessUrl = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe"
$installer = "C:\tess_installer.exe"

Write-Host "Tesseract yuklanmoqda..."
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $tessUrl -OutFile $installer

Write-Host "Tesseract o'rnatilmoqda..."
Start-Process -FilePath $installer -ArgumentList "/SILENT" -Wait

$tessdata = "C:\Program Files\Tesseract-OCR\tessdata"
if (-Not (Test-Path $tessdata)) {
    New-Item -ItemType Directory -Force -Path $tessdata
}

Write-Host "Rus va O'zbek lug'atlari yuklanmoqda..."
Invoke-WebRequest -Uri "https://github.com/tesseract-ocr/tessdata_best/raw/main/rus.traineddata" -OutFile "$tessdata\rus.traineddata"
Invoke-WebRequest -Uri "https://github.com/tesseract-ocr/tessdata_best/raw/main/uzb.traineddata" -OutFile "$tessdata\uzb.traineddata"
Invoke-WebRequest -Uri "https://github.com/tesseract-ocr/tessdata_best/raw/main/uzb_cyrl.traineddata" -OutFile "$tessdata\uzb_cyrl.traineddata"

Write-Host "Yuklash va o'rnatish yakunlandi."
Remove-Item $installer -Force
