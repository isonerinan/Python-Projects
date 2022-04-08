while True:
    ilkSayi = float(input("İlk sayıyı giriniz: "))
    islem = input("İşlemi giriniz: ")

    if islem != "+" and islem != "-" and islem != "*" and islem != "/" and islem != "x":
        print("Yanlış bir işlem girdiniz.")
        break

    ikinciSayi = float(input("İkinci sayıyı giriniz: "))

    if islem == "+":
        sonuc = ilkSayi + ikinciSayi

    elif islem == "-":
        sonuc = ilkSayi - ikinciSayi

    elif islem == "*" or islem == "x":
        sonuc = ilkSayi * ikinciSayi

    elif islem == "/":
        sonuc = ilkSayi / ikinciSayi

    print(sonuc)

    while True:
        yeniIslem = input("Yeni işlem? (evet veya e, hayır veya h)")
        if yeniIslem == "hayır" or yeniIslem == "h":
            break

        if yeniIslem == "evet" or yeniIslem == "e":
            break

        else:
            print("hatalı giriş")

    if yeniIslem == "hayır" or yeniIslem == "h":
        break