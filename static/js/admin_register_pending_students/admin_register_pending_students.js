function pass_func(template_values_curr) {
        $(document).ready(function() {


                /*PAGING*/

                //bulunulan sayfa set edilir
                $("#pagenum").text((template_values_curr["init_page_num"]).toString());


                //Paging icin enable-disable
                if (template_values_curr["disable_next_page"]) {
                        $("#pagenext-li").attr("class", "page-item disabled");

                } else {
                        $("#pagenext-li").attr("class", "page-item");

                }

                if (template_values_curr["init_page_num"] == 1) {
                        $("#pageprev-li").attr("class", "page-item disabled");

                } else {
                        $("#pageprev-li").attr("class", "page-item");
                }


                //İleri ve geri butonlari icin bulunulan sayfaya gore guncellemeler
                var init_page_num = template_values_curr["init_page_num"]

                updated_prev_page_url = "/admin/register_pending_students?page=" + (init_page_num - 1).toString();
                $("#pageprev").attr("href", updated_prev_page_url);

                updated_next_page_url = "/admin/register_pending_students?page=" + (init_page_num + 1).toString();
                $("#pagenext").attr("href", updated_next_page_url);



                /*OGRENCI LISTELEME*/

                student_list = template_values_curr["students"];


                //Sunucudan gelen proje listesi gosterilir (varsa)
                if (student_list!=null && student_list[0]!=null) {

                        student_list.forEach(function(student, index) {
                                $("#students").append(
                                        '<li name="be_deleted" class="list-group-item">' +
                                                '<label>' + student[0] + '</label>' +
                                                '<button type="button" name="delete_button" class="btn btn-danger float-right">Sil</button>'+
                                                '<button type="button" name="confirm_button" class="btn btn-success float-right mr-2">Onayla</button>'+
                                        '</li>'
                                );
                        });

                }

                //Ogrenci başvurusu yoksa
                else {

                        $("#title").after('<div class="ml-2 alert alert-warning" role="alert">'+
                                                '<h4 class="alert-heading">Onay bekleyen öğrenci hesabı bulunmamaktadır!</h4>');


                        $("[name='be_deleted']").remove();


                }




                /*OGRENCI ARAMA*/

                $("#search-box").keyup(function(){
                        //Arama kutusuna girilen pattern ile regular expression nesnesi olusturuluyor
                        pattern = $(this).prop("value");
                        //Case sensitive olmayan arama yapabilmek icin
                        pattern = pattern.toUpperCase();
                        var re = new RegExp(pattern);

                        $("#students li").each(function(){
                                //Mevcut liste elemanı (li) icindeki proje adı ve proje tipinde arama kutusundan girilen deger ile eslesme bulma
                                var student_no = $(this).find("label").text().toUpperCase();

                                //Pattern icermeyen liste elemanlari gizlenir
                                if ( student_no.match(re)) {
                                        $(this).show();
                                }
                                else {
                                        $(this).hide();
                                }
                        });
                });




                /*BASVURU SILME ISLEMI*/

                var project_id; //Silinmek istenen projenin id'si bu degiskene cekilecek
                var parent_element; //Silinecek liste elemani


                //Modal penceresinden onay gelirse asil silme islemi yapilir
                $("[name='delete_button']").click(function(){

                        //Tıklanan butondan ana liste elemanina ulasilir
                        var parent_element = $(this).parent();

                        //Hidden input ile gizlenen proje id sine ulasilir
                        var student_no = parent_element.find("label").text();


                        //Sunucu tarafına AJAX call yapilir ve islem basarisi cevabi alinir
                        $.get("/admin/reject_registration?student_no="+student_no, function(data, status){

                                var response = JSON.parse(data);
                                parent_element.remove();

                        });
                });


                /* OGRENCI HESABI AKTIFLESTIRME ISLEMI*/

                $("[name='confirm_button']").click(function(){

                        //Tıklanan butondan ana liste elemanina ulasilir
                        var parent_element = $(this).parent();

                        //Hidden input ile gizlenen proje id sine ulasilir
                        var student_no = parent_element.find("label").text();

                        parent_element.find("[name='confirm_button']").remove();
                        parent_element.find("[name='delete_button']").remove();
                        parent_element.append('<div class="spinner-border text-success float-right"></div>');

                        //Sunucu tarafına AJAX call yapilir ve islem basarisi cevabi alinir
                        $.get("/admin/confirm_registration?op_type=single&student_no="+student_no, function(data, status){

                                var response = JSON.parse(data);
                                parent_element.remove();

                        });


                });



                /* TUM OGRECILER HESAP AKTIFLESTIRME ISLEMI*/

                $("#all_students").click(function(){

                        $("#all_students").remove();
                        $("#search-box-parent").after('<button name="be_deleted" class="btn btn-warning mb-4 ml-1" disabled>'+
                                                                '<span class="spinner-border spinner-border-sm"></span>'+
                                                                'Lütfen bekleyiniz...'+
                                                        '</button>');

                        //Sunucu tarafına AJAX call yapilir ve islem basarisi cevabi alinir
                        $.get("/admin/confirm_registration?op_type=all", function(data, status){

                                var response = JSON.parse(data);

                                if (response["success"] === "true") {

                                        $("#title").after('<div class="ml-2 alert alert-success" role="alert">'+
                                                                '<h4 class="alert-heading">Tüm öğrenci hesapları başarıyla aktifleştirildi!</h4>');

                                }

                                $("[name='be_deleted']").remove();

                        });


                });





        });

}
