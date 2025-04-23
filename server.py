from flask import Flask, send_file
import os

app = Flask(__name__)

VIDEO_DIRECTORY = 'C:/Users/evely/Desktop/segments/'

@app.route('/manifest.mpd')
def manifest():
    try:
        return send_file('manifest.mpd', as_attachment=False)
    except FileNotFoundError:
        return 'Manifesto não encontrado.', 404


@app.route('/video/<qualidade>')
def video_segment(qualidade):
    try:
        # Ajustando o caminho para encontrar o arquivo segment.mp4 dentro da pasta da qualidade
        caminho_segmento = os.path.join(VIDEO_DIRECTORY, qualidade, 'segment.mp4')
        print(f"Tentando acessar o arquivo: {caminho_segmento}")
        return send_file(caminho_segmento, as_attachment=False)
    except FileNotFoundError:
        return f'Arquivo segment.mp4 não encontrado para qualidade {qualidade}.', 404

if __name__ == "__main__":
    app.run(debug=True)
