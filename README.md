# Lab1072

Project untuk menginstall audio dan vidio ditermunal, bisajiga mencari dan memutar music dari YouTube yang anda inginkan 
### peringatan !!!
tidakbisa memutar secara langsung 
## Cara install

```bash
git clone https://github.com/ghostshark1500-gif/Lab1072.git
cd Lab1072
cd install-iv
./iv.py -h


iv version-0.0.7

Menginstall audio dan video menjadi lebih mudah dengan iv.
Bisa memutar/install audio/video dari YouTube, TikTok, Instagram, Facebook, LK21.

OPTIONS
  -h   --help          bantuan
  -f   --format        format output
 AUDIO:
    [.mp3, .m4a, .opus, .aac, .wav]
  -a   --abr           kualitas audio [64,128,192 kbps] [default 128]

 VIDEO:
    [.mp4, .mkv, .avi, .mov, .wmv, .flv, .webm]
  -q   --quality       kualitas video [144p, 240p, 360p, 480p, 540p, 720p, 1080p]
  -l   --list-formats  tampilkan semua format
  -sr  --search        mencari audio/video interaktif
  --min-duration       durasi minimal (detik)
  --max-duration       durasi maksimal (detik)
  --max-results        jumlah hasil search [1-20] default 10

CONTO:
>>> iv -sr "lastchild" --max-results 10 --min-duration 3600
>>> iv -f mp4 -q 240p "link video"
>>> iv -a 64 "link audio" -p
>>> iv "link audio/video" (default mp3 128 kbps)






