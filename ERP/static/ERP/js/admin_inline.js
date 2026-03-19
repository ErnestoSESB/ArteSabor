function showTab(tab, btn) {
            document.getElementById('tab-doces').style.display = 'none';
            document.getElementById('tab-categorias').style.display = 'none';
            document.getElementById('tab-pedidos').style.display = 'none';
            document.getElementById('tab-clientes').style.display = 'none';
            document.getElementById('tab-pagamentos').style.display = 'none';
            document.getElementById('tab-receitas').style.display = 'none';
            document.getElementById('header-btn-doces').style.display = 'none';
            document.getElementById('header-btn-categorias').style.display = 'none';
            document.getElementById('header-btn-pedidos').style.display = 'none';
            document.getElementById('header-btn-clientes').style.display = 'none';
            document.getElementById('header-btn-pagamentos').style.display = 'none';
            document.getElementById('header-btn-receitas').style.display = 'none';

            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            btn.classList.add('active');

            document.getElementById('tab-' + tab).style.display = 'block';
            document.getElementById('header-btn-' + tab).style.display = 'block';
        }