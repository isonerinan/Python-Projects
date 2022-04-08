kalinanSaat = float(input("Otoparkta kaç saat kaldınız? "))

if kalinanSaat <= 1:
    ucret = 5

elif 1 < kalinanSaat <= 5:
    ucret = kalinanSaat * 4

elif kalinanSaat > 5:
    ucret = kalinanSaat * 3

print(ucret, "TL ödemelisiniz.")