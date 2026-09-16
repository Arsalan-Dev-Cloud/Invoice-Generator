function addItem() {

    const itemsContainer = document.getElementById("items-container");

    const itemRow = document.createElement("div");

    itemRow.className = "item-row";

    itemRow.innerHTML = `
        
        <div class="form-group">

            <label>Product</label>

            <input
                type="text"
                name="product_name[]"
                placeholder="Product name"
                required
            >

        </div>


        <div class="form-group">

            <label>Quantity</label>

            <input
                type="number"
                name="quantity[]"
                placeholder="Qty"
                min="1"
                required
            >

        </div>


        <div class="form-group">

            <label>Price</label>

            <input
                type="number"
                name="price[]"
                placeholder="Price"
                min="0"
                step="0.01"
                required
            >

        </div>


        <button
            type="button"
            class="delete-item-btn"
            onclick="deleteItem(this)"
        >
            🗑 Delete
        </button>

    `;

    itemsContainer.appendChild(itemRow);
}


function deleteItem(button) {

    const itemRow = button.parentElement;

    itemRow.remove();

}