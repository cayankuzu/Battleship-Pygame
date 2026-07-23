# Battleship Pygame

Klasik deniz savaşı oyununu sürükle-bırak gemi yerleşimi, bilgisayar rakibi, animasyonlu isabet işaretleri ve ayrıntılı ses kontrolleriyle yeniden kuran bir Pygame projesi.

Oyuncu gemilerini 10×10 ızgaraya yerleştirir, ardından bilgisayarla dönüşümlü atış yapar. Oyun; isabet/ıskalama istatistiklerini, arka plan müziği oynatıcısını ve patlama, ateş ve su seslerini ayrı ayrı yönetir.

## Özellikler

- Fareyle gemi taşıma, döndürme ve ızgaraya yapıştırma
- Oyuncu ve rastgele hamle yapan bilgisayar rakibi
- İsabet/ıskalama animasyonları ve skor takibi
- MP3 oynatıcı arayüzü ile bağımsız SFX kontrolleri
- Türkçe, hücre hücre açıklanmış Colab defteri
- Tek dosyada çalıştırılabilir Python kaynak kodu

## Çalıştırma

```bash
python -m pip install -r requirements.txt
python battleship.py
```

Kod `assets/images` ve `assets/sounds` klasörlerini bekler. Telifli müzik dosyaları bu depoya dahil edilmemiştir; kendi ses dosyalarınızı kodda belirtilen adlarla ekleyebilirsiniz.

Colab sürümü: [Battleship Türkçe Açıklamalar](https://colab.research.google.com/drive/1eg8Icicn8qVi9wrtUO_9aO6OigZiDJYm?usp=sharing)

## Web sürümü

[Amiral Battı'yı tarayıcıda oyna](https://battleship-pygame.vercel.app/)

Web sürümü iki rastgele filo, bilgisayar rakibi, dönüşümlü atışlar ve gemi batırma durumlarını kurulum gerektirmeden çalıştırır.
