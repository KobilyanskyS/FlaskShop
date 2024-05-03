renderProductsTable(productsData);
renderCategoriesTable(categoriesData);
renderCategoriesFilter(categoriesData);

    function filterAndSearch() {
          const productSearchText = document.getElementById('productSearch').value.toLowerCase();
          const selectedCategoryId = document.getElementById('categoryFilter').value;

          const categorySearchText = document.getElementById('categorySearch').value.toLowerCase();

          const filteredProducts = productsData.filter(product => {
            const matchesSearch = product.name.toLowerCase().includes(productSearchText);
            const matchesCategory = selectedCategoryId === '' || product.category_name.toString() === selectedCategoryId;
            return matchesSearch && matchesCategory;
          });

          const filteredCategories = categoriesData.filter(category => {
                return category.name.toLowerCase().includes(categorySearchText);
          });
          renderProductsTable(filteredProducts);
          renderCategoriesTable(filteredCategories);
          renderCategoriesFilter(categoriesData);
    }

function renderProductsTable(products) {
  const tbody = document.querySelector('#productsTable tbody');
  tbody.innerHTML = products.map(product => `
    <tr>
      <td><img width="40px" src="${product.image_url}" alt=""></td>
      <td>${product.name}</td>
      <td>${product.price}</td>
      <td>${product.quantity}</td>
      <td data-category-id="${product.category_name}">${product.category_name}</td>
      <td>
        <a class="btn btn-sm btn-success d-block mb-1"
           data-bs-toggle="modal"
           data-bs-target="#updateProductModal"
           data-product-id="${product.id}"
           data-product-image_url="${product.image_url}"
           data-product-name="${product.name}"
           data-product-description="${product.description}"
           data-product-price="${product.price}"
           data-product-quantity="${product.quantity}"
           data-product-category-name="${product.category_name}">Изменить</a>

        <a class="btn btn-sm btn-danger d-block"
           data-bs-toggle="modal"
           data-bs-target="#deleteProductModal"
           data-product-id="${product.id}"
           data-product-name="${product.name}"
           data-product-price="${product.price}">Удалить</a>
      </td>
    </tr>
  `).join('');
}

function renderCategoriesTable(categories) {
  const tbody = document.querySelector('#categoriesTable tbody');
  tbody.innerHTML = categories.map(category => `
    <tr>
      <td><img width="40px" src="${category.image_url}" alt=""></td>
      <td>${category.name}</td>
      <td>
        <a class="btn btn-sm btn-success"
            data-bs-toggle="modal"
            data-bs-target="#updateCategoryModal"
            data-category-id="${category.id}"
            data-category-name="${category.name}"
            data-category-main_category="${category.main_category}"
            data-category-image_url="${category.image_url}"
        >Изменить</a>
        <a class="btn btn-sm btn-danger"
           data-bs-toggle="modal"
           data-bs-target="#deleteCategoryModal"
           data-category-id="${category.id}"
           data-category-name="${category.name}">Удалить</a>
      </td>
    </tr>
  `).join('');
}

function renderCategoriesFilter(categories) {
  const select = document.getElementById('categoryFilter');
  select.innerHTML = '<option value="">Все категории</option>'; // Очищаем существующие опции

  categories.forEach(category => {
    const option = document.createElement('option');
    option.value = category.name;
    option.text = category.name;
    select.appendChild(option);
  });
}

document.getElementById('productSearch').addEventListener('input', filterAndSearch);
document.getElementById('categoryFilter').addEventListener('change', filterAndSearch);
document.getElementById('categorySearch').addEventListener('input', filterAndSearch);
