# Read-only by default. Push/PR phases require separate explicit Founder authority.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidatePattern('^[a-f0-9]{40}$')][string]$ExpectedSHA,
    [Parameter(Mandatory)][string]$Python,
    [ValidateSet('Verify','Push','Runs','PR')][string]$Phase = 'Verify',
    [switch]$FounderPushAuthorized,
    [switch]$FounderPRAuthorized
)
$ErrorActionPreference = 'Stop'
$branch = 'release/m9-hosted-ci-20261112'
$dev = 'd8a5c0aa7ed845c31bd2ff40c1b3491246c6cf83'
$main = '1715b504e2041127056127ab5236a3248195a234'
function GitValue([string[]]$Arguments) {
    $value = & git @Arguments
    if ($LASTEXITCODE -ne 0) { throw 'Git verification failed' }
    return ($value -join "`n").Trim()
}
if ((GitValue -Arguments @('branch','--show-current')) -ne $branch) { throw 'Wrong validation branch' }
if ((GitValue -Arguments @('rev-parse','HEAD')) -ne $ExpectedSHA) { throw 'Unreviewed source SHA' }
if (GitValue -Arguments @('status','--porcelain=v1')) { throw 'Working tree is not clean' }
$origin = GitValue -Arguments @('remote','get-url','origin')
if ($origin -notin @('https://github.com/e-sall/KryptRoom.git','git@github.com:e-sall/KryptRoom.git')) { throw 'Unexpected origin' }
foreach ($item in @(@('dev',$dev),@('main',$main))) {
    $remote = GitValue -Arguments @('ls-remote','origin',"refs/heads/$($item[0])")
    if (($remote -split "`t")[0] -ne $item[1]) { throw 'Remote baseline changed; re-audit before publication' }
}
& git log --oneline "c2a8e7b8d30472297beecd4a2fdb08b512c62e46..$ExpectedSHA"
& git diff --stat "c2a8e7b8d30472297beecd4a2fdb08b512c62e46" $ExpectedSHA
& $Python -m unittest discover -s .github -p 'test_*.py' -v
if ($LASTEXITCODE -ne 0) { throw 'Local policy tests failed' }
$audit = Join-Path $env:TEMP "KryptRoom-M9-bootstrap-$ExpectedSHA.json"
& $Python .github/bootstrap_audit.py --source $ExpectedSHA --output $audit
if ($LASTEXITCODE -ne 0) { throw 'Workflow audit failed' }
$matrix = Get-Content -LiteralPath $audit -Raw | ConvertFrom-Json
$push = @($matrix.rows | Where-Object push_release)
if ($push.Count -ne 1 -or $push[0].file -ne '.github/workflows/m9-hosted-bootstrap.yml') { throw 'Unexpected first-push workflow' }
if ($Phase -eq 'Push') {
    if (-not $FounderPushAuthorized) { throw 'Separate Founder push authorization required' }
    if (GitValue -Arguments @('ls-remote','origin',"refs/heads/$branch")) { throw 'First-push branch already exists; do not overwrite it' }
    & git push origin "${ExpectedSHA}:refs/heads/$branch"
    if ($LASTEXITCODE -ne 0) { throw 'Push failed' }
}
if ($Phase -eq 'Runs' -or $Phase -eq 'PR') {
    & gh run list --repo e-sall/KryptRoom --branch $branch --commit $ExpectedSHA --event push --json databaseId,headSha,workflowName,url,status,conclusion
    if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect exact-head runs' }
}
if ($Phase -eq 'PR') {
    if (-not $FounderPRAuthorized) { throw 'Separate Founder PR authorization required; never merge automatically' }
    $remoteHead = GitValue -Arguments @('ls-remote','origin',"refs/heads/$branch")
    if (($remoteHead -split "`t")[0] -ne $ExpectedSHA) { throw 'Remote validation head changed' }
    Write-Warning 'Current PR scope is core=true: classification/refusal checks must remain red; crypto validation is still outstanding.'
    & gh pr create --repo e-sall/KryptRoom --base dev --head $branch --title 'M9 hosted CI bootstrap — diagnostic, release blocked' --body-file docs/m9/ci-bootstrap/PR-BODY.md
    if ($LASTEXITCODE -ne 0) { throw 'PR creation failed' }
}
Write-Output "Verification finished. Workflow matrix: $audit. No merge or deployment performed."
