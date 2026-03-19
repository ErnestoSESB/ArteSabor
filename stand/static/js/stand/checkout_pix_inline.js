function copiarPix() {

        const input = document.getElementById('pix-texto');

        input.select();

        input.setSelectionRange(0, 99999); // Para mobile

        navigator.clipboard.writeText(input.value).then(() => {

            const msg = document.getElementById('msg-copiado');

            msg.style.display = 'block';

            setTimeout(() => { msg.style.display = 'none'; }, 3000);

        }).catch(err => {

            console.error("Erro ao copiar", err);

        });

    }