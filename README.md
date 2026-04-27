
# Middleware-json-to-wl
sudo nano /etc/systemd/system/worklist-api.service
isi wordlist-api
[Unit]
Description=Python Worklist API for Orthanc
After=network.target

[Service]
User=user //sesuaikan
Group=user //sesuaikan
WorkingDirectory=/home/rsram/path/ke/script/anda
ExecStart=/usr/bin/python3 worklist_generat.py
Restart=always

[Install]
WantedBy=multi-user.target

//
sudo systemctl daemon-reload
sudo systemctl enable worklist-api
sudo systemctl start worklist-api
python3 worklist_generat.py
