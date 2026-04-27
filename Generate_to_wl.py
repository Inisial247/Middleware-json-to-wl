from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)

# Folder sesuai konfigurasi orthanc.json
WL_FOLDER = '/var/lib/orthanc/worklists/'

@app.route('/create-worklist', methods=['POST'])
def create_wl():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No JSON data received"}), 400
            
        tags = data.get('Tags', {})
        acc_number = tags.get('AccessionNumber', 'unknown')
        
        # Buat format teks untuk dump2dcm
        dump_content = f"""
(0008,0005) CS [ISO_IR 192]
(0010,0010) PN [{tags.get('PatientName', '')}]
(0010,0020) LO [{tags.get('PatientID', '')}]
(0010,0030) DA [{tags.get('PatientBirthDate', '')}]
(0010,0040) CS [{tags.get('PatientSex', '')}]
(0008,0050) SH [{acc_number}]
(0008,0090) PN [{tags.get('ReferringPhysicianName', 'DOKTER PENGIRIM')}]
(0008,0080) LO [RSU RIZKI AMALIA MEDIKA]
(0032,1060) LO [{tags.get('PemeriksaanName', 'RADIOLOGY STUDY')}]
(0040,0100) SQ # ScheduledProcedureStepSequence
  (fffe,e000) na
    (0040,0001) AE [RADIOLOGI_PACS]
    (0040,0002) DA [{today}]
    (0040,0003) TM [{now_time}]
    (0008,0060) CS [{tags.get('Modality', 'DX')}]
    (0040,0007) LO [{tags.get('PemeriksaanName', 'RADIOLOGY STUDY')}]
    (0040,0009) SH [{acc_number}]
  (fffe,e00d) na
(fffe,e0dd) na
"""
        # Path file
        txt_path = f"/tmp/{acc_number}.txt"
        wl_path = os.path.join(WL_FOLDER, f"{acc_number}.wl")

        # Pastikan folder tujuan ada
        if not os.path.exists(WL_FOLDER):
            os.makedirs(WL_FOLDER, exist_ok=True)

        # BARIS 46: Sekarang sudah masuk ke dalam blok try (4 spasi dari def)
        if os.path.exists(txt_path):
            os.remove(txt_path)

        with open(txt_path, "w") as f:
            f.write(dump_content)

        # Konversi ke .wl dengan penanganan error mendalam
        try:
            result = subprocess.run(
                ['/usr/bin/dump2dcm', txt_path, wl_path], 
                check=True, 
                capture_output=True, 
                text=True
            )
            if os.path.exists(wl_path):
                os.chmod(wl_path, 0o644)
            if os.path.exists(txt_path):
                os.remove(txt_path) 

            return jsonify({"status": "success", "ID": acc_number}), 200

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else "Gagal menjalankan dump2dcm"
            return jsonify({"status": "error", "message": error_msg}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)
