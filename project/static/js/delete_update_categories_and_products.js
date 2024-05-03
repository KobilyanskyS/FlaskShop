    document.getElementById('deleteProductModal').addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget;
        var productId = button.getAttribute('data-product-id');
        var productName = button.getAttribute('data-product-name');
        var productPrice = button.getAttribute('data-product-price');

        var modal = this;
        modal.querySelector('.modal-body').innerHTML =
            'Вы действительно хотите удалить товар: ' + productName + ' (' + productPrice + ' руб.)?';
        modal.querySelector('#product_id').value = productId;
    });

    document.getElementById('deleteCategoryModal').addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget;
        var categoryId = button.getAttribute('data-category-id');
        var categoryName = button.getAttribute('data-category-name');

        var modal = this;
        modal.querySelector('.modal-body').innerHTML =
            'Вы действительно хотите удалить категорию: ' + categoryName + '?';
        modal.querySelector('#category_id').value = categoryId;
    });

    document.getElementById('updateProductModal').addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget;
        var productId = button.getAttribute('data-product-id');
        var productImageUrl = button.getAttribute('data-product-image_url');
        var productName = button.getAttribute('data-product-name');
        var productDescription = button.getAttribute('data-product-description');
        var productPrice = button.getAttribute('data-product-price');
        var productQuantity = button.getAttribute('data-product-quantity');
        var productCategoryName = button.getAttribute('data-product-category-name');

        document.getElementById('update_product_id').value = productId;
        document.getElementById('update_product_image').src = productImageUrl;
        document.getElementById('update_product_name').value = productName;
        document.getElementById('update_product_description').value = productDescription;
        document.getElementById('update_product_price').value = productPrice;
        document.getElementById('update_product_quantity').value = productQuantity;

        var selectOptions = document.querySelectorAll('#update_product_category_name option');
        selectOptions.forEach(function(option) {
            if (option.textContent === productCategoryName) {
                option.selected = true;
            }
        });
    });



    function updateCategorySelect(selectedCategoryId) {
        var select = document.getElementById('update_category_main_category');
        while (select.firstChild) {
            select.removeChild(select.firstChild);
        }

        var defaultOption = new Option('Нет (Верхний уровень)', '');
        select.appendChild(defaultOption);

        categoriesData.forEach(function(category) {
            if (category.id.toString() !== selectedCategoryId) {
               var option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.name;
               select.appendChild(option);
           }
       });
    }

    document.getElementById('updateCategoryModal').addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget;
        var categoryId = button.getAttribute('data-category-id');
        var categoryImageUrl = button.getAttribute('data-category-image_url');
        var categoryName = button.getAttribute('data-category-name');
        var categoryMainCategory = button.getAttribute('data-category-main_category');

        document.getElementById('update_category_id').value = categoryId;
        document.getElementById('update_category_image').src = categoryImageUrl;
        document.getElementById('update_category_name').value = categoryName;

        updateCategorySelect(categoryId);
    });



    function checkSelectOptions(selectId, btnId, textId) {
      const selectElement = document.getElementById(selectId);
      const options = selectElement.options;
      const btn = document.getElementById(btnId);
      const text = document.getElementById(textId);

      if (options.length === 0) {
        selectElement.disabled = true;
        btn.disabled = true;
        text.append("Для добавления нового товара создайте хотя бы одну категорю.");
      } else {
        selectElement.disabled = false;
      }
    }

    window.onload = function() { checkSelectOptions("category", "addProductId", "categoryError");};