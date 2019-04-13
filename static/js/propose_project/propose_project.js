function pass_func(template_values_curr) {
        $(document).ready(function() {

                /* Uyari mesajlari document ilk yukledinden disable ediliyor */
                $('#danger_message').hide()
                $('#success_message').hide()


                /* Formun default submit edilmesi engelleniyor. Asagidaki gibi kontroller yapildiktan sonra manuel olarak submit ediliyor. */
                $("#form-to-be-sent").on("submit", function() {
                        event.preventDefault()
                });


                /* Form gonderilmeden cesitli kontroller yapiliyor */
                $("#kaydet_button").on("click", function() {
                        var everythingIsOkay = true;
                        var msg = "";


                        /* Proje adi bos mu? */
                        if ($("#project_name").val() == "") {
                                everythingIsOkay = false;
                                msg = " Proje adi bos birakilamaz!"
                        }


                        /* Sorun yok ise form sunucuya gonderiliyor */
                        if (everythingIsOkay) {
                                document.forms["form-to-be-sent"].submit();
                        }


                        /* Sorun var, hata mesaji basiliyor */
                        else {
                                $('#danger_source').text(msg);
                                $('#danger_message').show();

                        }

                });

                if (template_values_curr["success"]) {
                        $('#success_message').show()
                }



        });

}
