# Auto Keyboard

Aplicativo desktop para Windows, feito em Python com Tkinter, para automatizar o envio de teclas e atalhos. O app permite repetir uma tecla em intervalo fixo ou executar uma sequência de ações com atrasos individuais, tudo por uma interface gráfica estilo dashboard.

## Projeto

- Aplicação principal em `autokeyboard.py`
- Interface gráfica customizada inspirada no layout de `DESIGN.md`
- Suporte a `pt-BR` e `en` com troca de idioma em tempo real
- Configuração persistida em `autokeyboard_config.json`
- Strings centralizadas em `strings.json`
- Assets visuais em `assets/`

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

## Como executar

Use Python no Windows:

```powershell
python .\autokeyboard.py
```

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
- `strings.json`: traduções e textos da interface
- `autokeyboard_config.json`: configuração local salva automaticamente
- `assets/english.png`: botão de idioma inglês
- `assets/portuguese.png`: botão de idioma português
- `test_autokeyboard.py`: testes das rotinas de parsing e validação

## Observações

- O envio de teclas funciona para a janela que estiver em foco no Windows.
- Se a sequência tiver itens, ela tem prioridade sobre o campo de tecla única.
- Alguns jogos podem exigir o app executando como administrador.
- Mesmo com `scan code`, certos jogos com anti-cheat podem bloquear a automação.
- `autokeyboard_config.json` é arquivo local de usuário e não precisa ser versionado.
