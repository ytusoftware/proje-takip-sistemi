#SYSTEM FLOW CONTROL
####################

#######################################################################################################################
#ONEMLI NOT: Sadece PROCESS_2 VE PROCESS_3 paralel yurutulebilir. Diger tum surecler birbirinden ayri yurutulmelidir
#######################################################################################################################


#Akademisyen proje oneri gonderme sureci
#Ogrenci arkadas ekleme sureci
PROCESS_1 = True

#Ogrenci proje basvuru yapma/silme sureci
PROCESS_2 = True

#Akademisyen proje basvuru degerlendirme sureci
PROCESS_3 = True

#Form-2 gonderme sureci
PROCESS_4 = True

#Form-2 akademisyen onayi sureci
PROCESS_5 = True

#Form-2 kurul onayi sureci
PROCESS_6 = True

#Rapor gonderme sureci
PROCESS_7 = True


#Ogrenci devam karari sureci (Bu surec sistem sifirlanana kadar devam etmelidir, bir sonraki donem baslangicina kadar)
PROCESS_8 = True
