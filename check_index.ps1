$dataDir = "c:\Users\tsuyoshi_tsuchiya\.gemini\antigravity\scratch\chart_rousoku_app\data"
$files = @('INDEX_BTC.js','INDEX_ETH.js','INDEX_WTI.js','INDEX_GOLD.js','INDEX_N225.js','INDEX_USDJPY.js','INDEX_EURJPY.js','INDEX_DJI.js','INDEX_GSPC.js','INDEX_IXIC.js','INDEX_TOPX.js')
foreach ($f in $files) {
    $path = Join-Path $dataDir $f
    $c = Get-Content $path -Raw
    $fa = "N/A"
    $cnt = "N/A"
    if ($c -match '"fetched_at":\s*"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})"') { $fa = $Matches[1] }
    if ($c -match '"count":\s*(\d+)') { $cnt = $Matches[1] }
    Write-Host ("{0,-22} fetched_at={1}  count={2}" -f $f, $fa, $cnt)
}
