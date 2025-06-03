import random


class Przedmiot:
    def __init__(self, nazwa, opis):
        self.nazwa = nazwa
        self.opis = opis

    def opisz(self):
        return f"{self.nazwa}: {self.opis}"



class Klucz(Przedmiot):
    def __init__(self, nazwa, opis):
        super().__init__(nazwa, opis)



class Skarb(Przedmiot):
    def __init__(self, nazwa, opis, wartosc):
        super().__init__(nazwa, opis)
        self.wartosc = wartosc

    def opisz(self):
        return f"{self.nazwa}: {self.opis} (Wartość: {self.wartosc} pkt)"



class Przejscie:
    def __init__(self, kierunek, komnata_docelowa):
        self.kierunek = kierunek
        self.komnata_docelowa = komnata_docelowa

    def przejdz(self):
        return self.komnata_docelowa



class Drzwi(Przejscie):
    def __init__(self, kierunek, komnata_docelowa, pasujacy_klucz, kierunek2, komnata_docelowa2):
        super().__init__(kierunek, komnata_docelowa)
        self.pasujacy_klucz = pasujacy_klucz
        self.kierunek2 = kierunek2
        self.komnata_docelowa2 = komnata_docelowa2
        self.otwarte = False


    def otworz(self, gracz):
        if self.otwarte:
            print("Drzwi są już otwarte.")
            return

        for przedmiot in gracz.inwentarz:
            if przedmiot == self.pasujacy_klucz:
                self.otwarte = True
                print("Drzwi zostały otwarte.")
                return
        print("Nie masz odpowiedniego klucza do tych drzwi.")


    def zamknij(self):
        if not self.otwarte:
            print("Drzwi są już zamknięte.")
            return

        self.otwarte = False
        print("Drzwi zostały zamknięte.")


    def czy_otwarte(self):
        return self.otwarte


    def przejdz(self, obecna_komnata=None):
        if not self.otwarte:
            return
        if obecna_komnata == self.komnata_docelowa2:
            return self.komnata_docelowa
        elif obecna_komnata == self.komnata_docelowa:
            return self.komnata_docelowa2
        return


class PrzejscieNaPunkty(Przejscie):
    def __init__(self, kierunek, komnata_docelowa, prog_punktow):
        super().__init__(kierunek, komnata_docelowa)
        self.prog_punktow = prog_punktow


    def przejdz(self, gracz=None):
        if not self.czy_przejscie(gracz):
            return

        return self.komnata_docelowa

    def czy_przejscie(self, gracz=None):
        return gracz.liczba_punktow() >= self.prog_punktow



class Komnata:
    def __init__(self, nazwa, opis):
        self.nazwa = nazwa
        self.opis = opis
        self.przedmioty = []
        self.przejscia = []
        self.stworzenia = []


    def dodaj_przedmiot(self, przedmiot):
        self.przedmioty.append(przedmiot)


    def usun_przedmiot(self, nazwa):
        for p in self.przedmioty:
            if p.nazwa == nazwa:
                self.przedmioty.remove(p)
                return p
        return


    def opisz(self, gracz):
        opis = f"\n{self.nazwa}: {self.opis}\n"
        if self.przedmioty:
            opis += "Przedmioty: " + ", ".join(p.nazwa for p in self.przedmioty) + "\n"
        if self.przejscia:
            opis += "Wyjścia: "
            for p in self.przejscia:
                if isinstance(p, Drzwi):
                    status = "otwarte" if p.otwarte else "zamknięte"
                    if self == p.komnata_docelowa:
                        kierunek = p.kierunek2
                    else:
                        kierunek = p.kierunek
                    if status == "otwarte":
                        opis += f"drzwi w kierunku: {kierunek} ({status}), "
                    else:
                        opis += f"drzwi w kierunku: {kierunek} ({status} - pasujący klucz: {p.pasujacy_klucz.nazwa}), "
                elif isinstance(p, PrzejscieNaPunkty):
                    status = "otwarte" if p.czy_przejscie(gracz) else "zamknięte"
                    if status == "otwarte":
                        opis += f"magiczne przejście w kierunku: {p.kierunek} ({status}), "
                    else:
                        opis += f"magiczne przejście w kierunku: {p.kierunek} ({status} - potrzebujesz {p.prog_punktow} punktów), "
                else:
                    opis += f"przejście w kierunku: {p.kierunek}, "
            opis = opis.rstrip(", ") + "\n"
        if self.stworzenia:
            opis += "Stworzenia: " + ", ".join(["Złodziej"] * len(self.stworzenia)) + "\n"
        return opis



class Stworzenie:
    def __init__(self, komnata_poczatkowa):
        self.komnata_aktualna = komnata_poczatkowa

    def ruch_losowy(self):
        # 30% szans na pozostanie w miejscu
        if random.random() < 0.3:
            return

        mozliwe_przejscia = [p for p in self.komnata_aktualna.przejscia if (not isinstance(p, Drzwi) and not isinstance(p, PrzejscieNaPunkty))
                             or (isinstance(p, Drzwi) and p.czy_otwarte())]
        if mozliwe_przejscia:
            przejscie = random.choice(mozliwe_przejscia)
            nowa_komnata = przejscie.przejdz(self.komnata_aktualna) if isinstance(przejscie, Drzwi) else przejscie.przejdz()
            if nowa_komnata:
                self.komnata_aktualna.stworzenia.remove(self)
                self.komnata_aktualna = nowa_komnata
                self.komnata_aktualna.stworzenia.append(self)

    @staticmethod
    def spotkaj_gracza(gracz, wszystkie_komnaty):
        if random.random() < 0.2:  # 20% szans na kradzież skarbu
            skarby_gracza = [obiekt for obiekt in gracz.inwentarz if isinstance(obiekt, Skarb)]
            if skarby_gracza:
                ukradziony = random.choice(skarby_gracza)
                gracz.inwentarz.remove(ukradziony)
                print(f"Złodziej ukradł ci: {ukradziony.nazwa}!")

                obecna_komnata = gracz.aktualna_komnata
                inne_komnaty = [k for k in wszystkie_komnaty if k != obecna_komnata and k.nazwa != "Świątynia Skarbów"]
                nowa_komnata = random.choice(inne_komnaty)
                nowa_komnata.przedmioty.append(ukradziony)
                print(f"Skarb pojawił się w innej komnacie: {nowa_komnata.nazwa}.")
            else:
                print("Złodziej chciał coś ukraść, ale nie masz nic w inwentarzu.")
        else:
            print("Złodziej obserwuje cię, ale nie podejmuje żadnych działań.")


class Gracz:
    def __init__(self, komnata_poczatkowa):
        self.aktualna_komnata = komnata_poczatkowa
        self.inwentarz = []

    def przejdz(self, kierunek):
        for p in self.aktualna_komnata.przejscia:
            if isinstance(p, Drzwi):
                if ((p.komnata_docelowa == self.aktualna_komnata and p.kierunek2 == kierunek) or
                        (p.komnata_docelowa2 == self.aktualna_komnata and p.kierunek == kierunek)):

                    if p.czy_otwarte():
                        nowa_komnata = p.przejdz(self.aktualna_komnata)
                        if nowa_komnata:
                            self.aktualna_komnata = nowa_komnata
                            print(f"Przeszedłeś do {nowa_komnata.nazwa}.")
                            return True
                    else:
                        print("Drzwi są zamknięte.")
                        print(f"Potrzebujesz klucza: {p.pasujacy_klucz.nazwa}.")
                    return False

            elif isinstance(p, PrzejscieNaPunkty) and p.kierunek == kierunek:
                if p.czy_przejscie(self):
                    nowa_komnata = p.przejdz(self)
                    if nowa_komnata:
                        self.aktualna_komnata = nowa_komnata
                        print(f"Przeszedłeś do {nowa_komnata.nazwa}.")
                        return True
                else:
                    print("Magiczne przejście jest zamknięte.")
                    print(f"Potrzebujesz {p.prog_punktow} punktów.")
                return False

            elif p.kierunek == kierunek:
                self.aktualna_komnata = p.przejdz()
                print(f"Przeszedłeś do {self.aktualna_komnata.nazwa}.")
                return True

        print("Nie ma przejścia w tym kierunku.")
        return False


    def otworz_drzwi(self, kierunek):
        for p in self.aktualna_komnata.przejscia:
            if isinstance(p, Drzwi):
                if ((p.komnata_docelowa == self.aktualna_komnata and p.kierunek2 == kierunek) or
                        (p.komnata_docelowa2 == self.aktualna_komnata and p.kierunek == kierunek)):
                    p.otworz(self)
                    return
        print("Nie ma drzwi w tym kierunku.")


    def rozejrzyj_sie(self):
        print(self.aktualna_komnata.opisz(self))


    def sprawdz(self, nazwa):
        for p in self.aktualna_komnata.przedmioty + self.inwentarz:
            if p.nazwa == nazwa:
                print(p.opisz())
                return
        print("Nie znaleziono przedmiotu.")


    def wez(self, nazwa):
        przedmiot = self.aktualna_komnata.usun_przedmiot(nazwa)
        if przedmiot:
            self.inwentarz.append(przedmiot)
            print(f"Wzięto: {nazwa}.")
        else:
            print("Nie ma takiego przedmiotu.")


    def poloz(self, nazwa):
        for p in self.inwentarz:
            if p.nazwa == nazwa:
                self.inwentarz.remove(p)
                self.aktualna_komnata.dodaj_przedmiot(p)
                print(f"Położono: {nazwa}.")
                return
        print("Nie masz takiego przedmiotu.")


    def liczba_punktow(self):
        return sum(p.wartosc for p in self.inwentarz if isinstance(p, Skarb))


    def pokaz_inwentarz(self):
        if self.inwentarz:
            print("Masz w inwentarzu:")
            for p in self.inwentarz:
                print(f"- {p.nazwa}")
        else:
            print("Twój inwentarz jest pusty.")


class Mapa:
    def __init__(self):
        self.komnaty = {}
        self.stworzenia = []
        self.gracz = None

    def zbuduj(self):

        # Tworzenie komnat
        przeznaczenia = Komnata("Sala Przeznaczenia", "Monumentalna sala o sklepieniu pokrytym freskami przedstawiającymi przyszłość każdego, kto ją przekroczy.")
        rycerza = Komnata("Pokój Rycerza", "Atmosfera odwagi i walki wypełnia powietrze tej komnaty.")
        zaklec = Komnata("Komnata Zaklęć", "Wypełniona unoszącymi się w powietrzu księgami i migoczącymi runami.")
        zludzen = Komnata("Sala Złudzeń", "Nic nie jest tym, czym się wydaje. Lustra, wirujące obrazy i zmieniające się iluzje sprawiają, że gość łatwo traci zmysły.")
        cieni = Komnata("Wieża Cieni", "Wysoka, spiralna wieża spowita wiecznym półmrokiem.")
        snu = Komnata("Komnata Snu", "Spokojne, nieziemskie miejsce, gdzie czas płynie inaczej.")
        szeptow = Komnata("Ogród Szeptów", "Tajemniczy ogród pełen egzotycznych roślin i szeptów dobiegających z każdego liścia.")
        bastion = Komnata("Zimowy Bastion", "Lodowa forteca na końcu świata. Zamrożona w czasie, kryje zimowe duchy i tajemnice pradawnej wojny.")
        poprzednia = Komnata("Sala Poprzednia", "Prosta, kamienna sala z magicznymi drzwiami – bez klucza, bez mechanizmu. Drzwi otworzą się tylko tym, którzy zdobyli wszystkie pozostałe skarby.")
        skarbow = Komnata("Świątynia Skarbów", "Olbrzymia świątynia wykuta z kryształów i obsydianu. Pośrodku wznosi się ołtarz, a na nim spoczywa największy skarb.")


        # Dodanie komnat do słownika
        self.komnaty = {
            "przeznaczenia": przeznaczenia,
            "rycerza": rycerza,
            "zaklec": zaklec,
            "zludzen": zludzen,
            "cieni": cieni,
            "snu": snu,
            "szeptow": szeptow,
            "bastion": bastion,
            "poprzednia": poprzednia,
            "skarbow": skarbow
        }

        # Tworzenie kluczy
        klucz_niebieski = Klucz("Klucz Niebieski", "Chłodny w dotyku, połyskuje jak tafla jeziora o świcie.")
        klucz_zolty = Klucz("Klucz Żółty", "Lśni jak promień słońca, wydaje się lekki, ale solidny.")
        klucz_czerwony = Klucz("Klucz Czerwony", "Ciężki i masywny, ma wyryty symbol ognia.")
        klucz_zielony = Klucz("Klucz Zielony", "Pachnie delikatnie mchem, zrobiony jakby z żywej rośliny.")
        klucz_bialy = Klucz("Klucz Biały", "Matowy i tajemniczy, jakby wykuty z lodu lub kości.")
        klucz_fioletowy = Klucz("Klucz Fioletowy", "Emituje subtelny blask, sprawia wrażenie magicznego.")

        # Dodanie kluczy do komnat
        przeznaczenia.dodaj_przedmiot(klucz_niebieski)
        rycerza.dodaj_przedmiot(klucz_zolty)
        zaklec.dodaj_przedmiot(klucz_czerwony)
        zludzen.dodaj_przedmiot(klucz_zielony)
        snu.dodaj_przedmiot(klucz_bialy)
        bastion.dodaj_przedmiot(klucz_fioletowy)

        # Tworzenie skarbów
        skarb_przeznaczenia = Skarb("Zwierciadło Wglądu", "lustro, które ukazuje przyszłość właściciela, ale tylko raz w życiu.", 50)
        skarb_rycerza = Skarb("Ostrze Cienia", "Magiczny miecz, który staje się niewidzialny podczas walki.", 150)
        skarb_zaklec = Skarb("Księga Zapomnianych Zaklęć", "Zawiera czary, których nie zapisano w żadnym innym tomie.", 50)
        skarb_zludzen = Skarb("Złudny Skarb", "Skarb, który nie jest skarbem", 0)
        skarb_cieni = Skarb("Płaszcz Nocy", "Pozwala użytkownikowi poruszać się niezauważenie w ciemności.", 100)
        skarb_szeptow = Skarb("Szepczący Kwiat", "Kwiat, który wyszepcze ci całą prawdę.", 50)
        skarb_bastion = Skarb("Serce Lodu", "Artefakt zdolny zatrzymać czas na krótką chwilę.", 100)
        skarb_skarbow = Skarb("Korona Życzeń", "Legendarny artefakt spełniający jedno DOWOLNE życzenie właściciela, o ile nie narusza ono porządku świata.", 500)


        # Dodanie skarbów do komnat
        przeznaczenia.dodaj_przedmiot(skarb_przeznaczenia)
        rycerza.dodaj_przedmiot(skarb_rycerza)
        zaklec.dodaj_przedmiot(skarb_zaklec)
        zludzen.dodaj_przedmiot(skarb_zludzen)
        cieni.dodaj_przedmiot(skarb_cieni)
        szeptow.dodaj_przedmiot(skarb_szeptow)
        bastion.dodaj_przedmiot(skarb_bastion)
        skarbow.dodaj_przedmiot(skarb_skarbow)


        # Tworzenie oraz dodanie przejść i drzwi
        drzwi1 = Drzwi("północ", przeznaczenia, klucz_zielony,"południe", zludzen)
        zludzen.przejscia.append(drzwi1)
        przeznaczenia.przejscia.append(drzwi1)

        przejscie1 = Przejscie("zachód", zaklec)
        zludzen.przejscia.append(przejscie1)
        przejscie2 = Przejscie("wschód", zludzen)
        zaklec.przejscia.append(przejscie2)

        drzwi2 = Drzwi("wschód", cieni, klucz_czerwony,"zachód", zludzen)
        zludzen.przejscia.append(drzwi2)
        cieni.przejscia.append(drzwi2)

        przejscie3 = Przejscie("wschód", rycerza)
        przeznaczenia.przejscia.append(przejscie3)
        przejscie4 = Przejscie("zachód", przeznaczenia)
        rycerza.przejscia.append(przejscie4)

        drzwi3 = Drzwi("południe", szeptow, klucz_niebieski,"północ", zludzen)
        zludzen.przejscia.append(drzwi3)
        szeptow.przejscia.append(drzwi3)

        przejscie5 = Przejscie("południe", snu)
        zaklec.przejscia.append(przejscie5)
        przejscie6 = Przejscie("północ", zaklec)
        snu.przejscia.append(przejscie6)

        drzwi4 = Drzwi("południe", bastion, klucz_zolty,"północ", cieni)
        cieni.przejscia.append(drzwi4)
        bastion.przejscia.append(drzwi4)

        drzwi5 = Drzwi("wschód", szeptow, klucz_bialy,"zachód", snu)
        snu.przejscia.append(drzwi5)
        szeptow.przejscia.append(drzwi5)

        drzwi6 = Drzwi("południe", poprzednia, klucz_fioletowy,"północ", szeptow)
        szeptow.przejscia.append(drzwi6)
        poprzednia.przejscia.append(drzwi6)

        przejscie7 = PrzejscieNaPunkty("wschód", skarbow, 500)
        przejscie8 = Przejscie("zachód", poprzednia)
        skarbow.przejscia.append(przejscie8)
        poprzednia.przejscia.append(przejscie7)


        # Tworzenie stworzeń
        stworzenie_1 = Stworzenie(snu)
        stworzenie_2 = Stworzenie(rycerza)

        # Dodanie stworzeń do komnat
        stworzenie_1.komnata_aktualna.stworzenia.append(stworzenie_1)
        stworzenie_2.komnata_aktualna.stworzenia.append(stworzenie_2)

        self.stworzenia = [stworzenie_1, stworzenie_2]

        # Ustawienie gracza w "Sali Złudzeń"
        self.gracz = Gracz(zludzen)


class Rozgrywka:
    def __init__(self):
        self.mapa = Mapa()
        self.mapa.zbuduj()

    def wykonaj_polecenie(self, wejscie):

        try:
            czesci = wejscie.strip().split(maxsplit=1)
            polecenie = czesci[0]
            argument = czesci[1] if len(czesci) > 1 else ""
        except IndexError:
            print("Błąd przetwarzania polecenia.")
            return True

        self.ruch_stworzen()

        if polecenie == "rozejrzyj":
            self.mapa.gracz.rozejrzyj_sie()
        elif polecenie == "sprawdź":
            self.mapa.gracz.sprawdz(argument)
        elif polecenie == "weź":
            self.mapa.gracz.wez(argument)
        elif polecenie == "połóż":
            self.mapa.gracz.poloz(argument)
        elif polecenie == "przejdź":
            if self.mapa.gracz.przejdz(argument):
                self.wyswietl_mape()
        elif polecenie == "otwórz":
            self.mapa.gracz.otworz_drzwi(argument)
        elif polecenie == "inwentarz":
            self.mapa.gracz.pokaz_inwentarz()
        elif polecenie == "punkty":
            print(f"Aktualna liczba punktów: {self.mapa.gracz.liczba_punktow()}.")
        elif polecenie == "koniec":
            return False
        else:
            print("Nieznane polecenie.")

        for stworzenie in self.mapa.gracz.aktualna_komnata.stworzenia:
            stworzenie.spotkaj_gracza(self.mapa.gracz, self.mapa.komnaty.values())
        return True


    def ruch_stworzen(self):
        for stworzenie in self.mapa.stworzenia:
            stworzenie.ruch_losowy()


    def uruchom(self):
        print("Witamy w grze Labirynt!")
        print("Zbierz wszystkie skarby, uciekaj przed złodziejami, by dostać się do Świątyni Skarbów i spełnić swoje życzenie.")
        print(
            "Dostępne komendy: rozejrzyj, sprawdź [przedmiot], weź [przedmiot], połóż [przedmiot], przejdź [kierunek], otwórz [kierunek], inwentarz, punkty, koniec.")
        self.wyswietl_mape()

        while True:
            wejscie = input("> ")

            if len(wejscie) == 0:
                print("Wpisz polecenie.")
                continue

            if not self.wykonaj_polecenie(wejscie):
                break

        print(f"Dziękujemy za grę!")
        print(f"Zdobyłeś {self.mapa.gracz.liczba_punktow()} punktów na 1000 możliwych.")
        ma_korone = any(obiekt.nazwa == "Korona Życzeń" for obiekt in self.mapa.gracz.inwentarz)

        if ma_korone:
            print("Udało ci się zdobyć główny skarb! Teraz spełni się dowolne Twoje życzenie!")
        else:
            print("Niestety, nie udało Ci się zdobyć głównego skarbu.")


    def wyswietl_mape(self):
        aktualna = self.mapa.gracz.aktualna_komnata.nazwa

        def znacznik(nazwa):
            return f"[X] {nazwa}" if nazwa == aktualna else f"[ ] {nazwa}"

        print("\nMAPA PODZIEMI:\n")

        print(" " * 22 + znacznik("Sala Przeznaczenia") + "───" + znacznik("Pokój Rycerza"))
        print(" " * 38 + "│")
        print(" " * 9 + znacznik("Komnata Zaklęć") + "───" + znacznik("Sala Złudzeń") + "───" + znacznik("Wieża Cieni"))
        print(" " * 20 + "│" + " " * 15 + "│" + " " * 20 + "│")
        print(" " * 9 + znacznik("Komnata Snu") + "───" + znacznik("Ogród Szeptów") + "   " + znacznik("Zimowy Bastion"))
        print(" " * 35 + "│")
        print(" " * 22 + znacznik("Sala Poprzednia") + "───" + znacznik("Świątynia Skarbów"))
        print()


if __name__ == "__main__":
    Rozgrywka().uruchom()

