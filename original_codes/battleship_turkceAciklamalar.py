# Battleship Oyunu, MP3 Oynatıcı ve SFX Ses Kontrolleri ile
# Bu kod, pygame kullanılarak Battleship oyununu uygular.
# Arka plan müziği içeren bir MP3 oynatıcı arayüzü ve ses efektleri (Splash, Explosion, Gunshot) için ayrı ses kontrolleri içerir.
# Her fonksiyon, sınıf ve bölüm basit Türkçe ile detaylı biçimde yorumlanmıştır.

import pygame, random, os  # pygame: oyun fonksiyonları; random: rastgele seçimler; os: dosya yolu işlemleri

# ---------------- BAŞLANGIÇ AYARLARI ---------------- #
pygame.init()  # Tüm pygame modüllerini başlat

# Bu scriptin bulunduğu temel dizini al (varlık dosyalarına mutlak yol oluşturmak için)
BASE_PATH = os.path.dirname(os.path.abspath(__file__))  # scriptin bulunduğu dizini al

# ---------------- GENEL DEĞİŞKENLER ---------------- #
# Genel oyun durumu değişkenleri (oyunun ilerleyişini ve sonuçlarını takip eder)

game_over = False              # Oyunun bittiğini belirten bayrak (False: oyun devam ediyor)
winner = ""                    # Kazananı ("Player" veya "Computer") tutacak, başlangıçta boş
overlay_buttons = []           # Oyun bittiğinde gösterilecek overlay düğmelerini saklamak için liste

# Oyuncu ve bilgisayar istatistikleri (atışlar, isabetler, ıskalamalar, batırılan gemiler, kalan gemiler)
player_stats = {               # İnsan oyuncusunun istatistikleri
    "shots": 0,               # Oyuncunun attığı atış sayısı (başlangıçta 0)
    "hits": 0,                # Oyuncunun isabet ettiği atış sayısı (başlangıçta 0)
    "misses": 0,              # Oyuncunun ıskaladığı atış sayısı (başlangıçta 0)
    "sunk": 0,                # Oyuncunun batırdığı düşman gemi sayısı (başlangıçta 0)
    "remaining": 0            # Oyuncunun kalan gemi sayısı (daha sonra belirlenecek)
}
computer_stats = {             # Bilgisayarın istatistikleri
    "shots": 0,               # Bilgisayarın attığı atış sayısı
    "hits": 0,                # Bilgisayarın isabet ettiği atış sayısı
    "misses": 0,              # Bilgisayarın ıskaladığı atış sayısı
    "sunk": 0,                # Bilgisayarın batırdığı oyuncu gemi sayısı
    "remaining": 0            # Bilgisayarın kalan gemi sayısı (daha sonra belirlenecek)
}

# ---------------- ARKA PLAN MÜZİĞİ AYARLARI ---------------- #
# Müzik parçalarının tam yolunu BASE_PATH kullanarak oluştur

bg_music_tracks = [  # Arka plan müziği parçalarının yollarını içeren liste
    os.path.join(BASE_PATH, "assets", "sounds", "Black_Sabbath__War_Pigs.mp3"),  # 1. parça yolu
    os.path.join(BASE_PATH, "assets", "sounds", "Iron_Maiden__The_Trooper.mp3"),    # 2. parça yolu
    os.path.join(BASE_PATH, "assets", "sounds", "Metallica__One.mp3"),              # 3. parça yolu
    os.path.join(BASE_PATH, "assets", "sounds", "Cannibal_Corpse__The_Time_To_Kill_Is_Now.mp3"),  # 4. parça yolu
    os.path.join(BASE_PATH, "assets", "sounds", "Megadeth __ Holy_Wars.mp3"),  # 5. parça yolu
    os.path.join(BASE_PATH, "assets", "sounds", "Megadeth__Symphony_Of_Destruction.mp3")  # 6. parça yolu
]

current_track_index = 0        # Şu anda çalan müzik parçasının indeksi (0: ilk parça)
music_paused = False           # Müzik duraklatıldı mı? (başlangıçta hayır)
normal_music_volume = 0.3      # Müzik için varsayılan ses seviyesi (0.0 ile 1.0 arası)
lowered_music_volume = 0.1     # Ses efekti çalındığında müzik sesinin geçici olarak düşürüleceği seviye
current_music_volume = normal_music_volume  # Mevcut müzik sesi, başlangıçta varsayılan ses seviyesi

# ---------------- SES EFEKTLERİ İÇİN SES SEVİYE DEĞİŞKENLERİ ---------------- #
# Her ses efekti için ayrı ses seviyesi değişkenleri

splash_volume = 0.05           # Splash (ıskalama) ses efekti için ses seviyesi
explosion_volume = 0.05        # Patlama ses efekti için ses seviyesi
gunshot_volume = 0.05          # Nişancı (gunshot) ses efekti için ses seviyesi

# ---------------- DÜĞMELER İÇİN GENEL SÖZLÜKLER ---------------- #
# SFX kontrol düğmelerini saklamak için sözlük tanımlıyoruz; bu, olay döngüsünde kullanılacak

sfx_buttons = {}  # SFX kontrol düğmelerini saklamak için boş sözlük

# ---------------- ÖZEL OLAYLAR ---------------- #
# Ses efekti çalındıktan sonra müzik sesini eski seviyeye getirmek için özel bir olay tanımlıyoruz

RESTORE_MUSIC_VOLUME = pygame.USEREVENT + 1  # Müzik sesini geri yüklemek için özel olay ID'si

# ---------------- MÜZİK KONTROL FONKSİYONLARI ---------------- #
def play_music():
    """Geçerli müzik parçasını yükle ve sonsuz döngüde çal."""  # Fonksiyonun amacı
    global music_paused  # Global music_paused değişkenini kullan
    try:
        pygame.mixer.music.load(bg_music_tracks[current_track_index])  # Şu anki müzik parçasını yükle
        pygame.mixer.music.play(-1)  # Parçayı sonsuz döngüde çal (-1: sürekli tekrar)
        pygame.mixer.music.set_volume(current_music_volume)  # Müzik sesini ayarla
        music_paused = False  # Müzik duraklatılmadı
    except pygame.error as e:  # Hata durumunda
        print(f"Müzik yüklenirken hata: {e}")  # Hata mesajını yazdır

def pause_music():
    """Arka plan müziğini duraklat."""  # Fonksiyonun amacı
    global music_paused  # Global music_paused değişkenini kullan
    pygame.mixer.music.pause()  # Müzik duraklat
    music_paused = True  # Müzik duraklatıldı

def unpause_music():
    """Arka plan müziğini devam ettir (duraklatmayı kaldır)."""  # Fonksiyonun amacı
    global music_paused  # Global music_paused değişkenini kullan
    pygame.mixer.music.unpause()  # Müzik devam etsin
    music_paused = False  # Müzik duraklatılmadı

def next_track():
    """Bir sonraki müzik parçasına geç ve çal."""  # Fonksiyonun amacı
    global current_track_index  # Global müzik parçası indeksini kullan
    current_track_index = (current_track_index + 1) % len(bg_music_tracks)  # İndeksi döngüsel olarak artır
    try:
        pygame.mixer.music.load(bg_music_tracks[current_track_index])  # Sonraki parçayı yükle
        pygame.mixer.music.play(-1)  # Sonsuz döngüde çal
        pygame.mixer.music.set_volume(current_music_volume)  # Müzik sesini ayarla
    except pygame.error as e:  # Hata durumunda
        print(f"Sonraki parça yüklenirken hata: {e}")  # Hata mesajını yazdır

def prev_track():
    """Önceki müzik parçasına dön ve çal."""  # Fonksiyonun amacı
    global current_track_index  # Global müzik parçası indeksini kullan
    current_track_index = (current_track_index - 1) % len(bg_music_tracks)  # İndeksi döngüsel olarak azalt
    try:
        pygame.mixer.music.load(bg_music_tracks[current_track_index])  # Önceki parçayı yükle
        pygame.mixer.music.play(-1)  # Sonsuz döngüde çal
        pygame.mixer.music.set_volume(current_music_volume)  # Müzik sesini ayarla
    except pygame.error as e:  # Hata durumunda
        print(f"Önceki parça yüklenirken hata: {e}")  # Hata mesajını yazdır

def select_track(index):
    """Belirtilen indeksli müzik parçasını seç ve çal."""  # Fonksiyonun amacı
    global current_track_index  # Global müzik parçası indeksini kullan
    if 0 <= index < len(bg_music_tracks):  # İndeks geçerliyse
        current_track_index = index  # Geçerli indeksi ayarla
        try:
            pygame.mixer.music.load(bg_music_tracks[current_track_index])  # Seçilen parçayı yükle
            pygame.mixer.music.play(-1)  # Sonsuz döngüde çal
            pygame.mixer.music.set_volume(current_music_volume)  # Müzik sesini ayarla
        except pygame.error as e:  # Hata durumunda
            print(f"{index} indeksli parça seçilirken hata: {e}")  # Hata mesajını yazdır

def play_effect(sound):
    """
    Ses efekti çalındığında müzik sesini geçici olarak düşürür.
    500ms sonra müzik sesi eski haline getirilir.
    """  # Fonksiyonun amacı
    pygame.mixer.music.set_volume(lowered_music_volume)  # Müzik sesini düşür
    sound.play()  # Verilen ses efektini çal
    pygame.time.set_timer(RESTORE_MUSIC_VOLUME, 500)  # 500ms sonra müzik sesini geri yüklemek için zamanlayıcı ayarla

# ---------------- OYUN NESNE SINIFLARI ---------------- #
class Ship:
    """Battleship oyunundaki bir gemiyi temsil eder."""  # Sınıfın amacı
    def __init__(self, name, img, pos, size):
        self.name = name  # Geminin adını sakla (örneğin, "battleship")
        self.pos = pos  # Varsayılan başlangıç konumunu (x, y) sakla
        self.verticalImage = loadImage(img, size)  # Geminin dikey görüntüsünü yükle
        self.verticalImageWidth = self.verticalImage.get_width()  # Dikey görüntünün genişliğini al
        self.verticalImageHeight = self.verticalImage.get_height()  # Dikey görüntünün yüksekliğini al
        self.verticalImageRect = self.verticalImage.get_rect()  # Dikey görüntünün dikdörtgenini (hitbox) al
        self.verticalImageRect.topleft = pos  # Dikdörtgenin sol üst köşesini varsayılan konuma ayarla
        self.horizontalImage = pygame.transform.rotate(self.verticalImage, -90)  # Dikey görüntüyü -90 derece döndürerek yatay görüntüyü oluştur
        self.horizontalImageWidth = self.horizontalImage.get_width()  # Yatay görüntünün genişliğini al
        self.horizontalImageHeight = self.horizontalImage.get_height()  # Yatay görüntünün yüksekliğini al
        self.horizontalImageRect = self.horizontalImage.get_rect()  # Yatay görüntünün dikdörtgenini al
        self.horizontalImageRect.topleft = pos  # Yatay görüntünün sol üst köşesini varsayılan konuma ayarla
        self.image = self.verticalImage  # Başlangıçta mevcut görüntüyü dikey görüntü olarak ayarla
        self.rect = self.verticalImageRect  # Başlangıçta hitbox olarak dikey dikdörtgeni kullan
        self.rotation = False  # Geminin dönüş durumunu belirten bayrak (False: dikey, True: yatay)
        self.active = False  # Geminin oyuncu tarafından seçilip hareket ettirilip ettirilmediğini belirten bayrak
        self.occupiedCells = []  # Geminin yerleştirildiği grid hücrelerini saklar
        self.hitCells = []  # Gemide vurulan grid hücrelerini saklar
        self.sunk = False  # Geminin batıp batmadığını belirten bayrak

    def draw(self, window):
        """Gemiyi oyun penceresinde çizer."""  # Metot açıklaması
        window.blit(self.image, self.rect)  # Mevcut görüntüyü, hitbox konumunda pencereye çiz
        pygame.draw.rect(window, (255, 0, 0), self.rect, 1)  # İsteğe bağlı olarak geminin etrafına kırmızı kenarlık çiz

    def selectShipAndMove(self):
        """
        Oyuncunun fare ile gemiyi seçip hareket ettirmesine izin verir.
        Gemi, yerleştirilene (sol tıklama) veya döndürülene (sağ tıklama) kadar fareyi takip eder.
        """  # Metot açıklaması
        while self.active:  # Gemi aktif olduğu sürece döngüye gir
            self.rect.center = pygame.mouse.get_pos()  # Geminin merkezini fare imlecinin konumuna ayarla
            updateGameScreen(GAME_SCREEN)  # Güncellenmiş konumla ekranı yeniden çiz
            for event in pygame.event.get():  # Hareket sırasında oluşan olayları işle
                if event.type == pygame.MOUSEBUTTONDOWN:  # Fare tıklama olayı varsa
                    if not self.checkForCollisions(playerFleet):  # Geminin diğerleriyle çakışmadığını kontrol et
                        if event.button == 1:  # Sol fare düğmesine tıklandığında
                            self.horizontalImageRect.center = self.verticalImageRect.center = self.rect.center  # Her iki görüntünün merkezini hizala
                            self.active = False  # Gemiyi yerleştir (aktifliği sonlandır)
                    if event.button == 3:  # Sağ fare düğmesine tıklandığında
                        self.rotateShip()  # Gemiyi döndür

    def rotateShip(self, doRotation=False):
        """
        Gemiyi dikey ve yatay konum arasında döndürür.
        doRotation True ise, gemi aktif olmasa bile döndür.
        """  # Metot açıklaması
        if self.active or doRotation:  # Geminin aktif olması veya zorla döndürme
            self.rotation = not self.rotation  # Döndürme bayrağını tersine çevir
            self.switchImageAndRect()  # Yeni yönelim için görüntü ve dikdörtgeni güncelle

    def switchImageAndRect(self):
        """
        Döndürme durumuna göre mevcut görüntüyü ve dikdörtgeni değiştirir.
        Bu, geminin merkezinin sabit kalmasını sağlar.
        """  # Metot açıklaması
        if self.rotation:  # Eğer gemi yatay konumdaysa
            self.image = self.horizontalImage  # Mevcut görüntüyü yatay görüntü olarak ayarla
            self.rect = self.horizontalImageRect  # Hitbox olarak yatay dikdörtgeni kullan
        else:  # Eğer gemi dikey konumdaysa
            self.image = self.verticalImage  # Mevcut görüntüyü dikey görüntü olarak ayarla
            self.rect = self.verticalImageRect  # Hitbox olarak dikey dikdörtgeni kullan
        self.horizontalImageRect.center = self.verticalImageRect.center = self.rect.center  # Her iki görüntünün merkezlerini eşitle

    def checkForCollisions(self, shipList):
        """
        Bu geminin, verilen gemi listesiyle çakışıp çakışmadığını kontrol eder.
        Çakışma varsa True döndürür.
        """  # Metot açıklaması
        sList = shipList.copy()  # Orijinal listeyi değiştirmemek için kopyasını oluştur
        sList.remove(self)  # Bu gemiyi kontrol dışı bırak
        for item in sList:  # Diğer gemiler üzerinde döngü
            if self.rect.colliderect(item.rect):  # Eğer bu geminin dikdörtgeni başka bir geminin dikdörtgeniyle çakışıyorsa
                return True  # Çakışma var, True döndür
        return False  # Hiçbir çakışma yoksa False döndür

    def returnToDefaultPosition(self):
        """Gemiyi varsayılan başlangıç konumuna geri döndürür."""  # Metot açıklaması
        if self.rotation:  # Eğer gemi döndürülmüşse
            self.rotateShip(True)  # Zorla dikey konuma döndür
        self.rect.topleft = self.pos  # Dikdörtgenin sol üst köşesini varsayılan konuma ayarla
        self.horizontalImageRect.center = self.verticalImageRect.center = self.rect.center  # Merkezleri yeniden hizala

    def snapToGrid(self, gridCoords):
        """
        Geminin konumunu en yakın grid hücresine yapıştırır.
        Ayrıca, geminin işgal ettiği hücrelerin listesini günceller.
        """  # Metot açıklaması
        for i, row in enumerate(gridCoords):  # Grid'deki her satır için döngü
            for j, cell in enumerate(row):  # Satırdaki her hücre için döngü
                # Geminin sol ve üst kenarının, hücre sınırları içinde olup olmadığını kontrol et
                if (self.rect.left >= cell[0] and self.rect.left < cell[0] + CELL_SIZE and
                    self.rect.top >= cell[1] and self.rect.top < cell[1] + CELL_SIZE):
                    if not self.rotation:  # Eğer gemi dikey konumdaysa
                        self.rect.topleft = (cell[0] + (CELL_SIZE - self.image.get_width()) // 2, cell[1])  # Hücre içinde yatay olarak ortala
                        cell_count = max(1, round(self.verticalImage.get_height() / CELL_SIZE))  # Geminin kaç hücre kapladığını hesapla
                        self.occupiedCells = [(i + k, j) for k in range(cell_count) if i + k < len(gridCoords)]  # İşgal edilen hücreleri kaydet
                    else:  # Eğer gemi yatay konumdaysa
                        self.rect.topleft = (cell[0], cell[1] + (CELL_SIZE - self.image.get_height()) // 2)  # Hücre içinde dikey olarak ortala
                        cell_count = max(1, round(self.horizontalImage.get_width() / CELL_SIZE))  # Geminin kaç hücre kapladığını hesapla
                        self.occupiedCells = [(i, j + k) for k in range(cell_count) if j + k < len(row)]  # İşgal edilen hücreleri kaydet
                    self.horizontalImageRect.center = self.verticalImageRect.center = self.rect.center  # Her iki görüntünün merkezlerini yeniden hizala
                    return  # Gemiyi yapıştırdıktan sonra döngüden çık

    def snapToGridEdge(self, gridCoords):
        """
        Geminin grid sınırları içinde kalmasını sağlar.
        Eğer gemi grid dışında ise, varsayılan konumuna geri döner.
        """  # Metot açıklaması
        if self.rect.topleft != self.pos:  # Eğer gemi varsayılan konumdan farklıysa
            if (self.rect.left > gridCoords[0][-1][0] + CELL_SIZE or
                self.rect.right < gridCoords[0][0][0] or
                self.rect.top > gridCoords[-1][0][1] + CELL_SIZE or
                self.rect.bottom < gridCoords[0][0][1]):
                self.returnToDefaultPosition()  # Gemiyi varsayılan konuma döndür
            elif self.rect.right > gridCoords[0][-1][0] + CELL_SIZE:  # Eğer gemi sağa taşmışsa
                self.rect.right = gridCoords[0][-1][0] + CELL_SIZE  # Sağ kenarı gridin sağına hizala
            elif self.rect.left < gridCoords[0][0][0]:  # Eğer gemi sola taşmışsa
                self.rect.left = gridCoords[0][0][0]  # Sol kenarı gridin soluna hizala
            elif self.rect.top < gridCoords[0][0][1]:  # Eğer gemi yukarı taşmışsa
                self.rect.top = gridCoords[0][0][1]  # Üst kenarı gridin üstüne hizala
            elif self.rect.bottom > gridCoords[-1][0][1] + CELL_SIZE:  # Eğer gemi aşağı taşmışsa
                self.rect.bottom = gridCoords[-1][0][1] + CELL_SIZE  # Alt kenarı gridin altına hizala
            self.verticalImageRect.center = self.horizontalImageRect.center = self.rect.center  # Merkezleri yeniden hizala
            self.snapToGrid(gridCoords)  # Gemiyi tekrar grid'e yapıştır

class Button:
    """Oyun arayüzündeki etkileşimli düğmeyi temsil eder."""  # Sınıfın amacı
    def __init__(self, image, size, pos, msg):
        self.name = msg  # Düğme adını sakla (aynı zamanda etiket olarak kullanılır)
        self.image = image  # Düğmenin temel görüntüsünü sakla
        self.imageLarger = pygame.transform.scale(self.image, (size[0] + 10, size[1] + 10))  # Fare üzerine gelindiğinde gösterilecek daha büyük görüntüyü oluştur
        self.rect = self.image.get_rect()  # Düğmenin dikdörtgenini (konum ve boyut) al
        self.rect.topleft = pos  # Dikdörtgenin sol üst köşesini verilen konuma ayarla
        self.active = False  # Düğmenin aktif olup olmadığını belirten bayrak (bu kodda kullanılmasa da ileride kullanılabilir)
        self.msg = self.addText(msg)  # Düğme üzerindeki metni oluşturmak için addText metodunu çağır
        self.msgRect = self.msg.get_rect(center=self.rect.center)  # Metni düğme dikdörtgeninin ortasına hizala

    def addText(self, msg):
        """Düğme metnini basit bir font kullanarak render eder."""  # Metot açıklaması
        font = pygame.font.SysFont("Stencil", 22)  # "Stencil" fontunu 22 punto ile seç
        message = font.render(msg, True, (255, 255, 255))  # Metni beyaz renkte render et
        return message  # Render edilmiş metni döndür

    def draw(self, window):
        """Düğmeyi (görüntü ve metin) pencereye çizer."""  # Metot açıklaması
        self.focusOnButton(window)  # Düğme üzerine gelindiğinde odak (hover) efektini çiz
        window.blit(self.msg, self.msgRect)  # Düğme üzerindeki metni çiz

    def focusOnButton(self, window):
        """
        Fare imleci düğmenin üzerindeyse, büyütülmüş görüntüyü çizer.
        Aksi halde normal görüntüyü çizer.
        """  # Metot açıklaması
        if self.rect.collidepoint(pygame.mouse.get_pos()):  # Eğer fare düğme alanındaysa
            window.blit(self.imageLarger, (self.rect.x - 5, self.rect.y - 5))  # Büyütülmüş görüntüyü çiz
        else:
            window.blit(self.image, self.rect)  # Normal görüntüyü çiz

    def actionOnPress(self):
        """
        Düğmeye basıldığında gerçekleşecek eylemi tanımlar.
        Düğme adına bağlı olarak farklı görevler yapar.
        """  # Metot açıklaması
        global DEPLOYMENT, game_over  # Global deployment aşaması ve oyun bitişi bayrağını kullan
        if self.name == "Randomize":  # Eğer düğme "Randomize" ise
            self.randomizeShipPositions(playerFleet, playerGameGrid)  # Oyuncu gemilerinin konumlarını rastgele ayarla
            self.randomizeShipPositions(computerFleet, computerGameGrid)  # Bilgisayar gemilerinin konumlarını rastgele ayarla
        elif self.name == "Reset":  # Eğer düğme "Reset" ise
            resetGame()  # Oyunu sıfırla
        elif self.name == "Start":  # Eğer düğme "Start" ise
            if game_over:  # Eğer oyun bitti ise
                resetGame()  # Oyunu sıfırla
            else:
                DEPLOYMENT = deploymentPhase(DEPLOYMENT)  # Deployment aşamasını tersine çevir (yerleştirme/savaş aşaması)
                print("Deployment:", DEPLOYMENT)  # Konsola deployment durumunu yazdır
        elif self.name == "Quit":  # Eğer düğme "Quit" ise
            pass  # Çıkış işlemi ana döngüde ele alınır

    def resetShip(self, shipList):
        """Verilen listedeki tüm gemileri varsayılan konumlarına geri döndürür."""  # Metot açıklaması
        if DEPLOYMENT:  # Sadece deployment aşamasında çalışır
            for ship in shipList:  # Listedeki her gemi için
                ship.returnToDefaultPosition()  # Gemiyi varsayılan konumuna döndür

    def randomizeShipPositions(self, shipList, gameGrid):
        """Verilen grid üzerinde gemilerin konumunu rastgele ayarlar."""  # Metot açıklaması
        if DEPLOYMENT:  # Sadece deployment aşamasında çalışır
            randomizeShipPositions(shipList, gameGrid)  # randomizeShipPositions fonksiyonunu çağır

class Player:
    """İnsan oyuncusunu temsil eder."""  # Sınıf açıklaması
    def __init__(self):
        self.turn = True  # Oyuncunun sırası olduğunu belirtmek için True (oyun başında oyuncu başlar)

    def makeAttack(self, grid, logicGrid):
        """
        Düşman gridine tıklayarak oyuncunun saldırısını işler.
        Atışın isabetli veya ıskalama olmasına göre oyun mantığını ve istatistikleri günceller.
        """  # Metot açıklaması
        global player_stats, computer_stats, game_over, winner  # Global istatistikler ve oyun durumunu kullan
        posX, posY = pygame.mouse.get_pos()  # Mevcut fare konumunu (x, y) al
        # Tıklamanın düşman gridinin sınırları içinde olup olmadığını kontrol et
        if (posX >= grid[0][0][0] and posX <= grid[0][-1][0] + CELL_SIZE and
            posY >= grid[0][0][1] and posY <= grid[-1][0][1] + CELL_SIZE):
            for i, row in enumerate(grid):  # Grid'deki her satırı döngüye al
                for j, cell in enumerate(row):  # Satırdaki her hücreyi döngüye al
                    # Tıklamanın hücre sınırları içinde olup olmadığını kontrol et
                    if (posX >= cell[0] and posX < cell[0] + CELL_SIZE and
                        posY >= cell[1] and posY < cell[1] + CELL_SIZE):
                        player_stats["shots"] += 1  # Oyuncunun atış sayısını artır
                        SHOTSOUND.play()  # Nişancı ses efektini çal
                        if logicGrid[i][j] != " ":  # Hücre boş değilse (gemiyi temsil ediyorsa)
                            if logicGrid[i][j] == "O":  # Hücrede gemi varsa
                                print("Hit")  # Konsola "Hit" yazdır
                                HITSOUND.play()  # Patlama ses efektini çal
                                TOKENS.append(Tokens(GREEN_TOKEN, grid[i][j], "Hit", None, None))  # İsimabeti belirten token ekle
                                logicGrid[i][j] = "H"  # Mantık grid'inde hücreyi "H" (isabet) olarak güncelle
                                for ship in computerFleet:  # Bilgisayarın gemilerini kontrol et
                                    if (i, j) in ship.occupiedCells and (i, j) not in ship.hitCells:  # Eğer hücre gemiye ait ve henüz vurulmamışsa
                                        ship.hitCells.append((i, j))  # Gemideki bu hücreyi vurulmuş olarak işaretle
                                        player_stats["hits"] += 1  # Oyuncunun isabet sayısını artır
                                        if len(ship.hitCells) == len(ship.occupiedCells) and not ship.sunk:  # Eğer geminin tüm hücreleri vurulmuşsa ve gemi batmamışsa
                                            ship.sunk = True  # Gemiyi batırılmış olarak işaretle
                                            player_stats["sunk"] += 1  # Oyuncunun batırdığı gemi sayısını artır
                                            computer_stats["remaining"] -= 1  # Bilgisayarın kalan gemi sayısını azalt
                                            print(f"Computer ship sunk: {ship.name}")  # Konsola batırılan geminin adını yazdır
                                self.turn = False  # Oyuncunun sırası bitti
                        else:  # Hücre boşsa (gemi yoksa)
                            print("Miss")  # Konsola "Miss" yazdır
                            MISSSOUND.play()  # Splash (ıskalama) ses efektini çal
                            TOKENS.append(Tokens(RED_TOKEN, grid[i][j], "Miss", None, None))  # Işkalamayı belirten token ekle
                            logicGrid[i][j] = "M"  # Mantık grid'inde hücreyi "M" (ıskalama) olarak güncelle
                            player_stats["misses"] += 1  # Oyuncunun ıskalama sayısını artır
                            self.turn = False  # Oyuncunun sırası bitti
        if computer_stats["remaining"] <= 0:  # Eğer bilgisayarın kalan gemi sayısı 0 ise
            game_over = True  # Oyunu bitir
            winner = "Player"  # Oyuncuyu kazanan olarak belirle

class EasyComputer:
    """Basit bir bilgisayar rakibini temsil eder."""  # Sınıf açıklaması
    def __init__(self):
        self.turn = True  # Bilgisayarın sırası için True
        self.status = self.computerStatus("Thinking...")  # "Thinking..." durum mesajını başlat
        self.name = "Easy Computer"  # Bilgisayarın adını ayarla

    def computerStatus(self, msg):
        """
        Bilgisayar için bir durum mesajını render eder ve döndürür.
        Bu mesaj (örneğin, "Thinking...") ekranda görüntülenir.
        """  # Metot açıklaması
        font = pygame.font.SysFont("Stencil", 22)  # 22 punto "Stencil" fontunu oluştur
        message = font.render(msg, True, (0, 0, 0))  # Mesajı siyah renkte render et
        return message  # Render edilmiş mesajı döndür

    def makeAttack(self, gameLogic):
        """
        Bilgisayar, oyuncunun gridine saldırır.
        2 saniye bekler (düşünme süresi simülasyonu) ve rastgele geçerli bir hücre seçer.
        Saldırı sonucuna göre oyun mantığını ve istatistikleri günceller.
        """  # Metot açıklaması
        global computer_stats, player_stats, game_over, winner  # Global istatistikler ve oyun durumunu kullan
        start_time = pygame.time.get_ticks()  # Mevcut zamanı milisaniye olarak al
        while pygame.time.get_ticks() - start_time < 2000:  # 2 saniye (2000 ms) bekle
            updateGameScreen(GAME_SCREEN)  # Bekleme süresince ekranı güncelle (düşünme mesajı gösterilir)
        validChoice = False  # Geçerli hücre seçimi için bayrak
        while not validChoice:  # Geçerli bir hücre seçilene kadar döngü
            rowX = random.randint(0, 9)  # 0-9 arasında rastgele bir satır indeksi seç
            colX = random.randint(0, 9)  # 0-9 arasında rastgele bir sütun indeksi seç
            if gameLogic[rowX][colX] == " " or gameLogic[rowX][colX] == "O":  # Hücre boş veya gemi içeriyorsa
                validChoice = True  # Geçerli seçim
        computer_stats["shots"] += 1  # Bilgisayarın atış sayısını artır
        SHOTSOUND.play()  # Nişancı ses efektini çal
        if gameLogic[rowX][colX] == "O":  # Seçilen hücrede gemi varsa
            print("Hit Player's Ship")  # Konsola "Hit Player's Ship" yazdır
            HITSOUND.play()  # Patlama ses efektini çal
            TOKENS.append(Tokens(RED_TOKEN, playerGameGrid[rowX][colX], "Hit", None, None))  # Vuruşu belirten token ekle
            gameLogic[rowX][colX] = "H"  # Mantık grid'inde hücreyi "H" olarak güncelle
            for ship in playerFleet:  # Oyuncunun gemileri üzerinde döngüye gir
                if (rowX, colX) in ship.occupiedCells and (rowX, colX) not in ship.hitCells:  # Eğer hücre gemiye ait ve henüz vurulmamışsa
                    ship.hitCells.append((rowX, colX))  # Gemideki bu hücreyi vurulmuş olarak işaretle
                    computer_stats["hits"] += 1  # Bilgisayarın isabet sayısını artır
                    if len(ship.hitCells) == len(ship.occupiedCells) and not ship.sunk:  # Eğer geminin tüm hücreleri vurulmuşsa ve gemi batmamışsa
                        ship.sunk = True  # Gemiyi batırılmış olarak işaretle
                        computer_stats["sunk"] += 1  # Bilgisayarın batırdığı gemi sayısını artır
                        player_stats["remaining"] -= 1  # Oyuncunun kalan gemi sayısını azalt
                        print(f"Player ship sunk: {ship.name}")  # Konsola batırılan geminin adını yazdır
            self.turn = False  # Bilgisayarın sırası bitti
        else:  # Seçilen hücrede gemi yoksa
            gameLogic[rowX][colX] = "M"  # Hücreyi "M" olarak güncelle (ıskalama)
            print("Missed")  # Konsola "Missed" yazdır
            MISSSOUND.play()  # Splash ses efektini çal
            TOKENS.append(Tokens(GREEN_TOKEN, playerGameGrid[rowX][colX], "Miss", None, None))  # Işkalamayı belirten token ekle
            computer_stats["misses"] += 1  # Bilgisayarın ıskalama sayısını artır
            self.turn = False  # Bilgisayarın sırası bitti
        if player_stats["remaining"] <= 0:  # Eğer oyuncunun kalan gemi sayısı 0 ise
            game_over = True  # Oyunu bitir
            winner = "Computer"  # Bilgisayarı kazanan olarak belirle
        return self.turn  # Sıra durumunu döndür

    def draw(self, window):
        """Bilgisayarın sırasıysa ekranda 'Thinking...' mesajını gösterir."""  # Metot açıklaması
        if self.turn:  # Eğer bilgisayarın sırasıysa
            font = pygame.font.SysFont("Stencil", 24)  # 24 punto "Stencil" fontunu oluştur
            message = font.render("Thinking...", True, (0, 0, 0))  # "Thinking..." mesajını siyah renkte render et
            gap_top = computerGameGrid[-1][-1][1] + CELL_SIZE + 10  # Mesaj için üst boşluğu hesapla
            gap_bottom = computerGameGrid[-1][-1][1] + CELL_SIZE + 60  # Mesaj için alt boşluğu hesapla
            gap_center_y = (gap_top + gap_bottom) // 2  # Boşlukların dikey merkezini bul
            x_center = computerGameGrid[0][0][0] + (ROWS * CELL_SIZE) // 2 - message.get_width() // 2  # Mesajı yatay olarak ortala
            window.blit(message, (x_center, gap_center_y - message.get_height() // 2))  # "Thinking..." mesajını ekrana çiz

class Tokens:
    """Grid üzerinde isabet veya ıskalamayı gösteren animasyonlu tokenleri temsil eder."""  # Sınıf açıklaması
    def __init__(self, image, pos, action, imageList=None, explosionList=None, soundFile=None):
        self.image = image  # Tokenin temel görüntüsünü sakla (örneğin, kırmızı veya yeşil işaret)
        self.rect = self.image.get_rect()  # Token görüntüsünün dikdörtgenini (boyut ve konum) al
        self.pos = pos  # Tokenin çizileceği konumu sakla
        self.rect.topleft = self.pos  # Dikdörtgenin sol üst köşesini tokenin konumuna ayarla
        self.imageList = imageList  # İsteğe bağlı animasyon kareleri listesini sakla
        self.explosionList = explosionList  # Patlama animasyonu kareleri listesini sakla
        self.action = action  # Tokenin aksiyon türünü (örneğin, "Hit" veya "Miss") sakla
        self.soundFile = soundFile  # İsteğe bağlı olarak token ile ilişkili ses dosyasını sakla
        self.timer = pygame.time.get_ticks()  # Animasyon zamanlaması için mevcut zamanı kaydet
        self.explosionIndex = 0  # Patlama animasyonu için mevcut kare indeksini sakla
        self.explosion = False  # Patlama animasyonunun oynatılıp oynatılmayacağını belirten bayrak
        self.imageIndex = 0  # Diğer animasyon (örneğin, ateş animasyonu) için mevcut kare indeksini sakla

    def animateExplosion(self):
        """Patlama efektini animasyonla. Bitmişse ateş animasyonunu oynat."""  # Metot açıklaması
        self.explosionIndex += 1  # Patlama kare indeksini bir artır
        if self.explosionList and self.explosionIndex < len(self.explosionList):  # Eğer patlama görüntü listesi varsa ve indeks geçerliyse
            return self.explosionList[self.explosionIndex]  # Sonraki patlama karesini döndür
        else:
            return self.animateFire()  # Aksi halde ateş animasyonuna geç

    def animateFire(self):
        """Token için ateş efektini animasyonla."""  # Metot açıklaması
        if pygame.time.get_ticks() - self.timer >= 100:  # Son kare güncellemesinden 100ms geçmişse
            self.timer = pygame.time.get_ticks()  # Zamanlayıcıyı güncelle
            self.imageIndex = 1  # Kare indeksini 1 olarak ayarla (basit geçiş için)
        if self.imageList and self.imageIndex < len(self.imageList):  # Eğer animasyon görüntü listesi varsa ve indeks geçerliyse
            return self.imageList[self.imageIndex]  # İlgili animasyon karesini döndür
        else:
            self.imageIndex = 0  # Aksi halde kare indeksini sıfırla
            return self.imageList[self.imageIndex] if self.imageList else self.image  # İlk kareyi ya da temel görüntüyü döndür

    def draw(self, window):
        """Tokeni animasyonuyla birlikte ekrana çizer."""  # Metot açıklaması
        if not self.imageList:  # Eğer animasyon görüntü listesi yoksa
            window.blit(self.image, self.rect)  # Sadece temel görüntüyü çiz
        else:
            self.image = self.animateExplosion()  # Patlama (veya ateş) animasyonunu güncelle
            self.rect = self.image.get_rect(topleft=self.pos)  # Yeni görüntüye göre dikdörtgeni konumunu koruyarak güncelle
            self.rect.y = self.pos[1] - 10  # Görsel etki için y konumunu hafifçe ayarla
            window.blit(self.image, self.rect)  # Animasyonlu görüntüyü ekrana çiz

# ---------------- YARDIMCI FONKSİYONLAR ---------------- #
def createGameGrid(rows, cols, cellsize, pos):
    """
    Oyun tahtası için 2D koordinat grid'i oluşturur.
    Her hücre, sol üst köşe koordinatı ile temsil edilir.
    """  # Fonksiyon açıklaması
    start_X = pos[0]  # Grid için başlangıç x koordinatı
    start_Y = pos[1]  # Grid için başlangıç y koordinatı
    coordGrid = []  # Grid koordinatlarını saklamak için boş liste
    for row in range(rows):  # Satır sayısı kadar döngü
        row_coords = []  # Mevcut satırın koordinatlarını saklamak için liste
        for col in range(cols):  # Sütun sayısı kadar döngü   
            row_coords.append((start_X, start_Y))  # Mevcut hücrenin koordinatını ekle
            start_X += cellsize  # Bir sonraki hücre için x koordinatını hücre boyutu kadar artır
        coordGrid.append(row_coords)  # Satırı grid'e ekle
        start_X = pos[0]  # Yeni satır için x koordinatını sıfırla
        start_Y += cellsize  # Yeni satır için y koordinatını hücre boyutu kadar artır
    return coordGrid  # Tam grid'i döndür

def createGameLogic(rows, cols):
    """
    Oyun durumunu temsil eden 2D mantık grid'i oluşturur.
    Her hücre, gemi yoksa boşluk " " ile başlatılır.
    """  # Fonksiyon açıklaması
    gameLogic = []  # Mantık grid'ini saklamak için boş liste
    for row in range(rows):  # Satır sayısı kadar döngü
        row_logic = []  # Mevcut satırın mantık değerlerini saklamak için liste
        for col in range(cols):  # Sütun sayısı kadar döngü
            row_logic.append(" ")  # Her hücreye boşluk ekle (gemi yok)
        gameLogic.append(row_logic)  # Satırı mantık grid'ine ekle
    return gameLogic  # Tam mantık grid'ini döndür

def showGridOnScreen(window, cellsize, playerGrid, computerGrid):
    """
    Hem oyuncunun hem bilgisayarın grid'lerini oyun penceresinde çizer.
    Her hücre beyaz kenarlıkla çizilir.
    """  # Fonksiyon açıklaması
    for grid in [playerGrid, computerGrid]:  # Her iki grid için döngüye gir
        for row in grid:  # Grid'deki her satır için döngü
            for cell in row:  # Her hücre için döngü
                pygame.draw.rect(window, (255, 255, 255), (cell[0], cell[1], cellsize, cellsize), 1)  # Hücreyi beyaz kenarlıkla çiz

def printGameLogic():
    """
    Mantık grid'ini hata ayıklama için konsola yazdırır.
    """  # Fonksiyon açıklaması
    print("Player Grid".center(50, "#"))  # Oyuncu grid'inin başlığını, '#' karakterleri ile merkezlenmiş şekilde yazdır
    for row in playerGameLogic:  # Oyuncu mantık grid'inin her satırı için döngü
        print(row)  # Satırı yazdır
    print("Computer Grid".center(50, "#"))  # Bilgisayar grid'inin başlığını yazdır
    for row in computerGameLogic:  # Bilgisayar mantık grid'inin her satırı için döngü
        print(row)  # Satırı yazdır

def createFleet():
    """
    FLEET sözlüğüne göre bir dizi Gemiyi (Ship) oluşturur.
    """  # Fonksiyon açıklaması
    fleet = []  # Gemi listesini başlat
    for name in FLEET.keys():  # FLEET sözlüğündeki her gemi adı için döngü
        fleet.append(Ship(name, FLEET[name][1], FLEET[name][2], FLEET[name][3]))  # Gemiyi oluşturup listeye ekle
    return fleet  # Gemi listesini döndür

def sortFleet(ship, shipList):
    """
    Seçilen gemiyi, filodaki çizim sırasını değiştirmek için listenin sonuna taşır.
    """  # Fonksiyon açıklaması
    shipList.remove(ship)  # Gemiyi mevcut konumundan çıkar
    shipList.append(ship)  # Listenin sonuna ekle

def randomizeShipPositions(shipList, gameGrid):
    """
    Gemilerin üst üste binmeyecek şekilde grid üzerinde rastgele yerleştirilmesini sağlar.
    """  # Fonksiyon açıklaması
    placedShips = []  # Yerleştirilen gemileri saklamak için boş liste oluştur
    for ship in shipList:  # Gemi listesindeki her gemi için döngü
        validPosition = False  # Geminin konumunun geçerli olup olmadığını kontrol etmek için bayrak
        while not validPosition:  # Geçerli bir konum bulunana kadar döngüye gir
            ship.returnToDefaultPosition()  # Gemiyi varsayılan konumuna geri döndür
            rotateShip = random.choice([True, False])  # Rastgele gemiyi döndürme kararı ver
            if rotateShip:  # Eğer gemi döndürülüyorsa
                yAxis = random.randint(0, 9)  # Rastgele bir satır indeksi seç
                xAxis = random.randint(0, 9 - (ship.horizontalImage.get_width() // CELL_SIZE))  # Yatay olarak sığacak şekilde rastgele bir sütun indeksi seç
                ship.rotateShip(True)  # Gemiyi zorla yatay konuma döndür
                ship.rect.topleft = gameGrid[yAxis][xAxis]  # Gemiyi seçilen grid hücresine yerleştir
            else:  # Gemiyi döndürme seçilmediyse (dikey konum)
                yAxis = random.randint(0, 9 - (ship.verticalImage.get_height() // CELL_SIZE))  # Dikey olarak sığacak şekilde rastgele bir satır indeksi seç
                xAxis = random.randint(0, 9)  # Rastgele bir sütun indeksi seç
                ship.rect.topleft = gameGrid[yAxis][xAxis]  # Gemiyi seçilen grid hücresine yerleştir
            validPosition = True  # Konum geçerli kabul edilir
            for item in placedShips:  # Daha önce yerleştirilmiş gemiler üzerinde döngü
                if ship.rect.colliderect(item.rect):  # Eğer geminin dikdörtgeni başka bir gemiyle çakışıyorsa
                    validPosition = False  # Geçerli konum değil
                    break  # Döngüden çık
        ship.snapToGrid(gameGrid)  # Gemiyi grid'e tam yapıştır
        placedShips.append(ship)  # Gemiyi yerleştirilen gemiler listesine ekle

def updateGameLogic(coordGrid, shipList, gameLogic):
    """
    Gemilerin konumlarına göre mantık grid'ini günceller.
    Gemi bulunan hücreler "O" ile işaretlenir.
    """  # Fonksiyon açıklaması
    for i, row in enumerate(coordGrid):  # Grid'in her satırı için döngü
        for j, cell in enumerate(row):  # Her hücre için döngü
            if gameLogic[i][j] in ["H", "M"]:  # Eğer hücre zaten "H" (isabet) veya "M" (ıskalama) ile işaretlendiyse
                continue  # Bu hücreyi güncelleme
            else:
                gameLogic[i][j] = " "  # Aksi halde hücreyi boşluk ile sıfırla
            for ship in shipList:  # Her gemiyi kontrol et
                if pygame.Rect(cell[0], cell[1], CELL_SIZE, CELL_SIZE).colliderect(ship.rect):  # Eğer hücre, geminin dikdörtgeniyle çakışıyorsa
                    gameLogic[i][j] = "O"  # Hücreyi "O" olarak işaretle (gemiyi temsil eder)

def drawScoreboard(window):
    """
    Bilgisayar grid'inin altında skor tablosunu çizer.
    Oyuncu ve bilgisayarın atış, isabet, ıskalama, batırılan gemi ve kalan gemi sayılarını gösterir.
    """  # Fonksiyon açıklaması
    font = pygame.font.SysFont("Stencil", 20)  # 20 punto "Stencil" fontunu oluştur
    player_text = (f"Player - Shots: {player_stats['shots']}  Hits: {player_stats['hits']}  "  # Oyuncu istatistik metnini oluştur
                   f"Misses: {player_stats['misses']}  Sunk: {player_stats['sunk']}  "
                   f"Remaining: {player_stats['remaining']}")
    computer_text = (f"Computer - Shots: {computer_stats['shots']}  Hits: {computer_stats['hits']}  "  # Bilgisayar istatistik metnini oluştur
                     f"Misses: {computer_stats['misses']}  Sunk: {computer_stats['sunk']}  "
                     f"Remaining: {computer_stats['remaining']}")
    x_pos = computerGameGrid[0][0][0]  # Skor tablosunun x konumunu bilgisayar grid'ine hizala
    y_pos = computerGameGrid[-1][-1][1] + CELL_SIZE + 60  # Skor tablosunu bilgisayar grid'inin altına, biraz boşluk bırakarak yerleştir
    scoreboard_width = ROWS * CELL_SIZE  # Skor tablosu genişliği, grid genişliğiyle eşleşir
    pygame.draw.rect(window, (50, 50, 50), (x_pos, y_pos, scoreboard_width, 40))  # Skor tablosu için arka plan dikdörtgeni çiz
    text_surf_player = font.render(player_text, True, (255, 255, 255))  # Oyuncu metnini beyaz renkte render et
    text_surf_computer = font.render(computer_text, True, (255, 255, 255))  # Bilgisayar metnini beyaz renkte render et
    window.blit(text_surf_player, (x_pos + 5, y_pos + 5))  # Oyuncu metnini dikdörtgenin sol üstüne yerleştir
    window.blit(text_surf_computer, (x_pos + 5, y_pos + 25))  # Bilgisayar metnini oyuncu metninin altına yerleştir

def drawScoreboardOverlay(window):
    """
    Oyun bittiğinde, final skorlarını gösteren overlay üzerinde skor tablosunu çizer.
    """  # Fonksiyon açıklaması
    font = pygame.font.SysFont("Stencil", 20)  # Overlay için 20 punto "Stencil" fontunu oluştur
    player_text = (f"Player - Shots: {player_stats['shots']}  Hits: {player_stats['hits']}  "  # Oyuncu skorunu oluştur
                   f"Misses: {player_stats['misses']}  Sunk: {player_stats['sunk']}  "
                   f"Remaining: {player_stats['remaining']}")
    computer_text = (f"Computer - Shots: {computer_stats['shots']}  Hits: {computer_stats['hits']}  "  # Bilgisayar skorunu oluştur
                     f"Misses: {computer_stats['misses']}  Sunk: {computer_stats['sunk']}  "
                     f"Remaining: {computer_stats['remaining']}")
    scoreboard_width = SCREEN_WIDTH - 100  # Overlay skor tablosu genişliğini belirle
    x_pos = 50  # Sol kenardan 50 piksel boşluk bırak
    y_pos = SCREEN_HEIGHT // 2 - 50  # Ekranın ortasından biraz yukarıya yerleştir
    pygame.draw.rect(window, (50, 50, 50), (x_pos, y_pos, scoreboard_width, 60))  # Overlay skor tablosu arka planını çiz
    text_surf_player = pygame.font.SysFont("Stencil", 20).render(player_text, True, (255, 255, 255))  # Oyuncu skorunu render et
    text_surf_computer = pygame.font.SysFont("Stencil", 20).render(computer_text, True, (255, 255, 255))  # Bilgisayar skorunu render et
    window.blit(text_surf_player, (x_pos + 5, y_pos + 5))  # Oyuncu skorunu overlay üzerine yerleştir
    window.blit(text_surf_computer, (x_pos + 5, y_pos + 35))  # Bilgisayar skorunu overlay üzerine yerleştir

def draw_mp3_player(window):
    """
    MP3 oynatıcı arayüzünü çizer.
    Bu, kontrol düğmeleri ve parça isimlerini içerir.
    Güncellenmiş koordinatlar, diğer oyun elemanlarıyla çakışmayı önler.
    """  # Fonksiyon açıklaması
    global mp3_button_rects, mp3_song_rects  # MP3 düğme ve şarkı dikdörtgen sözlüklerini kullan
    mp3_area = pygame.Rect(750, SCREEN_HEIGHT - 250, SCREEN_WIDTH - 780, 200)  # MP3 oynatıcı alanını tanımla
    pygame.draw.rect(window, (30, 30, 30), mp3_area)  # MP3 oynatıcı arka planını koyu gri ile çiz
    font = pygame.font.SysFont("Stencil", 20)  # MP3 metinleri için font oluştur
    mp3_button_rects = {  # MP3 kontrol düğmelerini ve konumlarını tanımla
        "Prev": pygame.Rect(760, SCREEN_HEIGHT - 245, 80, 30),  # "Prev" düğmesi
        "PlayPause": pygame.Rect(850, SCREEN_HEIGHT - 245, 100, 30),  # "PlayPause" düğmesi
        "Next": pygame.Rect(960, SCREEN_HEIGHT - 245, 80, 30),  # "Next" düğmesi
        "Vol-": pygame.Rect(1050, SCREEN_HEIGHT - 245, 80, 30),  # Müzik için "Ses Azalt" düğmesi
        "Vol+": pygame.Rect(1140, SCREEN_HEIGHT - 245, 80, 30)  # Müzik için "Ses Artır" düğmesi
    }
    for key, rect in mp3_button_rects.items():  # Her MP3 kontrol düğmesi üzerinde döngü
        pygame.draw.rect(window, (70, 70, 70), rect)  # Düğme arka planını çiz (koyu gri)
        text = font.render(key, True, (255, 255, 255))  # Düğme etiketini beyaz renkte render et
        window.blit(text, (rect.x + (rect.width - text.get_width()) // 2,
                           rect.y + (rect.height - text.get_height()) // 2))  # Metni düğmenin ortasına yerleştir
    mp3_song_rects = {}  # Şarkı isimleri için boş dikdörtgen sözlüğü oluştur
    start_y = SCREEN_HEIGHT - 190  # Şarkı isimleri için başlangıç y konumunu ayarla
    for i, track in enumerate(bg_music_tracks):  # Her müzik parçası için döngü
        track_name = os.path.basename(track)  # Dosya yolundan sadece dosya adını al
        song_text = font.render(track_name, True, (255, 255, 255))  # Parça adını beyaz renkte render et
        song_rect = pygame.Rect(760, start_y + i * 25, 300, 20)  # Her parça için bir dikdörtgen oluştur
        window.blit(song_text, (song_rect.x, song_rect.y))  # Parça adını ekrana çiz
        mp3_song_rects[i] = song_rect  # Dikdörtgeni, parça indeksini anahtar olarak sözlüğe ekle
    return mp3_button_rects, mp3_song_rects  # MP3 düğme ve şarkı dikdörtgen sözlüklerini döndür

def draw_sfx_controls(window):
    """
    SFX (Ses Efekti) ses kontrollerini çizer.
    Bu bölüm, MP3 oynatıcı arayüzünün solunda yer alır.
    Her ses efekti (Splash, Explosion, Gunshot) için ayrı "Ses Azalt" ve "Ses Artır" düğmeleri içerir.
    """  # Fonksiyon açıklaması
    global sfx_buttons, splash_volume, explosion_volume, gunshot_volume  # Global SFX değişkenlerini ve sözlüğünü kullan
    sfx_area = pygame.Rect(500, SCREEN_HEIGHT - 250, 240, 180)  # SFX kontrol alanını tanımla
    pygame.draw.rect(window, (40, 40, 40), sfx_area)  # SFX alanı için koyu arka planı çiz
    font = pygame.font.SysFont("Stencil", 18)  # SFX metni için 18 punto "Stencil" fontu oluştur
    sfx_buttons = {}  # SFX düğme sözlüğünü sıfırla
    
    # --- Splash Kontrolleri ---
    row_y = sfx_area.y + 10  # Splash kontrolleri için y konumunu ayarla
    minus_rect = pygame.Rect(sfx_area.x + 10, row_y, 50, 30)  # "Ses Azalt" düğmesi için dikdörtgen oluştur
    plus_rect = pygame.Rect(sfx_area.x + sfx_area.width - 60, row_y, 50, 30)  # "Ses Artır" düğmesi için dikdörtgen oluştur
    pygame.draw.rect(window, (70, 70, 70), minus_rect)  # "Ses Azalt" düğmesini çiz
    pygame.draw.rect(window, (70, 70, 70), plus_rect)  # "Ses Artır" düğmesini çiz
    minus_text = font.render("-", True, (255, 255, 255))  # "-" simgesini render et
    plus_text = font.render("+", True, (255, 255, 255))  # "+" simgesini render et
    window.blit(minus_text, (minus_rect.centerx - minus_text.get_width()//2, minus_rect.centery - minus_text.get_height()//2))  # "-" simgesini düğme ortasına yerleştir
    window.blit(plus_text, (plus_rect.centerx - plus_text.get_width()//2, plus_rect.centery - plus_text.get_height()//2))  # "+" simgesini düğme ortasına yerleştir
    label_text = font.render(f"Splash: {splash_volume:.2f}", True, (255, 255, 255))  # Splash ses seviyesi etiketini render et
    window.blit(label_text, (sfx_area.x + 70, row_y))  # Etiketi düğmelerin yanına yerleştir
    sfx_buttons["Splash_VolDown"] = minus_rect  # "Splash Ses Azalt" düğmesinin dikdörtgenini sözlüğe ekle
    sfx_buttons["Splash_VolUp"] = plus_rect  # "Splash Ses Artır" düğmesinin dikdörtgenini sözlüğe ekle

    # --- Explosion Kontrolleri ---
    row_y = sfx_area.y + 70  # Explosion kontrolleri için y konumunu ayarla
    minus_rect = pygame.Rect(sfx_area.x + 10, row_y, 50, 30)  # "Ses Azalt" düğmesini oluştur
    plus_rect = pygame.Rect(sfx_area.x + sfx_area.width - 60, row_y, 50, 30)  # "Ses Artır" düğmesini oluştur
    pygame.draw.rect(window, (70, 70, 70), minus_rect)  # "Ses Azalt" düğmesini çiz
    pygame.draw.rect(window, (70, 70, 70), plus_rect)  # "Ses Artır" düğmesini çiz
    minus_text = font.render("-", True, (255, 255, 255))  # "-" simgesini render et
    plus_text = font.render("+", True, (255, 255, 255))  # "+" simgesini render et
    window.blit(minus_text, (minus_rect.centerx - minus_text.get_width()//2, minus_rect.centery - minus_text.get_height()//2))  # "-" simgesini ortala
    window.blit(plus_text, (plus_rect.centerx - plus_text.get_width()//2, plus_rect.centery - plus_text.get_height()//2))  # "+" simgesini ortala
    label_text = font.render(f"Explosion: {explosion_volume:.2f}", True, (255, 255, 255))  # Explosion ses seviyesi etiketini render et
    window.blit(label_text, (sfx_area.x + 70, row_y))  # Etiketi yerleştir
    sfx_buttons["Explosion_VolDown"] = minus_rect  # "Explosion Ses Azalt" düğmesini sözlüğe ekle
    sfx_buttons["Explosion_VolUp"] = plus_rect  # "Explosion Ses Artır" düğmesini sözlüğe ekle

    # --- Gunshot Kontrolleri ---
    row_y = sfx_area.y + 130  # Gunshot kontrolleri için y konumunu ayarla
    minus_rect = pygame.Rect(sfx_area.x + 10, row_y, 50, 30)  # "Ses Azalt" düğmesi için dikdörtgen oluştur
    plus_rect = pygame.Rect(sfx_area.x + sfx_area.width - 60, row_y, 50, 30)  # "Ses Artır" düğmesi için dikdörtgen oluştur
    pygame.draw.rect(window, (70, 70, 70), minus_rect)  # "Ses Azalt" düğmesini çiz
    pygame.draw.rect(window, (70, 70, 70), plus_rect)  # "Ses Artır" düğmesini çiz
    minus_text = font.render("-", True, (255, 255, 255))  # "-" simgesini render et
    plus_text = font.render("+", True, (255, 255, 255))  # "+" simgesini render et
    window.blit(minus_text, (minus_rect.centerx - minus_text.get_width()//2, minus_rect.centery - minus_text.get_height()//2))  # "-" simgesini ortala
    window.blit(plus_text, (plus_rect.centerx - plus_text.get_width()//2, plus_rect.centery - plus_text.get_height()//2))  # "+" simgesini ortala
    label_text = font.render(f"Gunshot: {gunshot_volume:.2f}", True, (255, 255, 255))  # Gunshot ses seviyesi etiketini render et
    window.blit(label_text, (sfx_area.x + 70, row_y))  # Etiketi yerleştir
    sfx_buttons["Gunshot_VolDown"] = minus_rect  # "Gunshot Ses Azalt" düğmesini sözlüğe ekle
    sfx_buttons["Gunshot_VolUp"] = plus_rect  # "Gunshot Ses Artır" düğmesini sözlüğe ekle
    
    return sfx_buttons  # SFX kontrol düğmeleri sözlüğünü döndür

def drawThinkingMessage(window):
    """
    Eğer bilgisayarın sırasıysa ekranda "Thinking..." mesajını gösterir.
    """  # Fonksiyon açıklaması
    if computer.turn:  # Eğer bilgisayarın sırasıysa
        font = pygame.font.SysFont("Stencil", 24)  # 24 punto "Stencil" fontunu oluştur
        message = font.render("Thinking...", True, (0, 0, 0))  # "Thinking..." mesajını siyah renkte render et
        gap_top = computerGameGrid[-1][-1][1] + CELL_SIZE + 10  # Üst boşluk hesapla
        gap_bottom = computerGameGrid[-1][-1][1] + CELL_SIZE + 60  # Alt boşluk hesapla
        gap_center_y = (gap_top + gap_bottom) // 2  # Boşlukların dikey merkezini bul
        x_center = computerGameGrid[0][0][0] + (ROWS * CELL_SIZE) // 2 - message.get_width() // 2  # Mesajı yatay olarak ortala
        window.blit(message, (x_center, gap_center_y - message.get_height() // 2))  # Mesajı ekrana çiz

def drawGameOver(window):
    """
    Oyun bittiğinde, final kazanan mesajı, skor tablosu ve Restart/Quit düğmeleri içeren overlay'i çizer.
    """  # Fonksiyon açıklaması
    global overlay_buttons  # Global overlay düğmeleri listesini kullan
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))  # Ekranı kaplayacak bir surface oluştur
    overlay.set_alpha(180)  # Overlay'in şeffaflık (alpha) değerini ayarla
    overlay.fill((0, 0, 0))  # Overlay'i siyah ile doldur
    window.blit(overlay, (0, 0))  # Overlay'i oyun ekranının üzerine çiz
    font_large = pygame.font.SysFont("Stencil", 50)  # Büyük boyutlu "Stencil" fontunu oluştur
    if winner == "Player":  # Eğer oyuncu kazandıysa
        win_message = "You Win!"  # Kazanma mesajını ayarla
    else:
        win_message = "You Lose, Computer Wins!"  # Kaybetme mesajını ayarla
    win_text = font_large.render(win_message, True, (255, 255, 0))  # Mesajı sarı renkte render et
    window.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 150))  # Mesajı overlay üzerinde ortala
    drawScoreboardOverlay(window)  # Overlay üzerinde skor tablosunu çiz
    restart_button = Button(BUTTON_IMAGE, (150, 50), (SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2 + 50), "Restart")  # Restart düğmesini oluştur
    quit_button = Button(BUTTON_IMAGE, (150, 50), (SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2 + 50), "Quit")  # Quit düğmesini oluştur
    restart_button.draw(window)  # Restart düğmesini ekrana çiz
    quit_button.draw(window)  # Quit düğmesini ekrana çiz
    overlay_buttons = [restart_button, quit_button]  # Global overlay düğmeleri listesini güncelle

def resetGame():
    """
    Oyunu başlangıç durumuna sıfırlar.
    Tüm oyun değişkenlerini, grid'leri, gemi filolarını ve istatistikleri sıfırlar.
    """  # Fonksiyon açıklaması
    global game_over, winner, DEPLOYMENT  # Oyun durumu ve deployment aşaması için global değişkenleri kullan
    global playerFleet, computerFleet, playerGameLogic, computerGameLogic, playerGameGrid, computerGameGrid  # Grid ve filo değişkenlerini kullan
    global player_stats, computer_stats, player1, computer, TOKENS  # İstatistikler, oyuncu nesneleri ve token listesini kullan
    game_over = False  # Oyunun bittiğini gösteren bayrağı False yap
    winner = ""  # Kazananı temizle
    DEPLOYMENT = True  # Gemi yerleştirme aşamasına geç (deployment)
    player_stats = {"shots": 0, "hits": 0, "misses": 0, "sunk": 0, "remaining": 0}  # Oyuncu istatistiklerini sıfırla
    computer_stats = {"shots": 0, "hits": 0, "misses": 0, "sunk": 0, "remaining": 0}  # Bilgisayar istatistiklerini sıfırla
    TOKENS.clear()  # Token listesini temizle
    playerGameGrid = createGameGrid(ROWS, COLS, CELL_SIZE, (50, 50))  # Oyuncu grid'ini yeniden oluştur
    playerGameLogic = createGameLogic(ROWS, COLS)  # Oyuncu mantık grid'ini yeniden oluştur
    computerGameGrid = createGameGrid(ROWS, COLS, CELL_SIZE, (SCREEN_WIDTH - (ROWS * CELL_SIZE), 50))  # Bilgisayar grid'ini yeniden oluştur
    computerGameLogic = createGameLogic(ROWS, COLS)  # Bilgisayar mantık grid'ini yeniden oluştur
    playerFleet = createFleet()  # Oyuncunun gemi filolarını yeniden oluştur
    computerFleet = createFleet()  # Bilgisayarın gemi filolarını yeniden oluştur
    randomizeShipPositions(computerFleet, computerGameGrid)  # Bilgisayar gemilerini rastgele yerleştir
    computer_stats["remaining"] = len(computerFleet)  # Bilgisayarın kalan gemi sayısını ayarla
    player_stats["remaining"] = len(playerFleet)  # Oyuncunun kalan gemi sayısını ayarla
    player1 = Player()  # Yeni bir oyuncu nesnesi oluştur
    computer = EasyComputer()  # Yeni bir bilgisayar nesnesi oluştur
    play_music()  # Arka plan müziğini yeniden başlat

def deploymentPhase(deployment):
    """
    Deployment aşamasını tersine çevirir.
    Eğer gemiler yerleştiriliyorsa savaş aşamasına, aksi halde tekrar yerleştirme aşamasına geçer.
    """  # Fonksiyon açıklaması
    return not deployment  # Mevcut deployment durumunun tersini döndür

def updateGameScreen(window):
    """
    Ekranı günceller ve tüm oyun elemanlarını yeniden çizer.
    Buna arka plan, grid'ler, gemiler, tokenler, düğmeler, SFX kontrolleri, MP3 oynatıcı vb. dahildir.
    """  # Fonksiyon açıklaması
    window.blit(BACKGROUND, (0, 0))  # Arka plan görüntüsünü pencereye çiz
    showGridOnScreen(window, CELL_SIZE, playerGameGrid, computerGameGrid)  # Hem oyuncu hem bilgisayar grid'lerini çiz
    player_origin = (playerGameGrid[0][0][0] - CELL_SIZE, playerGameGrid[0][0][1] - CELL_SIZE)  # Oyuncu grid resmi için başlangıç ofsetini hesapla
    window.blit(PGAMEGRIDIMG, player_origin)  # Oyuncu grid resmini çiz
    for ship in playerFleet:  # Oyuncunun filodaki her gemi için döngü
        ship.snapToGridEdge(playerGameGrid)  # Geminin grid sınırları içinde kalmasını sağla
        ship.snapToGrid(playerGameGrid)  # Gemiyi en yakın grid hücresine yapıştır
        ship.draw(window)  # Gemiyi ekrana çiz
    for ship in computerFleet:  # Bilgisayarın filodaki her gemi için döngü
        ship.snapToGridEdge(computerGameGrid)  # Geminin bilgisayar grid sınırları içinde kalmasını sağla
        ship.snapToGrid(computerGameGrid)  # Gemiyi bilgisayar grid'ine yapıştır
        ship.draw(window)  # Gemiyi ekrana çiz
    computer_origin = (computerGameGrid[0][0][0] - CELL_SIZE, computerGameGrid[0][0][1] - CELL_SIZE)  # Bilgisayar grid resmi için başlangıç ofsetini hesapla
    window.blit(CGAMEGRIDIMG, computer_origin)  # Bilgisayar grid resmini çiz
    for button in BUTTONS:  # Ana arayüz düğmeleri için döngü
        button.draw(window)  # Düğmeleri ekrana çiz
    computer.draw(window)  # Bilgisayarın durum mesajını (örneğin "Thinking...") çiz
    for token in TOKENS:  # Hit/Miss tokenleri için döngü
        token.draw(window)  # Tokenleri ekrana çiz
    updateGameLogic(playerGameGrid, playerFleet, playerGameLogic)  # Oyuncu gemilerine göre mantık grid'ini güncelle
    updateGameLogic(computerGameGrid, computerFleet, computerGameLogic)  # Bilgisayar gemilerine göre mantık grid'ini güncelle
    drawScoreboard(window)  # Skor tablosunu çiz
    drawThinkingMessage(window)  # Bilgisayar "Thinking..." mesajını çiz (varsa)
    draw_sfx_controls(window)  # SFX ses kontrollerini çiz
    draw_mp3_player(window)  # MP3 oynatıcı arayüzünü çiz
    if game_over:  # Eğer oyun bittiyse
        drawGameOver(window)  # Oyun bitiş overlay'ini çiz
    pygame.display.update()  # Tüm elemanları göstermek için ekranı güncelle

def loadImage(path, size, rotate=False):
    """
    Verilen dosya yolundan bir görüntü yükler, belirtilen boyuta ölçekler,
    ve isteğe bağlı olarak 90 derece döndürür (rotate True ise).
    """  # Fonksiyon açıklaması
    img = pygame.image.load(path).convert_alpha()  # Görüntüyü alfa kanalı ile yükle
    img = pygame.transform.scale(img, size)  # Görüntüyü belirtilen boyuta ölçekle
    if rotate:  # Eğer döndürme isteniyorsa
        img = pygame.transform.rotate(img, -90)  # Görüntüyü -90 derece döndür
    return img  # İşlenmiş görüntüyü döndür

def loadAnimationImages(path, aniNum, size):
    """
    Bir animasyon için bir dizi görüntü yükler.
    aniNum, yüklenecek görüntü sayısını belirtir.
    """  # Fonksiyon açıklaması
    imageList = []  # Animasyon karelerini saklamak için boş liste oluştur
    for num in range(aniNum):  # 0'dan aniNum-1'e kadar döngü
        if num < 10:  # Eğer sayı 10'dan küçükse
            imageList.append(loadImage(f"{path}00{num}.png", size))  # Dosya adını iki basamaklı biçimde formatlayıp yükle
        elif num < 100:  # Eğer sayı 100'den küçükse
            imageList.append(loadImage(f"{path}0{num}.png", size))  # Dosya adını bir basamaklı biçimde formatlayıp yükle
        else:
            imageList.append(loadImage(f"{path}{num}.png", size))  # 100 ve üzeri için dosya adını direkt kullanarak yükle
    return imageList  # Animasyon görüntü listesini döndür

def takeTurns(p1, p2):
    """
    Oyuncu ile bilgisayar arasında sırayı değiştirir.
    Eğer oyuncu hamle yaptıysa, bilgisayar saldırır; aksi halde oyuncunun sırası gelir.
    """  # Fonksiyon açıklaması
    if p1.turn:  # Eğer oyuncunun sırasıysa
        p2.turn = False  # Bilgisayarın sırası olmadığını ayarla
    else:  # Aksi halde
        p2.turn = True  # Bilgisayarın sırasını ayarla
        if not p2.makeAttack(playerGameLogic):  # Bilgisayar saldırısını gerçekleştir; eğer False dönerse
            p1.turn = True  # Oyuncuya sıra ver

# ---------------- OYUN AYARLARI VE DEĞİŞKENLER ---------------- #
SCREEN_WIDTH = 1260    # Oyun penceresinin genişliği (piksel cinsinden)
SCREEN_HEIGHT = 960    # Oyun penceresinin yüksekliği (piksel cinsinden)
ROWS = 10              # Grid'deki satır sayısı
COLS = 10              # Grid'deki sütun sayısı
CELL_SIZE = 50         # Her grid hücresinin boyutu (piksel cinsinden)
DEPLOYMENT = True      # Gemilerin yerleştirme aşamasında olup olmadığımızı belirten bayrak (True: yerleştirme, False: savaş)

# Belirtilen boyutlarda ana oyun penceresini oluştur
GAME_SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Ana pencereyi oluştur
pygame.display.set_caption("Battle Ship")  # Pencere başlığını ayarla

# FLEET sözlüğü, gemi detaylarını içerir: gemi adı, görüntü yolu, varsayılan konum ve boyut
FLEET = {
    'battleship': ["battleship", os.path.join("assets", "images", "ships", "battleship", "battleship.png"), (125, 600), (40, 195)],  # Battleship detayları
    'cruiser': ["cruiser", os.path.join("assets", "images", "ships", "cruiser", "cruiser.png"), (200, 600), (40, 195)],  # Cruiser detayları
    'destroyer': ["destroyer", os.path.join("assets", "images", "ships", "destroyer", "destroyer.png"), (275, 600), (43, 195)],  # Destroyer detayları
    'patrol boat': ["patrol boat", os.path.join("assets", "images", "ships", "patrol boat", "patrol boat.png"), (425, 600), (20, 95)],  # Patrol boat detayları
    'submarine': ["submarine", os.path.join("assets", "images", "ships", "submarine", "submarine.png"), (350, 600), (30, 145)],  # Submarine detayları
    'carrier': ["carrier", os.path.join("assets", "images", "ships", "carrier", "carrier.png"), (50, 600), (45, 245)],  # Carrier detayları
    'rescue ship': ["rescue ship", os.path.join("assets", "images", "ships", "rescue ship", "rescue ship.png"), (500, 600), (20, 95)]  # Rescue ship detayları
}

# Oyuncu ve bilgisayar grid'lerini (görsel ve mantıksal) oluştur
playerGameGrid = createGameGrid(ROWS, COLS, CELL_SIZE, (50, 50))  # Oyuncu grid'ini (50,50) konumunda oluştur
playerGameLogic = createGameLogic(ROWS, COLS)  # Oyuncu mantık grid'ini oluştur
playerFleet = createFleet()  # Oyuncunun gemi filolarını oluştur

computerGameGrid = createGameGrid(ROWS, COLS, CELL_SIZE, (SCREEN_WIDTH - (ROWS * CELL_SIZE), 50))  # Bilgisayar grid'ini ekranın sağında oluştur
computerGameLogic = createGameLogic(ROWS, COLS)  # Bilgisayar mantık grid'ini oluştur
computerFleet = createFleet()  # Bilgisayarın gemi filolarını oluştur
randomizeShipPositions(computerFleet, computerGameGrid)  # Bilgisayar gemilerini rastgele yerleştir

printGameLogic()  # Başlangıç mantık grid'lerini hata ayıklama için konsola yazdır

# Varlıklar (düğmeler, tokenler, grid görüntüleri, arka plan) için görüntüleri yükle
BUTTON_IMAGE = loadImage(os.path.join("assets", "images", "buttons", "button.png"), (150, 50))  # Düğme görüntüsünü (150x50) yükle
BUTTONS = [  # Ana arayüz düğmelerini oluştur
    Button(BUTTON_IMAGE, (150, 50), (25, 900), "Randomize"),  # Gemilerin konumunu rastgele ayarlayan düğme
    Button(BUTTON_IMAGE, (150, 50), (200, 900), "Reset"),  # Oyunu sıfırlayan düğme
    Button(BUTTON_IMAGE, (150, 50), (375, 900), "Start"),  # Oyunu başlatan (yerleştirme/savaş aşaması değiştiren) düğme
    Button(BUTTON_IMAGE, (150, 50), (550, 900), "Quit")  # Oyundan çıkmayı sağlayan düğme
]

RED_TOKEN = loadImage(os.path.join("assets", "images", "tokens", "redtoken.png"), (CELL_SIZE, CELL_SIZE))  # Kırmızı token (ıskalama) görüntüsünü yükle
GREEN_TOKEN = loadImage(os.path.join("assets", "images", "tokens", "greentoken.png"), (CELL_SIZE, CELL_SIZE))  # Yeşil token (isabet) görüntüsünü yükle
BBLUE_TOKEN = loadImage(os.path.join("assets", "images", "tokens", "bbluetoken.png"), (CELL_SIZE, CELL_SIZE))  # Alternatif token görüntüsü
RRED_TOKEN = loadImage(os.path.join("assets", "images", "tokens", "rredtoken.png"), (CELL_SIZE, CELL_SIZE))  # Alternatif token görüntüsü
TOKENS = []  # Hit/Miss tokenlerini saklamak için boş liste

# Grid görüntülerini ve arka planı yükle
PGAMEGRIDIMG = loadImage(os.path.join("assets", "images", "grids", "player_grid.png"), ((ROWS + 1) * CELL_SIZE, (COLS + 1) * CELL_SIZE))  # Oyuncu grid görüntüsünü yükle
CGAMEGRIDIMG = loadImage(os.path.join("assets", "images", "grids", "comp_grid.png"), ((ROWS + 1) * CELL_SIZE, (COLS + 1) * CELL_SIZE))  # Bilgisayar grid görüntüsünü yükle
BACKGROUND = loadImage(os.path.join("assets", "images", "background", "gamebg.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))  # Arka plan görüntüsünü yükle

# Ses efektlerini yükle ve SFX ses seviyelerini, ilgili değişkenlerle ayarla
HITSOUND = pygame.mixer.Sound(os.path.join("assets", "sounds", "explosion.wav"))  # Patlama ses efektini yükle
HITSOUND.set_volume(explosion_volume)  # Patlama sesinin ses seviyesini ayarla
SHOTSOUND = pygame.mixer.Sound(os.path.join("assets", "sounds", "gunshot.wav"))  # Nişancı ses efektini yükle
SHOTSOUND.set_volume(gunshot_volume)  # Nişancı sesinin ses seviyesini ayarla
MISSSOUND = pygame.mixer.Sound(os.path.join("assets", "sounds", "splash.wav"))  # Splash (ıskalama) ses efektini yükle
MISSSOUND.set_volume(splash_volume)  # Splash sesinin ses seviyesini ayarla

play_music()  # Arka plan müziğini çalmaya başla

player1 = Player()  # İnsan oyuncusu nesnesini oluştur
computer = EasyComputer()  # Bilgisayar rakibini temsil eden nesneyi oluştur

computer_stats["remaining"] = len(computerFleet)  # Bilgisayarın kalan gemi sayısını, gemi filosunun uzunluğuna eşitle
player_stats["remaining"] = len(playerFleet)  # Oyuncunun kalan gemi sayısını, gemi filosunun uzunluğuna eşitle

# ---------------- ANA OYUN DÖNGÜSÜ ---------------- #
running = True  # Oyun döngüsünü başlatmak için running True olarak ayarlanır
while running:  # Ana oyun döngüsü
    for event in pygame.event.get():  # Tüm olayları (klavye, fare vb.) işle
        if event.type == pygame.QUIT:  # Eğer kullanıcı pencereyi kapatma tuşuna basarsa
            running = False  # Oyun döngüsünü sonlandırmak için running'i False yap
        if event.type == RESTORE_MUSIC_VOLUME:  # Eğer özel müzik sesini eski haline getirme olayı gerçekleşirse
            pygame.mixer.music.set_volume(current_music_volume)  # Müzik sesini mevcut ses seviyesine ayarla
            pygame.time.set_timer(RESTORE_MUSIC_VOLUME, 0)  # Zamanlayıcıyı kapat
        if game_over:  # Eğer oyun bittiyse
            if event.type == pygame.MOUSEBUTTONDOWN:  # Fare tıklama olaylarını kontrol et
                for button in overlay_buttons:  # Overlay üzerindeki her düğme için döngü
                    if button.rect.collidepoint(pygame.mouse.get_pos()):  # Eğer tıklama düğme alanındaysa
                        if button.name == "Restart":  # Eğer düğme "Restart" ise
                            resetGame()  # Oyunu sıfırla
                        elif button.name == "Quit":  # Eğer düğme "Quit" ise
                            running = False  # Oyun döngüsünden çık
        else:  # Eğer oyun devam ediyorsa
            if event.type == pygame.MOUSEBUTTONDOWN:  # Fare tıklama olaylarını işle
                for button in BUTTONS:  # Ana arayüz düğmeleri üzerinde döngü
                    if button.rect.collidepoint(pygame.mouse.get_pos()):  # Tıklama düğme alanındaysa
                        button.actionOnPress()  # Düğmenin actionOnPress metodunu çağır
                        if button.name == "Quit":  # Eğer düğme "Quit" ise
                            running = False  # Oyundan çık
                sfx_area = pygame.Rect(500, SCREEN_HEIGHT - 250, 240, 200)  # SFX kontrolleri alanını tanımla
                if sfx_area.collidepoint(event.pos):  # Tıklama SFX alanı içerisindeyse
                    for key, rect in sfx_buttons.items():  # SFX düğmeleri üzerinde döngü
                        if rect.collidepoint(event.pos):  # Tıklama, ilgili düğme alanındaysa
                            # İlgili SFX ses seviyesini ayarla
                            if key == "Splash_VolDown":  # "Splash Ses Azalt" düğmesine basıldıysa
                                splash_volume = max(0.0, splash_volume - 0.01)  # splash_volume'u azalt, 0.0'ın altına düşmesin
                                MISSSOUND.set_volume(splash_volume)  # Splash sesini güncelle
                            elif key == "Splash_VolUp":  # "Splash Ses Artır" düğmesine basıldıysa
                                splash_volume = min(1.0, splash_volume + 0.01)  # splash_volume'u artır, 1.0'ın üstüne çıkmasın
                                MISSSOUND.set_volume(splash_volume)  # Splash sesini güncelle
                            elif key == "Explosion_VolDown":  # "Explosion Ses Azalt" düğmesine basıldıysa
                                explosion_volume = max(0.0, explosion_volume - 0.01)  # explosion_volume'u azalt
                                HITSOUND.set_volume(explosion_volume)  # Explosion sesini güncelle
                            elif key == "Explosion_VolUp":  # "Explosion Ses Artır" düğmesine basıldıysa
                                explosion_volume = min(1.0, explosion_volume + 0.01)  # explosion_volume'u artır
                                HITSOUND.set_volume(explosion_volume)  # Explosion sesini güncelle
                            elif key == "Gunshot_VolDown":  # "Gunshot Ses Azalt" düğmesine basıldıysa
                                gunshot_volume = max(0.0, gunshot_volume - 0.01)  # gunshot_volume'u azalt
                                SHOTSOUND.set_volume(gunshot_volume)  # Gunshot sesini güncelle
                            elif key == "Gunshot_VolUp":  # "Gunshot Ses Artır" düğmesine basıldıysa
                                gunshot_volume = min(1.0, gunshot_volume + 0.01)  # gunshot_volume'u artır
                                SHOTSOUND.set_volume(gunshot_volume)  # Gunshot sesini güncelle
                mp3_area = pygame.Rect(750, SCREEN_HEIGHT - 250, SCREEN_WIDTH - 780, 200)  # MP3 oynatıcı kontrol alanını tanımla
                if mp3_area.collidepoint(event.pos):  # Tıklama MP3 alanı içindeyse
                    btn_rects, song_rects = draw_mp3_player(GAME_SCREEN)  # MP3 oynatıcıyı yeniden çiz, düğme dikdörtgenlerini al
                    pos = event.pos  # Tıklama konumunu al
                    for key, rect in btn_rects.items():  # MP3 kontrol düğmeleri üzerinde döngü
                        if rect.collidepoint(pos):  # Tıklama düğme alanında ise
                            if key == "Prev":  # "Prev" düğmesine basıldıysa
                                prev_track()  # Önceki parçaya geç
                            elif key == "PlayPause":  # "PlayPause" düğmesine basıldıysa
                                if music_paused:  # Eğer müzik duraklatıldıysa
                                    unpause_music()  # Müzik devam etsin
                                else:
                                    pause_music()  # Müzik duraksın
                            elif key == "Next":  # "Next" düğmesine basıldıysa
                                next_track()  # Sonraki parçaya geç
                            elif key == "Vol-":  # Müzik için "Ses Azalt" düğmesine basıldıysa
                                current_music_volume = max(0.0, current_music_volume - 0.05)  # Müzik sesini azalt, 0.0'ın altına düşmesin
                                pygame.mixer.music.set_volume(current_music_volume)  # Müzik sesini güncelle
                            elif key == "Vol+":  # Müzik için "Ses Artır" düğmesine basıldıysa
                                current_music_volume = min(1.0, current_music_volume + 0.05)  # Müzik sesini artır, 1.0'ın üstüne çıkmasın
                                pygame.mixer.music.set_volume(current_music_volume)  # Müzik sesini güncelle
                    for idx, rect in song_rects.items():  # Parça isimleri dikdörtgenleri üzerinde döngü
                        if rect.collidepoint(pos):  # Tıklama, parça adı alanında ise
                            select_track(idx)  # O parçayı seç ve çal
                if event.button == 1:  # Sol fare düğmesine basıldıysa
                    if DEPLOYMENT:  # Eğer gemi yerleştirme aşamasındaysak
                        for ship in playerFleet:  # Oyuncunun gemileri üzerinde döngü
                            if ship.rect.collidepoint(pygame.mouse.get_pos()):  # Eğer gemiye tıklanmışsa
                                ship.active = True  # Gemiyi aktif (seçilmiş) olarak işaretle
                                sortFleet(ship, playerFleet)  # Seçilen gemiyi filonun sonuna taşı (çizim sırası için)
                                ship.selectShipAndMove()  # Gemiyi fare ile hareket ettirmesine izin ver
                    else:  # Deployment aşaması dışında (savaş aşaması)
                        if player1.turn:  # Ve oyuncunun sırasıysa
                            player1.makeAttack(computerGameGrid, computerGameLogic)  # Oyuncunun saldırısını işle
                elif event.button == 3:  # Sağ fare düğmesine basıldıysa
                    if DEPLOYMENT:  # Eğer yerleştirme aşamasındaysak
                        for ship in playerFleet:  # Oyuncunun gemileri üzerinde döngü
                            if ship.rect.collidepoint(pygame.mouse.get_pos()):  # Eğer gemiye tıklanmışsa
                                ship.rotateShip(True)  # Gemiyi hemen döndür
            elif event.type == pygame.KEYDOWN:  # Bir tuşa basıldığında
                if event.key == pygame.K_l:  # "L" tuşuna basıldıysa (hata ayıklama için)
                    printGameLogic()  # Güncel mantık grid'ini konsola yazdır
                    print("oyuncu tahtalarini terminalde gormek icin 'L' ye basildi")
    updateGameScreen(GAME_SCREEN)  # Tüm oyun elemanlarını güncelle ve yeniden çiz
    if not game_over and not DEPLOYMENT:  # Eğer oyun bitmemiş ve yerleştirme aşaması tamamlanmışsa
        takeTurns(player1, computer)  # Oyuncu ile bilgisayar arasında sıralamayı değiştir
pygame.quit()  # Oyun döngüsü sona erdiğinde pygame'i kapat
