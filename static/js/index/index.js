function pass_func(template_values_curr) {
        $(document).ready(function() {
                if (template_values_curr["first_timer"] !== "false") {
                        if (template_values_curr["user_type"] === "academician") {
                                $("#modal_name").remove();
                                $("#modal_sname").remove();

                        }

                        $('#bilgiAlmaModal').modal({
                                backdrop: 'static',
                                keyboard: false
                        });


                        $('#modal_onay_buton').click(function() {

                                var user_type = template_values_curr["user_type"];
                                var modal_name = "";
                                var modal_sname = "";
                                var modal_pass;

                                modal_pass = $("#modal_pass").val();

                                //Hata mesajlari temizleniyor
                                if (user_type === "student") {
                                        modal_name = $("#modal_name").val();
                                        modal_sname = $("#modal_sname").val();

                                        $("#modal_name").removeClass("is-invalid");
                                        $("#modal_sname").removeClass("is-invalid");

                                }

                                $("#modal_pass").removeClass("is-invalid");
                                $("#modal_pass_again").removeClass("is-invalid");


                                $("[name='error_msg']").remove();



                                //Ajax call oncesi cesitli kontroller yapiliyor
                                if ( (user_type === "student") && ($("#modal_name").val() === "") ) {
                                        $("#modal_name").addClass("is-invalid");
                                        $("#modal_name").after('<div name="error_msg" class="invalid-feedback">'+
                                                                        'İsim boş bırakılamaz.'+
                                                                '</div>');

                                }


                                else if ((user_type === "student") && ($("#modal_sname").val() === "")) {
                                        $("#modal_name").addClass("is-valid");
                                        $("#modal_sname").addClass("is-invalid");
                                        $("#modal_sname").after('<div name="error_msg" class="invalid-feedback">'+
                                                                        'Soyisim boş bırakılamaz.'+
                                                                '</div>');
                                }


                                else if ($("#modal_pass").val() === "") {
                                        if (user_type === "student") {
                                                $("#modal_name").addClass("is-valid");
                                                $("#modal_sname").addClass("is-valid");
                                        }

                                        $("#modal_pass").addClass("is-invalid");
                                        $("#modal_pass").after('<div name="error_msg" class="invalid-feedback">'+
                                                                        'Şifre boş bırakılamaz.'+
                                                                '</div>');

                                }


                                else if ($("#modal_pass").val() !== $("#modal_pass_again").val()) {
                                        $("#modal_pass").addClass("is-invalid");
                                        $("#modal_pass_again").addClass("is-invalid");
                                        $("#modal_pass").after('<div name="error_msg" class="invalid-feedback">'+
                                                                        'Şifreler birbiriyle uyuşmamaktadır!'+
                                                                '</div>');
                                }

                                else {
                                        $.ajax({
                                                type: "POST",
                                                url: "/edit_info",
                                                contentType: "application/json;charset=UTF-8",
                                                dataType: "json",
                                                data: JSON.stringify({
                                                        "modal_name": modal_name,
                                                        "modal_sname": modal_sname,
                                                        "modal_pass": modal_pass
                                                }),

                                                success: function (data, status, xhr) {
                                                        window.location.href = "/";
                                                }

                                        });

                                }


                        });
                }

        });
}
