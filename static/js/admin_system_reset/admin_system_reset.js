$(document).ready(function() {


                /* Form gonderilmeden cesitli kontroller yapiliyor */
                $("[name='kaydet_button']").on("click", function() {

                        $.get("/system_reset", function(data, status){

                                var data_var = JSON.parse(data);
                                if (data_var["success"]) {
                                        $("#aciklama").after('<div class="alert alert-success alert-dismissible fade show" role="alert">'+
                                                'Sistem başarıyla sıfırlandı.'+
                                                        '<button type="button" class="close" data-dismiss="alert" aria-label="Close">'+
                                                                '<span aria-hidden="true">&times;</span>'+
                                                        '</button>'+
                                                        '</div>');

                                }
                                else {
                                        $("#aciklama").after('<div class="alert alert-danger alert-dismissible fade show" role="alert">'+
                                                'Bir hata oldu, lütfen tekrar deneyiniz.'+
                                                        '<button type="button" class="close" data-dismiss="alert" aria-label="Close">'+
                                                                '<span aria-hidden="true">&times;</span>'+
                                                        '</button>'+
                                                        '</div>');

                                }

                        });

                });

        });
