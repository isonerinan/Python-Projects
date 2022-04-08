# Hem 2'ye hem 3'e bölünebilmek, 6'ya bölünebilme kuralıdır.

ikiBol = []
ucBol = []
altiBol = []

i = 1

while i <= 100:
    if i % 2 == 0:
        ikiBol.append(i)

    if i % 3 == 0:
        ucBol.append(i)

    if i % 2 == 0 and i % 3 == 0:
        altiBol.append(i)

    i += 1

print("2'ye bölünenler:", ikiBol, "\n3'e bölünenler:", ucBol, "\nHem 2 hem 3'e bölünenler:", altiBol)