param(
    [switch]$ValidateOnly
)

Set-StrictMode -Version Latest

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$script:ConfigPath = Join-Path $PSScriptRoot 'autokeyboard_config.json'
$script:SequenceSteps = New-Object System.Collections.ArrayList
$script:PreparedSequence = @()
$script:PreparedSingle = ''
$script:PreparedInterval = 1000
$script:PreparedSequencePause = 1000
$script:CountdownRemaining = 0
$script:IsRunning = $false
$script:CurrentSequenceIndex = 0

function Convert-ToSendKeys {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Combo
    )

    $parts = @($Combo.Split('+', [System.StringSplitOptions]::RemoveEmptyEntries) | ForEach-Object { $_.Trim().ToLowerInvariant() } | Where-Object { $_ })
    if ($parts.Count -eq 0) {
        throw 'Informe ao menos uma tecla.'
    }

    $modifierPrefix = ''
    $mainToken = $null

    foreach ($part in $parts) {
        if ($part -eq 'ctrl' -or $part -eq 'control') {
            $modifierPrefix += '^'
            continue
        }
        if ($part -eq 'alt') {
            $modifierPrefix += '%'
            continue
        }
        if ($part -eq 'shift') {
            $modifierPrefix += '+'
            continue
        }

        if ($null -ne $mainToken) {
            throw "Use apenas uma tecla principal por atalho. Valor recebido: '$Combo'."
        }

        if ($part.Length -eq 1) {
            if ($part -cmatch '[a-z0-9]') {
                $mainToken = $part
                continue
            }

            switch ($part) {
                ' ' { $mainToken = ' '; continue }
                '.' { $mainToken = '.'; continue }
                ',' { $mainToken = ','; continue }
                '-' { $mainToken = '-'; continue }
                '/' { $mainToken = '/'; continue }
                ';' { $mainToken = ';'; continue }
                '=' { $mainToken = '='; continue }
                '[' { $mainToken = '['; continue }
                ']' { $mainToken = ']'; continue }
                "'" { $mainToken = "'"; continue }
                '\' { $mainToken = '\'; continue }
            }
        }

        switch ($part) {
            'space' { $mainToken = ' '; continue }
            'tab' { $mainToken = '{TAB}'; continue }
            'enter' { $mainToken = '{ENTER}'; continue }
            'return' { $mainToken = '{ENTER}'; continue }
            'esc' { $mainToken = '{ESC}'; continue }
            'escape' { $mainToken = '{ESC}'; continue }
            'backspace' { $mainToken = '{BACKSPACE}'; continue }
            'delete' { $mainToken = '{DELETE}'; continue }
            'del' { $mainToken = '{DELETE}'; continue }
            'insert' { $mainToken = '{INSERT}'; continue }
            'ins' { $mainToken = '{INSERT}'; continue }
            'home' { $mainToken = '{HOME}'; continue }
            'end' { $mainToken = '{END}'; continue }
            'pageup' { $mainToken = '{PGUP}'; continue }
            'pgup' { $mainToken = '{PGUP}'; continue }
            'pagedown' { $mainToken = '{PGDN}'; continue }
            'pgdn' { $mainToken = '{PGDN}'; continue }
            'left' { $mainToken = '{LEFT}'; continue }
            'right' { $mainToken = '{RIGHT}'; continue }
            'up' { $mainToken = '{UP}'; continue }
            'down' { $mainToken = '{DOWN}'; continue }
            'plus' { $mainToken = '{+}'; continue }
            'minus' { $mainToken = '-'; continue }
        }

        if ($part -match '^f([1-9]|1[0-9]|2[0-4])$') {
            $mainToken = '{' + $part.ToUpperInvariant() + '}'
            continue
        }

        throw "Tecla desconhecida: '$part'. Exemplos aceitos: A, F6, space, enter, ctrl+s."
    }

    if ([string]::IsNullOrEmpty($mainToken)) {
        throw 'O atalho precisa terminar com uma tecla principal.'
    }

    return $modifierPrefix + $mainToken
}

function Get-NonNegativeInt {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Value,
        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    $parsed = 0
    if (-not [int]::TryParse($Value, [ref]$parsed)) {
        throw "$Label precisa ser um numero inteiro."
    }

    if ($parsed -lt 0) {
        throw "$Label nao pode ser negativo."
    }

    return $parsed
}

function Save-Config {
    $payload = [pscustomobject]@{
        single_combo   = $singleComboTextBox.Text.Trim()
        interval_ms    = $intervalTextBox.Text.Trim()
        start_delay    = $startDelayTextBox.Text.Trim()
        sequence_pause = $sequencePauseTextBox.Text.Trim()
        sequence_steps = @(
            foreach ($step in $script:SequenceSteps) {
                [pscustomobject]@{
                    combo    = $step.Combo
                    delay_ms = $step.DelayMs
                }
            }
        )
    }

    $payload | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $script:ConfigPath -Encoding UTF8
}

function Load-Config {
    if (-not (Test-Path -LiteralPath $script:ConfigPath)) {
        return
    }

    try {
        $config = Get-Content -LiteralPath $script:ConfigPath -Raw | ConvertFrom-Json
    }
    catch {
        $statusLabel.Text = 'Nao foi possivel carregar a configuracao salva.'
        return
    }

    if ($null -ne $config.single_combo) {
        $singleComboTextBox.Text = [string]$config.single_combo
    }
    if ($null -ne $config.interval_ms) {
        $intervalTextBox.Text = [string]$config.interval_ms
    }
    if ($null -ne $config.start_delay) {
        $startDelayTextBox.Text = [string]$config.start_delay
    }
    if ($null -ne $config.sequence_pause) {
        $sequencePauseTextBox.Text = [string]$config.sequence_pause
    }

    $script:SequenceSteps.Clear() | Out-Null
    $sequenceListView.Items.Clear()

    foreach ($step in @($config.sequence_steps)) {
        $combo = [string]$step.combo
        if ([string]::IsNullOrWhiteSpace($combo)) {
            continue
        }

        $delayMs = 0
        [void][int]::TryParse([string]$step.delay_ms, [ref]$delayMs)
        Add-SequenceStepRecord -Combo $combo -DelayMs ([Math]::Max(0, $delayMs)) | Out-Null
    }
}

function Update-ModeHint {
    if ($script:SequenceSteps.Count -gt 0) {
        $modeHintLabel.Text = 'Modo atual: sequencia personalizada'
    }
    else {
        $modeHintLabel.Text = 'Modo atual: tecla unica'
    }
}

function Add-SequenceStepRecord {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Combo,
        [Parameter(Mandatory = $true)]
        [int]$DelayMs
    )

    $record = [pscustomobject]@{
        Combo   = $Combo
        DelayMs = $DelayMs
    }

    [void]$script:SequenceSteps.Add($record)

    $item = New-Object System.Windows.Forms.ListViewItem($Combo)
    [void]$item.SubItems.Add([string]$DelayMs)
    [void]$sequenceListView.Items.Add($item)
    Update-ModeHint
    return $record
}

function Refresh-SequenceList {
    $sequenceListView.Items.Clear()
    foreach ($step in $script:SequenceSteps) {
        $item = New-Object System.Windows.Forms.ListViewItem($step.Combo)
        [void]$item.SubItems.Add([string]$step.DelayMs)
        [void]$sequenceListView.Items.Add($item)
    }
    Update-ModeHint
}

function Get-SelectedSequenceIndex {
    if ($sequenceListView.SelectedIndices.Count -eq 0) {
        return $null
    }

    return [int]$sequenceListView.SelectedIndices[0]
}

function Show-Error {
    param(
        [string]$Message,
        [string]$Title = 'Erro'
    )

    [void][System.Windows.Forms.MessageBox]::Show(
        $Message,
        $Title,
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    )
}

function Add-StepFromEditor {
    $combo = $stepComboTextBox.Text.Trim()
    $delayMs = Get-NonNegativeInt -Value $stepDelayTextBox.Text.Trim() -Label 'Espera depois'
    [void](Convert-ToSendKeys -Combo $combo)
    Add-SequenceStepRecord -Combo $combo -DelayMs $delayMs | Out-Null
    Save-Config
    $stepComboTextBox.Text = ''
    $stepDelayTextBox.Text = '500'
    $statusLabel.Text = 'Passo adicionado na sequencia.'
}

function Update-StepFromEditor {
    $index = Get-SelectedSequenceIndex
    if ($null -eq $index) {
        [void][System.Windows.Forms.MessageBox]::Show('Selecione um passo para atualizar.', 'Atualizar passo')
        return
    }

    $combo = $stepComboTextBox.Text.Trim()
    $delayMs = Get-NonNegativeInt -Value $stepDelayTextBox.Text.Trim() -Label 'Espera depois'
    [void](Convert-ToSendKeys -Combo $combo)
    $script:SequenceSteps[$index] = [pscustomobject]@{
        Combo   = $combo
        DelayMs = $delayMs
    }
    Refresh-SequenceList
    Save-Config
    $statusLabel.Text = 'Passo atualizado.'
}

function Remove-SelectedStep {
    $index = Get-SelectedSequenceIndex
    if ($null -eq $index) {
        [void][System.Windows.Forms.MessageBox]::Show('Selecione um passo para remover.', 'Remover passo')
        return
    }

    $script:SequenceSteps.RemoveAt($index)
    Refresh-SequenceList
    Save-Config
    $statusLabel.Text = 'Passo removido.'
}

function Clear-SequenceSteps {
    $script:SequenceSteps.Clear() | Out-Null
    Refresh-SequenceList
    Save-Config
    $statusLabel.Text = 'Sequencia limpa. O app voltou para o modo de tecla unica.'
}

function Prepare-ExecutionPlan {
    $singleCombo = $singleComboTextBox.Text.Trim()
    $intervalMs = Get-NonNegativeInt -Value $intervalTextBox.Text.Trim() -Label 'Intervalo'
    $startDelay = Get-NonNegativeInt -Value $startDelayTextBox.Text.Trim() -Label 'Contagem inicial'
    $sequencePause = Get-NonNegativeInt -Value $sequencePauseTextBox.Text.Trim() -Label 'Pausa apos sequencia'

    if ($script:SequenceSteps.Count -gt 0) {
        $prepared = @()
        foreach ($step in $script:SequenceSteps) {
            $prepared += [pscustomobject]@{
                Combo    = $step.Combo
                DelayMs  = [int]$step.DelayMs
                SendKeys = Convert-ToSendKeys -Combo $step.Combo
            }
        }

        return [pscustomobject]@{
            SingleCombo   = $singleCombo
            IntervalMs    = $intervalMs
            StartDelay    = $startDelay
            SequencePause = $sequencePause
            Sequence      = $prepared
        }
    }

    $singlePrepared = Convert-ToSendKeys -Combo $singleCombo
    return [pscustomobject]@{
        SingleCombo   = $singleCombo
        IntervalMs    = $intervalMs
        StartDelay    = $startDelay
        SequencePause = $sequencePause
        Sequence      = @()
        SingleSendKey = $singlePrepared
    }
}

function Set-RunningState {
    param(
        [bool]$Running
    )

    $script:IsRunning = $Running
    $startButton.Enabled = -not $Running
    $stopButton.Enabled = $Running
}

function Stop-Automation {
    $countdownTimer.Stop()
    $sendTimer.Stop()
    $script:CurrentSequenceIndex = 0
    Set-RunningState -Running $false
    $statusLabel.Text = 'Automacao parada.'
}

function Start-AutomationCore {
    if ($script:PreparedSequence.Count -gt 0) {
        $statusLabel.Text = 'Sequencia em execucao. Coloque a janela alvo em foco.'
        $script:CurrentSequenceIndex = 0
        $sendTimer.Interval = 1
        $sendTimer.Start()
    }
    else {
        $statusLabel.Text = "Tecla '$($singleComboTextBox.Text.Trim())' em repeticao."
        $sendTimer.Interval = [Math]::Max(1, $script:PreparedInterval)
        $sendTimer.Start()
    }
}

if ($ValidateOnly) {
    [void](Convert-ToSendKeys -Combo 'ctrl+shift+s')
    [void](Get-NonNegativeInt -Value '100' -Label 'Intervalo')
    Write-Output 'validate-ok'
    exit 0
}

$form = New-Object System.Windows.Forms.Form
$form.Text = 'Auto Keyboard'
$form.StartPosition = 'CenterScreen'
$form.Size = New-Object System.Drawing.Size(900, 640)
$form.MinimumSize = New-Object System.Drawing.Size(900, 640)
$form.BackColor = [System.Drawing.ColorTranslator]::FromHtml('#f3efe7')
$form.Font = New-Object System.Drawing.Font('Segoe UI', 10)

$titleLabel = New-Object System.Windows.Forms.Label
$titleLabel.Text = 'Auto Keyboard'
$titleLabel.Font = New-Object System.Drawing.Font('Segoe UI Semibold', 20)
$titleLabel.Location = New-Object System.Drawing.Point(20, 16)
$titleLabel.AutoSize = $true
$form.Controls.Add($titleLabel)

$subtitleLabel = New-Object System.Windows.Forms.Label
$subtitleLabel.Text = 'Configure uma tecla repetida ou uma sequencia de atalhos. Depois de iniciar, troque o foco para a janela desejada durante a contagem.'
$subtitleLabel.Location = New-Object System.Drawing.Point(24, 54)
$subtitleLabel.Size = New-Object System.Drawing.Size(830, 42)
$subtitleLabel.ForeColor = [System.Drawing.ColorTranslator]::FromHtml('#6d5f50')
$form.Controls.Add($subtitleLabel)

$quickGroup = New-Object System.Windows.Forms.GroupBox
$quickGroup.Text = 'Execucao rapida'
$quickGroup.Location = New-Object System.Drawing.Point(20, 100)
$quickGroup.Size = New-Object System.Drawing.Size(390, 190)
$quickGroup.Anchor = 'Top,Left'
$form.Controls.Add($quickGroup)

$singleComboLabel = New-Object System.Windows.Forms.Label
$singleComboLabel.Text = 'Tecla ou atalho'
$singleComboLabel.Location = New-Object System.Drawing.Point(18, 34)
$singleComboLabel.AutoSize = $true
$quickGroup.Controls.Add($singleComboLabel)

$singleComboTextBox = New-Object System.Windows.Forms.TextBox
$singleComboTextBox.Location = New-Object System.Drawing.Point(180, 30)
$singleComboTextBox.Size = New-Object System.Drawing.Size(180, 27)
$singleComboTextBox.Text = 'F6'
$quickGroup.Controls.Add($singleComboTextBox)

$intervalLabel = New-Object System.Windows.Forms.Label
$intervalLabel.Text = 'Intervalo (ms)'
$intervalLabel.Location = New-Object System.Drawing.Point(18, 70)
$intervalLabel.AutoSize = $true
$quickGroup.Controls.Add($intervalLabel)

$intervalTextBox = New-Object System.Windows.Forms.TextBox
$intervalTextBox.Location = New-Object System.Drawing.Point(180, 66)
$intervalTextBox.Size = New-Object System.Drawing.Size(180, 27)
$intervalTextBox.Text = '1000'
$quickGroup.Controls.Add($intervalTextBox)

$startDelayLabel = New-Object System.Windows.Forms.Label
$startDelayLabel.Text = 'Contagem inicial (s)'
$startDelayLabel.Location = New-Object System.Drawing.Point(18, 106)
$startDelayLabel.AutoSize = $true
$quickGroup.Controls.Add($startDelayLabel)

$startDelayTextBox = New-Object System.Windows.Forms.TextBox
$startDelayTextBox.Location = New-Object System.Drawing.Point(180, 102)
$startDelayTextBox.Size = New-Object System.Drawing.Size(180, 27)
$startDelayTextBox.Text = '3'
$quickGroup.Controls.Add($startDelayTextBox)

$sequencePauseLabel = New-Object System.Windows.Forms.Label
$sequencePauseLabel.Text = 'Pausa apos sequencia (ms)'
$sequencePauseLabel.Location = New-Object System.Drawing.Point(18, 142)
$sequencePauseLabel.AutoSize = $true
$quickGroup.Controls.Add($sequencePauseLabel)

$sequencePauseTextBox = New-Object System.Windows.Forms.TextBox
$sequencePauseTextBox.Location = New-Object System.Drawing.Point(180, 138)
$sequencePauseTextBox.Size = New-Object System.Drawing.Size(180, 27)
$sequencePauseTextBox.Text = '1000'
$quickGroup.Controls.Add($sequencePauseTextBox)

$hintLabel = New-Object System.Windows.Forms.Label
$hintLabel.Text = 'Exemplos: A, F6, space, enter, ctrl+s, alt+tab'
$hintLabel.Location = New-Object System.Drawing.Point(18, 168)
$hintLabel.AutoSize = $true
$hintLabel.ForeColor = [System.Drawing.ColorTranslator]::FromHtml('#6d5f50')
$quickGroup.Controls.Add($hintLabel)

$sequenceGroup = New-Object System.Windows.Forms.GroupBox
$sequenceGroup.Text = 'Sequencia personalizada'
$sequenceGroup.Location = New-Object System.Drawing.Point(430, 100)
$sequenceGroup.Size = New-Object System.Drawing.Size(430, 360)
$sequenceGroup.Anchor = 'Top,Left,Right,Bottom'
$form.Controls.Add($sequenceGroup)

$stepComboLabel = New-Object System.Windows.Forms.Label
$stepComboLabel.Text = 'Tecla ou atalho'
$stepComboLabel.Location = New-Object System.Drawing.Point(18, 32)
$stepComboLabel.AutoSize = $true
$sequenceGroup.Controls.Add($stepComboLabel)

$stepDelayLabel = New-Object System.Windows.Forms.Label
$stepDelayLabel.Text = 'Aguardar depois (ms)'
$stepDelayLabel.Location = New-Object System.Drawing.Point(226, 32)
$stepDelayLabel.AutoSize = $true
$sequenceGroup.Controls.Add($stepDelayLabel)

$stepComboTextBox = New-Object System.Windows.Forms.TextBox
$stepComboTextBox.Location = New-Object System.Drawing.Point(18, 56)
$stepComboTextBox.Size = New-Object System.Drawing.Size(188, 27)
$sequenceGroup.Controls.Add($stepComboTextBox)

$stepDelayTextBox = New-Object System.Windows.Forms.TextBox
$stepDelayTextBox.Location = New-Object System.Drawing.Point(230, 56)
$stepDelayTextBox.Size = New-Object System.Drawing.Size(180, 27)
$stepDelayTextBox.Text = '500'
$sequenceGroup.Controls.Add($stepDelayTextBox)

$addButton = New-Object System.Windows.Forms.Button
$addButton.Text = 'Adicionar'
$addButton.Location = New-Object System.Drawing.Point(18, 98)
$addButton.Size = New-Object System.Drawing.Size(92, 30)
$addButton.BackColor = [System.Drawing.ColorTranslator]::FromHtml('#1d6b57')
$addButton.ForeColor = [System.Drawing.Color]::White
$sequenceGroup.Controls.Add($addButton)

$updateButton = New-Object System.Windows.Forms.Button
$updateButton.Text = 'Atualizar'
$updateButton.Location = New-Object System.Drawing.Point(120, 98)
$updateButton.Size = New-Object System.Drawing.Size(92, 30)
$sequenceGroup.Controls.Add($updateButton)

$removeButton = New-Object System.Windows.Forms.Button
$removeButton.Text = 'Remover'
$removeButton.Location = New-Object System.Drawing.Point(222, 98)
$removeButton.Size = New-Object System.Drawing.Size(92, 30)
$sequenceGroup.Controls.Add($removeButton)

$clearButton = New-Object System.Windows.Forms.Button
$clearButton.Text = 'Limpar'
$clearButton.Location = New-Object System.Drawing.Point(324, 98)
$clearButton.Size = New-Object System.Drawing.Size(86, 30)
$sequenceGroup.Controls.Add($clearButton)

$sequenceListView = New-Object System.Windows.Forms.ListView
$sequenceListView.Location = New-Object System.Drawing.Point(18, 142)
$sequenceListView.Size = New-Object System.Drawing.Size(392, 198)
$sequenceListView.View = 'Details'
$sequenceListView.FullRowSelect = $true
$sequenceListView.GridLines = $true
$sequenceListView.MultiSelect = $false
$sequenceListView.HideSelection = $false
$sequenceListView.Anchor = 'Top,Left,Right,Bottom'
[void]$sequenceListView.Columns.Add('Tecla / atalho', 220)
[void]$sequenceListView.Columns.Add('Espera depois (ms)', 150)
$sequenceGroup.Controls.Add($sequenceListView)

$controlGroup = New-Object System.Windows.Forms.GroupBox
$controlGroup.Text = 'Controle'
$controlGroup.Location = New-Object System.Drawing.Point(20, 308)
$controlGroup.Size = New-Object System.Drawing.Size(390, 152)
$controlGroup.Anchor = 'Left,Bottom'
$form.Controls.Add($controlGroup)

$modeHintLabel = New-Object System.Windows.Forms.Label
$modeHintLabel.Text = 'Modo atual: tecla unica'
$modeHintLabel.Location = New-Object System.Drawing.Point(18, 34)
$modeHintLabel.AutoSize = $true
$controlGroup.Controls.Add($modeHintLabel)

$statusLabel = New-Object System.Windows.Forms.Label
$statusLabel.Text = 'Pronto para iniciar.'
$statusLabel.Location = New-Object System.Drawing.Point(18, 64)
$statusLabel.Size = New-Object System.Drawing.Size(240, 50)
$statusLabel.ForeColor = [System.Drawing.ColorTranslator]::FromHtml('#6d5f50')
$controlGroup.Controls.Add($statusLabel)

$startButton = New-Object System.Windows.Forms.Button
$startButton.Text = 'Iniciar'
$startButton.Location = New-Object System.Drawing.Point(270, 28)
$startButton.Size = New-Object System.Drawing.Size(95, 34)
$startButton.BackColor = [System.Drawing.ColorTranslator]::FromHtml('#1d6b57')
$startButton.ForeColor = [System.Drawing.Color]::White
$controlGroup.Controls.Add($startButton)

$stopButton = New-Object System.Windows.Forms.Button
$stopButton.Text = 'Parar'
$stopButton.Location = New-Object System.Drawing.Point(270, 74)
$stopButton.Size = New-Object System.Drawing.Size(95, 34)
$stopButton.Enabled = $false
$controlGroup.Controls.Add($stopButton)

$sendTimer = New-Object System.Windows.Forms.Timer
$countdownTimer = New-Object System.Windows.Forms.Timer
$countdownTimer.Interval = 1000

$singleComboTextBox.Add_Leave({ Save-Config })
$intervalTextBox.Add_Leave({ Save-Config })
$startDelayTextBox.Add_Leave({ Save-Config })
$sequencePauseTextBox.Add_Leave({ Save-Config })

$sequenceListView.Add_SelectedIndexChanged({
    $index = Get-SelectedSequenceIndex
    if ($null -eq $index) {
        return
    }

    $selected = $script:SequenceSteps[$index]
    $stepComboTextBox.Text = [string]$selected.Combo
    $stepDelayTextBox.Text = [string]$selected.DelayMs
})

$addButton.Add_Click({
    try {
        Add-StepFromEditor
    }
    catch {
        Show-Error -Message $_.Exception.Message -Title 'Sequencia invalida'
    }
})

$updateButton.Add_Click({
    try {
        Update-StepFromEditor
    }
    catch {
        Show-Error -Message $_.Exception.Message -Title 'Sequencia invalida'
    }
})

$removeButton.Add_Click({
    Remove-SelectedStep
})

$clearButton.Add_Click({
    Clear-SequenceSteps
})

$startButton.Add_Click({
    if ($script:IsRunning) {
        return
    }

    try {
        $plan = Prepare-ExecutionPlan
    }
    catch {
        Show-Error -Message $_.Exception.Message -Title 'Configuracao invalida'
        return
    }

    $script:PreparedSequence = @($plan.Sequence)
    $script:PreparedInterval = [int]$plan.IntervalMs
    $script:PreparedSequencePause = [int]$plan.SequencePause
    $script:PreparedSingle = if ($plan.PSObject.Properties.Name -contains 'SingleSendKey') { $plan.SingleSendKey } else { '' }
    $script:CurrentSequenceIndex = 0
    Save-Config
    Set-RunningState -Running $true

    if ([int]$plan.StartDelay -gt 0) {
        $script:CountdownRemaining = [int]$plan.StartDelay
        $statusLabel.Text = "Iniciando em $($script:CountdownRemaining)s. Troque o foco para a janela alvo."
        $countdownTimer.Start()
    }
    else {
        Start-AutomationCore
    }
})

$stopButton.Add_Click({
    Stop-Automation
})

$countdownTimer.Add_Tick({
    $script:CountdownRemaining--
    if ($script:CountdownRemaining -gt 0) {
        $statusLabel.Text = "Iniciando em $($script:CountdownRemaining)s. Troque o foco para a janela alvo."
        return
    }

    $countdownTimer.Stop()
    Start-AutomationCore
})

$sendTimer.Add_Tick({
    try {
        if ($script:PreparedSequence.Count -gt 0) {
            $step = $script:PreparedSequence[$script:CurrentSequenceIndex]
            [System.Windows.Forms.SendKeys]::SendWait($step.SendKeys)

            if ($script:CurrentSequenceIndex -ge ($script:PreparedSequence.Count - 1)) {
                $script:CurrentSequenceIndex = 0
                $sendTimer.Interval = [Math]::Max(1, $script:PreparedSequencePause)
            }
            else {
                $script:CurrentSequenceIndex++
                $sendTimer.Interval = [Math]::Max(1, [int]$step.DelayMs)
            }
        }
        else {
            [System.Windows.Forms.SendKeys]::SendWait($script:PreparedSingle)
            $sendTimer.Interval = [Math]::Max(1, $script:PreparedInterval)
        }
    }
    catch {
        Stop-Automation
        Show-Error -Message $_.Exception.Message -Title 'Falha ao enviar tecla'
    }
})

$form.Add_FormClosing({
    Stop-Automation
    Save-Config
})

Load-Config
Refresh-SequenceList
[void]$form.ShowDialog()
