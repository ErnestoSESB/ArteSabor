function addIngredient() {
            const list = document.getElementById('ing-list');
            const row = document.createElement('div');
            row.className = 'ingredient-row';
            row.innerHTML = `
                <input type="text" name="ingredient_qty[]" placeholder="Qtd. (ex: 200g)">
                <input type="text" name="ingredient_name[]" placeholder="Nome (ex: Chocolate)" style="flex:1;">
                <button type="button" class="remove-btn" onclick="this.parentElement.remove()">X</button>
            `;
            list.appendChild(row);
        }