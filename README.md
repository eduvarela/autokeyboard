# Auto Keyboard

Aplicativo desktop para Windows, feito em Python com Tkinter, para automatizar o envio de teclas e atalhos. O app permite repetir uma tecla em intervalo fixo ou executar uma sequência de ações com atrasos individuais, tudo por uma interface gráfica estilo dashboard.

## Projeto

- Aplicação principal em `autokeyboard.py`
- Interface gráfica customizada inspirada no layout de `DESIGN.md`
- Suporte a `pt-BR` e `en` com troca de idioma em tempo real
- Idioma padrão definido automaticamente a partir do idioma do sistema
- Configuração persistida em `autokeyboard_config.json`
- Strings centralizadas em `strings.json`
- Assets visuais em `assets/`
- Script de build do executável em `build_exe.ps1`

## Recursos

- Repetição contínua de tecla ou atalho
- Sequência personalizada com múltiplas ações e atraso por passo
- Edição rápida da sequência pelo painel lateral
- Remoção de múltiplos itens selecionados na lista
- Reordenação de passos com mover para cima e para baixo
- Contagem inicial antes do início da automação
- Modo `scan code` para maior compatibilidade com jogos
- Perfil com nome editável direto no cabeçalho
- Importação e exportação de perfil em `.json`
- Troca de idioma por botão na barra superior
- Layout responsivo para janelas menores
- Ícone do app carregado a partir de `assets/icon.png`
- Suporte a moldura escura do Windows quando disponível

## Como executar

Use Python no Windows:

```powershell
python .\autokeyboard.py
```

## Como gerar o .exe

O projeto inclui um script para empacotar a aplicação com PyInstaller:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
```

O script:

- instala `pyinstaller` automaticamente se ele não estiver disponível
- gera um executável `--onefile`
- inclui `strings.json` no pacote
- inclui a pasta `assets/` no pacote
- usa `assets/icon.ico` como ícone do executável quando o arquivo existir

Saída esperada:

- `dist/AutoKeyboard.exe`

## Como testar

Validação de sintaxe:

```powershell
python -m py_compile autokeyboard.py test_autokeyboard.py
```

Testes automatizados:

```powershell
python -m unittest test_autokeyboard.py
```

## Exemplos de teclas e atalhos

- `A`
- `F6`
- `space`
- `enter`
- `tab`
- `ctrl+s`
- `ctrl+shift+s`
- `alt+tab`

## Arquivos principais

- `autokeyboard.py`: aplicação principal, interface e automação
- `build_exe.ps1`: script para gerar o executável `.exe`
- `strings.json`: traduções e textos da interface
- `autokeyboard_config.json`: configuração local salva automaticamente
- `assets/english.png`: botão de idioma inglês
- `assets/portuguese.png`: botão de idioma português
- `assets/icon.png`: ícone usado pela janela do aplicativo
- `assets/icon.ico`: ícone usado no executável gerado pelo PyInstaller
- `test_autokeyboard.py`: testes das rotinas de parsing, strings e helpers

## Comportamento no .exe

Quando executado como script Python:

- `strings.json` é lido da raiz do projeto
- `assets/` é lido da pasta do projeto
- `autokeyboard_config.json` é salvo na raiz do projeto

Quando executado como `.exe`:

- `strings.json` e `assets/` são carregados dos recursos empacotados
- `autokeyboard_config.json` é salvo ao lado do executável

## Observações

- O envio de teclas funciona para a janela que estiver em foco no Windows.
- Se a sequência tiver itens, ela tem prioridade sobre o campo de tecla única.
- Alguns jogos podem exigir o app executando como administrador.
- Mesmo com `scan code`, certos jogos com anti-cheat podem bloquear a automação.
- `autokeyboard_config.json` é arquivo local de usuário e não precisa ser versionado.
