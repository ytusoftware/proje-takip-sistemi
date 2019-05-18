function pass_func(template_values_curr) {
        $(document).ready(function() {

                /*Form-2 gönderilmişse*/
                if (template_values_curr["status"]) {

                        switch (template_values_curr["status"]) {
                                case "academician_pending":
                                        $("#apply_status").append('<p class="p-3 rounded bg-warning text-center">Akademisyen Onayı Bekliyor</p>');
                                        break;

                                case "academician_rejected":
                                        $("#apply_status").append('<p class="p-3 rounded bg-danger text-white text-center">Akademisyen Tarafından Reddedildi</p>');
                                        break;

                                case "council_pending":
                                        $("#apply_status").append('<p class="p-3 rounded bg-warning text-center">Kurul Onayı Bekliyor</p>');
                                        break;

                                case "council_rejected":
                                        $("#apply_status").after('<div class="card-header">'+
                                                                        '<strong>Kurul Açıklaması</strong>'+
                                                                  ' </div>'+
                                                                  '<div class="card-body">'+
                                                                        template_values_curr["council_decision"]+
                                                                  '</div>');

                                        $("#apply_status").append('<p class="p-3 rounded bg-danger text-white text-center">Kurul Tarafından Reddedildi</p>');
                                        break;

                                case "council_confirmed":
                                        $("#apply_status").after('<div class="card-header">'+
                                                                '<strong>Kurul Açıklaması</strong>'+
                                                          ' </div>'+
                                                          '<div class="card-body">'+
                                                                template_values_curr["council_decision"]+
                                                          '</div>');


                                        $("#apply_status").append('<p class="p-3 rounded bg-success text-white text-center">Kurul Tarafından Onaylandı</p>');
                                        break;
                        }

                }

                /* Form-2 gönderilmemiş*/
                else {
                        $("[name='be_deleted']").remove();
                        $("#title").after('<div class="ml-2 alert alert-warning" role="alert">' +
                                '<h4 class="alert-heading">Gönderilen Form-2 bulunmamaktadır!</h4>' +
                                '<p>"Proje İşlemleri/Form-2 Gönder" sayfasından Form-2 gönderebilirsiniz.</p></div>');

                }






        });

}
