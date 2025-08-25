# QR Code Generator

Uma aplicação moderna em **Python** para gerar, visualizar e salvar QR Codes com interface gráfica baseada em `customtkinter`.

## Funcionalidades

- **Interface moderna** com `customtkinter`
- Geração de QR Codes para múltiplos tipos:
  - Texto
  - URL
  - Wi-Fi Manual
  - Wi-Fi automatico (pega automaticamente a rede atual)
  - Pix (via PyPix, com suporte a valores, alguns bancos podem não aceitar sem valor)
  - Geo localização
  - SMS
  - Email
- **Histórico de QR Codes** gerados
- **Salvar QR Codes** em imagem PNG
- **Copiar conteúdo** para área de transferência
- **Limpar campos**
- **Visualizar dados de Pix** antes de gerar
- QR Code renderizado em alta qualidade

## Como executar

1. Clone o repositório:

```bash
git clone git@github.com:Br-Gui/qrcode_generator.git
cd qrcode_generator
```

2. Crie um ambiente virtual e instale as dependências:

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

3. Execute o programa:

```bash
python main.py
```

## Dependências principais

- [qrcode[pil]](https://pypi.org/project/qrcode/)
- [Pillow](https://pypi.org/project/Pillow/)
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter)
- [pyperclip](https://pypi.org/project/pyperclip/)
- [PyPix](https://pypi.org/project/pypix/)

Instale todas via:

```bash
pip install -r requirements.txt
```

## Licença

Este projeto é de uso livre para estudos e melhorias. Pull requests são bem-vindos!
