# ==========================================
# Script di Test Automatico - Mock Generator
# ==========================================
$ErrorActionPreference = "Stop" # Si ferma se c'è un errore
$InputFile = "input.json"
$OutputDir = "test_results"

Write-Host "--- Inizio Test Suite Completa ---" -ForegroundColor Cyan

# 0. Verifica Input
if (-not (Test-Path $InputFile)) {
    Write-Error "ERRORE: Manca il file '$InputFile' nella root!"
}

# 1. Pulisce/Crea cartella output
if (Test-Path $OutputDir) { Remove-Item $OutputDir -Recurse -Force }
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
Write-Host "Cartella '$OutputDir' pulita e ricreata." -ForegroundColor Gray

# ---------------------------------------------------------
# TEST FORMATI BASE
# ---------------------------------------------------------

# 2. Test JSON
Write-Host "Testing JSON..." -NoNewline
python -m src.static_generator.__main_cli__ --schema $InputFile --count 5 --out "$OutputDir/test.json" --format json
Write-Host " OK" -ForegroundColor Green

# 3. Test CSV
Write-Host "Testing CSV..." -NoNewline
python -m src.static_generator.__main_cli__ --schema $InputFile --count 10 --out "$OutputDir/test.csv" --format csv
Write-Host " OK" -ForegroundColor Green

# 4. Test NDJSON
Write-Host "Testing NDJSON..." -NoNewline
python -m src.static_generator.__main_cli__ --schema $InputFile --count 20 --out "$OutputDir/test.ndjson" --format ndjson
Write-Host " OK" -ForegroundColor Green

# 5. Test SQL
Write-Host "Testing SQL..." -NoNewline
python -m src.static_generator.__main_cli__ --schema $InputFile --count 5 --out "$OutputDir/test.sql" --format sql --table-name TEST_TABLE
Write-Host " OK" -ForegroundColor Green

# ---------------------------------------------------------
# TEST AVANZATI
# ---------------------------------------------------------

# 6. Test Verbose (Log Debug)
Write-Host "Testing Verbose Mode..." -NoNewline
python -m src.static_generator.__main_cli__ --schema $InputFile --count 1 --out "$OutputDir/verbose_test.json" --format json --verbose
Write-Host " OK" -ForegroundColor Green

# 7. Test Determinismo (SEED)
Write-Host "Testing SEED (Determinismo)..." -NoNewline
$SeedVal = 12345
$FileA = "$OutputDir/seed_a.json"
$FileB = "$OutputDir/seed_b.json"

# Genera due volte con lo stesso seed
python -m src.static_generator.__main_cli__ --schema $InputFile --count 5 --seed $SeedVal --out $FileA --format json
python -m src.static_generator.__main_cli__ --schema $InputFile --count 5 --seed $SeedVal --out $FileB --format json

# Calcola l'hash dei file per vedere se sono identici
$HashA = Get-FileHash $FileA -Algorithm SHA256
$HashB = Get-FileHash $FileB -Algorithm SHA256

if ($HashA.Hash -eq $HashB.Hash) {
    Write-Host " OK (I file sono identici)" -ForegroundColor Green
} else {
    Write-Host " FALLITO!" -ForegroundColor Red
    Write-Error "ERRORE: I file generati con lo stesso seed ($SeedVal) sono diversi!"
}

# ---------------------------------------------------------
# CONCLUSIONE
# ---------------------------------------------------------
Write-Host "`n--- TUTTI I TEST COMPLETATI CON SUCCESSO! ---" -ForegroundColor Green
Write-Host "I file sono disponibili in: $PWD\$OutputDir"