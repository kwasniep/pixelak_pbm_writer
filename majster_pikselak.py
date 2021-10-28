import re

#zmienne globalne
dlugosc_tabulatora=9
odstep_miedzy_wierszami=1

#czytanie pliku konfiguracyjnego
plik_konfiguracyjny = open("pikselak_pbm_writer.ini","r",-1,"utf-8")
litery=[] #deklaracja glownej listy danych
grupy=[]
relacje=[]
indeks=0
tryb=""
rodzaj=""
linia=plik_konfiguracyjny.readline()
while linia:
    s=re.search("@@@(.+?)$",linia)
    if s:
        tryb=s.group(1)
    else:
        s=re.search("@@(.+?)$",linia)
        if s:
            rodzaj=s.group(1)
        else:
            s=re.search("(.+?)\t(.+?)(\t.+)*?$",linia)
            if s:
                if tryb=="litery":
                    litery.append({'id':indeks,'znak':s.group(1),'symbol':s.group(2),'rodzaj':rodzaj})
                    indeks+=1
                elif tryb=="grupy":
                    grupy.append([s.group(1),
                                  re.sub(' ','',s.group(2)).split(",")])
                elif tryb=="relacje":
                    relacje.append([s.group(1),
                                    re.sub(' ','',s.group(2)).split(",")])
    linia=plik_konfiguracyjny.readline()
plik_konfiguracyjny.close

#stworzenie slownikow id_znaku i id_symbolu
id_znaku={}
id_symbolu={}
for litera in litery:
    id_znaku[litera['znak']]=litera['id']
    id_symbolu[litera['symbol']]=litera['id']

# dodanie informacji o grupach
for grupa in grupy:
    for symbol in grupa[1]:
        litery[id_symbolu[symbol]]['grupa']=grupa[0]
for litera in litery:
    s = re.search("^_",litera['symbol'])
    if s:
        litera['grupa']="7"

# stworzenie slownika relacji
slownik_relacji={}
for relacja in relacje:
    for para in relacja[1]:
        slownik_relacji[para]=relacja[0]

# procedury
def znak_od(symbol):
    c=''
    a=id_symbolu.get(symbol)
    if a!=None:
        b=litery[a]
        if b:
            c=b.get('znak','')
    return c

def symbol_od(znak):
    c=''
    a=id_znaku.get(znak)
    if a!=None:
        b=litery[a]
        if b:
            c=b.get('symbol','')
    return c

def macierz_od(symbol):
    c=''
    a=id_symbolu.get(symbol)
    if a!=None:
        b=litery[a]
        if b:
            c=b.get('macierz','')
    return c

def cos_od_symbolu(cos,symbol):
    c=''
    a=id_symbolu.get(symbol)
    if a!=None:
        b=litery[a]
        if b:
            c=b.get(cos,'')
    return c

def zbadaj_relacje(poprzednia, nastepna):
    para = "-".join([str(poprzednia),str(nastepna)])
    return slownik_relacji.get(para, 'c')

def dolacz_macierz_poziomo(macierz_lewa, macierz_prawa, odstep=0): # odstep >= -1
    odstep=int(odstep)
    if len(macierz_lewa)==len(macierz_prawa):
        for i in range(len(macierz_lewa)):
            if odstep==-1:
                wspolny_element=max(int(macierz_lewa[i][len(macierz_lewa[i])-1]),
                                    int(macierz_prawa[i][0]))
                macierz_lewa[i][len(macierz_lewa[i])-1]=str(wspolny_element)
                for j in range(1,len(macierz_prawa[i])):
                    macierz_lewa[i].append(macierz_prawa[i][j])
            elif odstep>-1:
                for k in range(odstep):
                    macierz_lewa[i].append('0')
                macierz_lewa[i].extend(macierz_prawa[i])
        return True
    else:
        print('niezgodne ilosci wierszy macierzy')
        print(len(macierz_lewa),len(macierz_prawa))
        return False

def dolacz_macierz_pionowo(macierz_gorna, macierz_dolna, odstep=0): # odstep >= 0
    if macierz_dolna!= None:
        odstep=int(odstep)
        if not macierz_gorna[0]:
            for k in range(len(macierz_dolna[0])):
                macierz_gorna[0].append('0')
        dlugosc_wiersza=len(macierz_gorna[0])
        if odstep>=0 and dlugosc_wiersza==len(macierz_dolna[0]):
            pusty_wiersz=[]
            for k in range(dlugosc_wiersza):
                pusty_wiersz.append('0')
            for k in range(odstep):
                macierz_gorna.append(pusty_wiersz)
            macierz_gorna.extend(macierz_dolna)

def wymiar_macierzy(macierz):
    liczba_wierszy=len(macierz)
    if liczba_wierszy>0:
        liczba_kolumn=len(macierz[0])
    else:
        liczba_kolumn=0
    return [liczba_kolumn, liczba_wierszy]

def wymiar_mac_do_pbm(para):
    w,k=wymiar_macierzy(para)
    return ' '.join([str(w),str(k)])

def wymiar_pbm_do_mac(wymiar_string):
    liczba_kolumn, liczba_wierszy = wymiar_string.split(' ')
    return [int(liczba_wierszy), int(liczba_kolumn)]

def czytaj_pbm(nazwa_pliku):
    f=open(nazwa_pliku)
    caly_plik=f.readlines()
    f.close()
    if len(caly_plik)>2:
        file_type=re.findall(".+$",caly_plik[0])[0]
        if file_type=='P1':
            literka=re.findall('(?<=# ).+$',caly_plik[1])[0]
            wymiar=re.findall('.+$',caly_plik[2])[0]
            obrazek=[]
            for i in range(3,len(caly_plik)):
                obrazek.extend(re.findall('[0-1]',caly_plik[i]))
            [liczba_wierszy, liczba_kolumn]=wymiar_pbm_do_mac(wymiar)
            macierz=[]
            obi=0
            for i in range(liczba_wierszy):
                wiersz=[]
                for j in range(liczba_kolumn):
                    #print(nazwa_pliku)
                    wiersz.append(obrazek[obi])
                    obi+=1
                macierz.append(wiersz)
            return {'literka':literka,'macierz':macierz}

def pisz_strone_pbm(nazwa_pliku, o_strona_mat, komentarz_pbm="", limit=70):
    wym_mat=wymiar_macierzy(o_strona_mat)
    wym_pbm=wymiar_mac_do_pbm(o_strona_mat)
    limit=int(limit)    
    naglowek_pbm="P1\n# {0}\n{1}\n".format(komentarz_pbm,wym_pbm)
    #linearyzacja
    number_list=[]
    for linia in o_strona_mat:
        for piksel in linia:
            number_list.append(piksel)
    #ustawienie limitujacego konca linii
    i=0
    parts=[]
    for pozycja in number_list:
        i+=len(pozycja)+1
        if i<limit:
            nowa_pozycja="".join([pozycja,' '])
        else:
            nowa_pozycja="".join([pozycja,'\n'])
            i=0
        parts.append(nowa_pozycja)
    # join
    body_pbm=''.join(parts)
    plik_pbm_napis=''.join([naglowek_pbm,body_pbm])
    
    #print(plik_pbm_napis)
    f=open(nazwa_pliku,"w",-1)
    f.write(plik_pbm_napis)
    f.close()
        
# dodanie obrazkow
for litera in litery:
    s=litera['symbol']
    nazwa_pliku="".join(['pbm_abc\\',s,'.pbm'])
    pbm=czytaj_pbm(nazwa_pliku)
    if pbm['literka']==s:
        litera['macierz']=pbm['macierz']
    else:
        print('niezgodnosc symboli, w deklaracji',s,', w pliku',pbm['literka'])

#print("litery po dodaniu obrazkow:\n", litery) 

def czytaj_tekst(tekst):
    global dlugosc_tabulatora
    if not dlugosc_tabulatora:
        dlugosc_tabulatora=4
        
    tekstlista=[]
    poprzedni_znak=""
    for znak in tekst:
        bierz_nastepny=False
        if poprzedni_znak:
            symbol=symbol_od(''.join([poprzedni_znak,znak]))
            if symbol:
                tekstlista.append(symbol)
                bierz_nastepny=True
            else:
                symbol=symbol_od(''.join([poprzedni_znak,'?']))
                if symbol:
                    tekstlista.append(symbol)
                else:
                    kod_znaku=ord(poprzedni_znak)
                    tekstlista.append('__back_slash')
                    for cyfra in str(kod_znaku):
                        tekstlista.append(''.join(['_',str(cyfra)]))
                    tekstlista.append('__space')
                    bierz_nastepny=True
            poprzedni_znak=""
        if not poprzedni_znak and not bierz_nastepny:
            symbol=symbol_od(znak)
            symbol2=symbol_od(str(ord(znak)))
            if symbol:
                tekstlista.append(symbol)
            elif symbol2:
                tekstlista.append(symbol2)
            elif znak=='\t':
                for i in range(dlugosc_tabulatora):
                    tekstlista.append('_space')
            else:
                poprzedni_znak=znak
    return tekstlista

def tekstlista_ogarnij(tekstlista, max_linia, max_strona, uzyj_koncow_linii=False): #max_linia - max dlugosc linii w pikselach

    poprzedni_symbol=None
    odstep=0
    rozdzial=[]
    strona=[[],0]
    linia=[[],0]
    slowo=[[],0,False]  #slowo[2] -> isSpaceword

    for symbol in tekstlista:
        if uzyj_koncow_linii and symbol=="__new_line":
            if strona[1]+odstep_miedzy_wierszami+5>max_strona:
                rozdzial.append(strona)
                strona=[[],0]
                strona[0].append(linia)
                strona[1]+=odstep_miedzy_wierszami+5
                linia=[[],0]
            strona[0].append(linia)
            strona[1]+=odstep_miedzy_wierszami+5
            linia=[[],0]
            continue
        if poprzedni_symbol:
            relacja=zbadaj_relacje(cos_od_symbolu('grupa',poprzedni_symbol),
                                   cos_od_symbolu('grupa',symbol))
            odstep=ord(relacja)-ord('a')-1
        poprzedni_symbol=symbol
        szerokosc_symbolu=wymiar_macierzy(macierz_od(symbol))[0]
        if not symbol=='__space' and not slowo[2]:
            slowo[0].append([odstep,symbol,szerokosc_symbolu])
            slowo[1]+=odstep+szerokosc_symbolu
        elif symbol=='__space' and slowo[2]:
            linia[0].append(slowo)
            linia[1]+=slowo[1]
        elif symbol=='__space' and not slowo[2]:
            slowo[2]=True
            if linia[1]+slowo[1]>max_linia:
                if strona[1]+odstep_miedzy_wierszami+5>max_strona:
                    rozdzial.append(strona)
                    strona=[[],0]
                strona[0].append(linia)
                strona[1]+=odstep_miedzy_wierszami+5
                linia=[[],0]
            linia[0].append(slowo)
            linia[1]+=slowo[1]
            slowo=[[],0,True]
            slowo[0].append([odstep,symbol,szerokosc_symbolu])
            slowo[1]+=odstep+szerokosc_symbolu
        elif not symbol=='__space' and slowo[2]:
            if linia[1]+slowo[1]>max_linia:
                if strona[1]+odstep_miedzy_wierszami+5>max_strona:
                    rozdzial.append(strona)
                    strona=[[],0]
                strona[0].append(linia)
                strona[1]+=odstep_miedzy_wierszami+5
                linia=[[],0]
            linia[0].append(slowo)
            linia[1]+=slowo[1]
            slowo=[[],0,False]
            slowo[0].append([odstep,symbol,szerokosc_symbolu])
            slowo[1]+=odstep+szerokosc_symbolu

    if slowo[1]>0:
        linia[0].append(slowo)
        linia[1]+=slowo[1]
        if linia[1]+slowo[1]>max_linia:
            if strona[1]+odstep_miedzy_wierszami+5>max_strona:
                rozdzial.append(strona)
                strona=[[],0]
            strona[0].append(linia)
            strona[1]+=odstep_miedzy_wierszami+5
            linia=[[],0]
        slowo=[[],0,False]
    if linia[1]>0:
        strona[0].append(linia)
        strona[1]+=odstep_miedzy_wierszami+5
        linia=[[],0]
    strona[0].append(linia)
    strona[1]+=odstep_miedzy_wierszami+5
    rozdzial.append(strona)
    strona=[[],0]

    return rozdzial

def ogarniety_wiersz_do_macierzy(o_wiersz):
    o_wiersz_mat=[[],[],[],[],[]]
    for slowo in o_wiersz:
        for o_znak in slowo[0]:
            odstep=o_znak[0]
            symbol=o_znak[1]
            macierz_prawa=macierz_od(symbol)
            rezultat=dolacz_macierz_poziomo(o_wiersz_mat,macierz_prawa,odstep)
            if not rezultat:
                print("znak", o_znak,"wywolal blad")
    return o_wiersz_mat

def polacz_i_formatuj_wiersze(lista_o_wiersz_mat,wyrownanie):

    #wyrownanie "lewo" "srodek" "prawo"
    lista_dlugosci=[]
    macierz_odstepu=['0','0','0','0','0']
    
    for o_wiersz_mat in lista_o_wiersz_mat:
        lista_dlugosci.append(len(o_wiersz_mat[0]))
    maksymalna_dlugosc_wiersza=max(lista_dlugosci)

    #formatowanie wierszy
    lista_sformatowanych_o_wiersz_mat=[]
    for o_wiersz_mat in lista_o_wiersz_mat:
        o_wiersz_z_formatem=[]
        niedobor=maksymalna_dlugosc_wiersza-len(o_wiersz_mat[0])
        if wyrownanie=="lewo":
            o_wiersz_z_formatem.extend(o_wiersz_mat)
            for i in range(niedobor):
                dolacz_macierz_poziomo(o_wiersz_z_formatem,macierz_odstepu)
        elif wyrownanie=="srodek":
            lewy_niedobor=int(niedobor/2)
            prawy_niedobor=niedobor-lewy_niedobor
            if lewy_niedobor:
                lewy_margines=[]
                lewy_margines.extend(macierz_odstepu)
                for i in range(1,lewy_niedobor):
                    dolacz_macierz_poziomo(lewy_margines,macierz_odstepu)
                o_wiersz_z_formatem.extend(lewy_margines)
            o_wiersz_z_formatem.extend(o_wiersz_mat)
            for i in range(prawy_niedobor):
                dolacz_macierz_poziomo(o_wiersz_z_formatem,macierz_odstepu)
        elif wyrownanie=="prawo":
            if niedobor:
                lewy_margines=[]
                lewy_margines.extend(macierz_odstepu)
                for i in range(1,niedobor):
                    dolacz_macierz_poziomo(lewy_margines,macierz_odstepu)
                o_wiersz_z_formatem.extend(lewy_margines)
            o_wiersz_z_formatem.extend(o_wiersz_mat)
        lista_sformatowanych_o_wiersz_mat.append(o_wiersz_z_formatem)
    #laczenie sformatowanych wierszy
    o_strona_mat=[[]]
    for s_wiersz_mat in lista_sformatowanych_o_wiersz_mat:
        dolacz_macierz_pionowo(o_strona_mat,s_wiersz_mat,odstep_miedzy_wierszami)
    return o_strona_mat

### CZĘŚĆ GŁÓWNA PROGRAMU ###

plik_z_tekstem=open("tekst.txt","r",-1,"utf-8")
tekst=plik_z_tekstem.read()
plik_z_tekstem.close

a=tekst

#  a="Ala ma dziką klacz na podwórzu"
#  to byl pierwszy napis
#  na nim preprowadzalem wszystkie najwazniejsze testy :)

b=czytaj_tekst(a)
rozdzial=tekstlista_ogarnij(b, 280,340, True)

#d=ogarniety_wiersz_do_macierzy(c[0][0][0][0])
#e=polacz_i_formatuj_wiersze([rozdzial],"lewo") 

def rozdzial_do_pbm(rozdzial):
    nr_strony=0    
    for strona in rozdzial:
        lista_wierszy=strona[0]
        nr_strony+=1
        lista_mat_strona=[]
        for wiersz in lista_wierszy:
            mat_wiersz=ogarniety_wiersz_do_macierzy(wiersz[0])
            lista_mat_strona.append(mat_wiersz)
        do_zapisu=polacz_i_formatuj_wiersze(lista_mat_strona,"lewo")
        komentarz=" ".join(['strona:',str(nr_strony)])
        nazwa_pliku="".join(['wynik','-','strona',str(nr_strony),'.pbm'])
        pisz_strone_pbm(nazwa_pliku,do_zapisu,komentarz)
rozdzial_do_pbm(rozdzial)

#print()
#print(a)
#print(b)
#print(c)
#print(d)
#print(e)



