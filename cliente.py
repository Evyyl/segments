# -*- coding: utf-8 -*-
import requests
import time
import xml.etree.ElementTree as ET

MANIFEST_URL = "http://127.0.0.1:5000/manifest.mpd"
SEGMENTOS_BASE_URL = "http://127.0.0.1:5000/video/"

def baixar_manifesto():
    print("Baixando manifesto...")
    resposta = requests.get(MANIFEST_URL)
    resposta.raise_for_status()
    print(f"Manifesto baixado com sucesso: {len(resposta.content)} bytes.")
    return resposta.content

def medir_largura_de_banda(url_segmento_teste):
    print(f"Baixando segmento para medir a largura de banda de {url_segmento_teste}...")
    inicio = time.time()
    try:
        resposta = requests.get(url_segmento_teste)
        resposta.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"Erro ao baixar o segmento: {err}")
        return None
    fim = time.time()

    if resposta.status_code == 200:
        tamanho_bytes = len(resposta.content)
        duracao = fim - inicio
        print(f"Tamanho do arquivo: {tamanho_bytes} bytes")
        print(f"Duração do download: {duracao:.2f} segundos")
        if duracao > 0.1:
            largura_banda_bps = (tamanho_bytes * 8) / duracao
            largura_banda_mbps = largura_banda_bps / 1_000_000
            print(f"Largura de banda estimada: {largura_banda_mbps:.2f} Mbps")
            return largura_banda_mbps
        else:
            print("Tempo de download muito curto para medir a largura de banda corretamente.")
            return None
    else:
        print(f"Erro ao baixar o segmento: {resposta.status_code}")
        return None

def selecionar_qualidade(manifesto_bytes, largura_banda_mbps):
    print("Selecionando a melhor qualidade...")
    raiz = ET.fromstring(manifesto_bytes)
    namespace = {'ns': 'urn:mpeg:dash:schema:mpd:2011'}
    representacoes = raiz.findall(".//ns:Representation", namespace)

    melhor_repr = None
    melhor_bitrate = 0

    for repr in representacoes:
        bitrate = int(repr.attrib['bandwidth'])
        if bitrate <= largura_banda_mbps * 1_000_000 and bitrate > melhor_bitrate:
            melhor_bitrate = bitrate
            melhor_repr = repr

    if melhor_repr is not None:
        qualidade = melhor_repr.attrib['id']
        print(f"Qualidade selecionada: {qualidade} ({melhor_bitrate} bps)")
        return qualidade
    else:
        print("Nenhuma qualidade adequada foi encontrada para a largura de banda disponível.")
        return None

def baixar_video(url):
    print(f"Baixando vídeo de {url}...")
    try:
        resposta = requests.get(url)
        resposta.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"Erro ao baixar o vídeo: {err}")
        return

    qualidade = url.split("/")[-1]
    nome_arquivo = f"video_{qualidade}.mp4"
    
    with open(nome_arquivo, "wb") as f:
        f.write(resposta.content)
    
    print(f"Vídeo salvo como {nome_arquivo}")

def main():
    manifesto = baixar_manifesto()
    largura_banda = medir_largura_de_banda(SEGMENTOS_BASE_URL + "360p")

    if largura_banda is not None and largura_banda > 0:
        qualidade_escolhida = selecionar_qualidade(manifesto, largura_banda)
        if qualidade_escolhida:
            # Corrigido: agora é passada a URL completa
            baixar_video(SEGMENTOS_BASE_URL + qualidade_escolhida)
    else:
        print("Não foi possível medir a largura de banda ou ela é muito baixa.")

if __name__ == "__main__":
    main()
