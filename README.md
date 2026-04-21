# Auto Keyboard

Aplicativo desktop para Windows que pressiona teclas automaticamente em um intervalo definido ou executa uma sequencia de atalhos.

## Recursos

- Repeticao continua de uma tecla ou atalho.
- Sequencia personalizada com varias teclas e atrasos entre cada passo.
- Contagem inicial para dar tempo de focar a janela correta.
- Configuracao salva automaticamente em `autokeyboard_config.json`.
- Interface grafica nativa em Windows Forms, sem dependencias externas.

## Como executar

```powershell
powershell -ExecutionPolicy Bypass -File .\AutoKeyboard.ps1
```

## Exemplos de teclas

- `A`
- `F6`
- `space`
- `enter`
- `ctrl+s`
- `alt+tab`

## Observacoes

- O envio de teclas funciona para a janela que estiver em foco no Windows.
- Se houver itens na lista de sequencia, o app usa a sequencia e ignora o campo de tecla unica.
- O arquivo `autokeyboard.py` ficou no projeto como uma base alternativa em Python, mas a versao principal pronta para uso e `AutoKeyboard.ps1`.
