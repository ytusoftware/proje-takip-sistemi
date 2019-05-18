function pass_func(template_values_curr) {
        $(document).ready(function() {

                /* Surec kapaliysa arkadas devam karari kapali */
                if (!template_values_curr["PROCESS_8"] || (template_values_curr["data_project"][1] !== "academician") || (template_values_curr["confirm_status"] === "true")) {
                        $("#devam_karari").remove()
                }


                /* devam karari isleme */
                $("#cancel_onay_button").on("click", function() {
                        $("[name='be_deleted']").remove();
                        $.get("/grade/confirm_continuation", function(data, status){
                                $("#top-part").prepend('<div class="mt-2 alert alert-success alert-dismissible fade show" role="alert">'+
                                                                         'Devam kararı başarılı bir şekilde işlendi!'+
                                                                                '<button type="button" class="close" data-dismiss="alert" aria-label="Close">'+
                                                                                        '<span aria-hidden="true">&times;</span>'+
                                                                                '</button>'+
                                                              '</div>'
                                                        );
                        });


                });

        });

}
