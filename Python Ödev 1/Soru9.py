yil = int(input("Lütfen doğum yılınızı giriniz: "))

yas = 2021 - yil

if yil > 2021:
    print("Gelecekten geldiğine göre bilirsin, hangi kriptoparaya yatırım yapayım?")

elif 2015 <= yil <= 2021:
    print("Agu bugu sen yazmayı ne ara öğrendin?", yas, "yaşındasın.")

else:
    print(yas, "yaşındasınız.")