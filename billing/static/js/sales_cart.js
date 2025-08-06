console.log("sales_cart.js loaded");

// Declare cart globally on the window object
window.cart = [];

// Declare today's date once
const today = new Date();


let allProducts = "";  // global to hold all dropdown options

document.addEventListener("DOMContentLoaded", function () {
    // Declare DOM elements here, so they are accessible in all functions below
    const searchUrl = document.getElementById("search-url")?.value || "";
    const productSelect = document.getElementById("product_ids");
    const quantityInput = document.getElementById("quantity");
    const cartDataInput = document.getElementById("cart_data");
    const cartTableBody = document.querySelector("table tbody");
    const totalDisplay = document.getElementById("total_display");
    const changeDisplay = document.getElementById("change");
    const amountPaidInput = document.getElementById("amount_paid");
    const productSearchInput = document.getElementById("product_search");
    const resetSearchButton = document.getElementById("reset_search");
    const resetCartButton = document.getElementById("resetCartButton");

    //===========================================================
    // Save all product options HTML
    allProducts = productSelect ? productSelect.innerHTML : "";

if (productSearchInput && productSelect) {
    productSearchInput.addEventListener("input", function () {
        const query = this.value.trim().toLowerCase();

        const match = Array.from(productSelect.options).find(opt =>
            opt.textContent.toLowerCase().includes(query) ||
            (opt.dataset.barcode && opt.dataset.barcode.toLowerCase() === query)
        );

        if (match) {
            match.selected = true;
        }
    });
}


if (productSearchInput && searchUrl) {
    productSearchInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            const query = this.value.trim();
            if (query.length > 1) {
                fetch(`${searchUrl}?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        console.log("Fetched on Enter:", data);
                        // Optional: dynamically update productSelect if needed
                    })
                    .catch(error => console.error("Search error:", error));
            }
        }
    });
}

//===================================================================

    // Reset search button clears search input and product selection
    if (resetSearchButton && productSearchInput && productSelect) {
        resetSearchButton.addEventListener("click", function () {
            productSearchInput.value = "";
            Array.from(productSelect.options).forEach(opt => opt.selected = false);
        });
    }



    // Update cart table UI and total display
    window.updateCartTable = function () {
        if (!cartTableBody || !totalDisplay || !cartDataInput) return;

        cartTableBody.innerHTML = "";
        let total = 0;

        window.cart.forEach((item, index) => {
            const subtotal = item.quantity * item.price;
            total += subtotal;

            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${item.name}</td>
                <td>${item.quantity}</td>
                <td>₵ ${item.price.toFixed(2)}</td>
                <td>₵ ${subtotal.toFixed(2)}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="editQuantity(${index})">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteItem(${index})">Delete</button>
                </td>
            `;
            cartTableBody.appendChild(row);
        });

        totalDisplay.textContent = total.toFixed(2);
        cartDataInput.value = JSON.stringify(window.cart);
    };

    // Add products to cart from selected options and quantity
    window.addToCart = function () {
        if (!productSelect || !quantityInput) {
            console.log("Missing productSelect or quantityInput");
            return;
        }

        const selectedOptions = Array.from(productSelect.selectedOptions);
        const quantity = parseInt(quantityInput.value);

        if (selectedOptions.length === 0 || isNaN(quantity) || quantity < 1) {
            alert("Select at least one product and enter a valid quantity.");
            return;
        }

        selectedOptions.forEach(option => {
            const id = option.value;
            const name = option.textContent.split(" - ₵")[0];
            const price = parseFloat(option.dataset.taxedPrice || option.dataset.discountedPrice || option.dataset.price);
            
            const existing = window.cart.find(item => item.id === id);

            if (existing) {
                existing.quantity += quantity;
            } else {
                window.cart.push({
                    id,
                    name,
                    price,
                    quantity
                });
            }
        });

        updateCartTable();
        productSelect.selectedIndex = -1;
        resetPaymentFields();

        // Reset dropdown options if needed
        if (productSelect && window.allProducts) {
            productSelect.innerHTML = window.allProducts;
            productSelect.value = "";
        }

        if (productSearchInput) {
            productSearchInput.value = "";
            productSearchInput.dispatchEvent(new Event('input'));  // <--- add this
            productSearchInput.focus();
        }
    };

    // Calculate Change function updates the change display color and value
    window.calculateChange = function () {
        const paid = parseFloat(amountPaidInput?.value) || 0;
        const total = window.cart.reduce((sum, item) => sum + item.quantity * item.price, 0);
        const change = paid - total;

        if (changeDisplay) {
            changeDisplay.value = change.toFixed(2);
            changeDisplay.style.color = change < 0 ? "red" : "green";
        }
    };

    // Attach calculateChange to amountPaidInput changes
    if (amountPaidInput) {
        amountPaidInput.addEventListener("input", window.calculateChange);
    }

    // Initial table update (if cart already has items)
    updateCartTable();
});



window.resetPaymentFields = function () {
    const amountPaidInput = document.getElementById("amount_paid");
    const changeDisplay = document.getElementById("change");
    if (amountPaidInput) amountPaidInput.value = "";
    if (changeDisplay) {
        changeDisplay.value = "";
        changeDisplay.style.color = "black";
    }
};


    

//Edit quantity
window.editQuantity = function (index) {
    console.log("editQuantity called with index:", index);
    console.log("Current cart:", window.cart);

    if (!window.cart[index]) {
        console.error(`No cart item at index ${index}`);
        return; // exit safely
    }

    // Set the hidden field to store the index of the item
    document.getElementById("editItemId").value = index;
    // Pre-fill the input with the current quantity
    document.getElementById("quantityInput").value = window.cart[index].quantity;

    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById("editQuantityModal"));
    modal.show();
};


// Handle the form submission
document.getElementById("editQuantityForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const index = parseInt(document.getElementById("editItemId").value);
    const newQty = parseInt(document.getElementById("quantityInput").value);

    if (!isNaN(newQty) && newQty > 0) {
        window.cart[index].quantity = newQty;
        updateCartTable();
        resetPaymentFields();

        const modalElement = document.getElementById("editQuantityModal");
        const modalInstance = bootstrap.Modal.getOrCreateInstance(modalElement);
        modalInstance.hide();


        
    }
});

// Refocus and auto-select the search input when the modal is closed (via Accept, Cancel, or Esc)
document.getElementById("editQuantityModal").addEventListener("hidden.bs.modal", function () {
    const searchInput = document.getElementById("product_search");
    searchInput.focus();
    searchInput.select(); // Auto-select the content for easy replacement
});

// Also focus on page load
window.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById("product_search");
    searchInput.focus();
    searchInput.select();
});



//=================================================================
//Delete Item fro Cart
window.deleteItem = function (index) {
    document.getElementById("deleteItemId").value = index;
    const modal = new bootstrap.Modal(document.getElementById("deleteConfirmModal"));
    modal.show();
};

document.getElementById("confirmDeleteBtn").addEventListener("click", function () {
    const index = parseInt(document.getElementById("deleteItemId").value);
    if (!isNaN(index)) {
        window.cart.splice(index, 1);
        updateCartTable();
        resetPaymentFields();

        // Manually hide the modal AFTER delete and updates are done
        const modalEl = document.getElementById("deleteConfirmModal");
        const modalInstance = bootstrap.Modal.getInstance(modalEl);
        modalInstance.hide();
    }
});


document.getElementById("deleteConfirmModal").addEventListener("hidden.bs.modal", function () {
    const searchInput = document.getElementById("product_search");
    if (searchInput) {
        setTimeout(() => {
            document.activeElement.blur();  // Remove focus from any element
            searchInput.focus();
            searchInput.select();
        }, 300);
    }
});


//=================================================================
// Reset Cart button and modal


resetCartButton.addEventListener("click", function () {
    console.log("Reset cart button clicked. Cart length:", window.cart.length);
    if (!window.cart || window.cart.length === 0) {
        console.log("Cart empty, showing emptyCartModal");
        const emptyCartModalEl = document.getElementById('emptyCartModal');
        const emptyCartModal = new bootstrap.Modal(emptyCartModalEl);
        emptyCartModal.show();
    } else {
        console.log("Cart not empty, showing resetCartModal");
        const resetCartModalEl = document.getElementById('resetCartModal');
        const resetCartModal = new bootstrap.Modal(resetCartModalEl);
        resetCartModal.show();
    }
});

document.getElementById("confirmResetButton").addEventListener("click", function () {
    console.log("Confirm reset button clicked. Clearing cart.");
    window.cart = [];
    updateCartTable();
    resetPaymentFields();

    const resetCartModalEl = document.getElementById('resetCartModal');
    const resetCartModal = bootstrap.Modal.getInstance(resetCartModalEl);
    resetCartModal.hide();
});


// Focus search input after resetCartModal hides
document.getElementById("resetCartModal").addEventListener("hidden.bs.modal", function () {
    const searchInput = document.getElementById("product_search");
    if (searchInput) {
        setTimeout(() => {
            searchInput.focus();
            searchInput.select();
        }, 100);
    }
});

// Focus search input after emptyCartModal hides
document.getElementById("emptyCartModal").addEventListener("hidden.bs.modal", function () {
    const searchInput = document.getElementById("product_search");
    if (searchInput) {
        setTimeout(() => {
            searchInput.focus();
            searchInput.select();
        }, 100);
    }
});




//=================================================================
// Calculte Change
document.addEventListener("DOMContentLoaded", function () {
    const productSearchInput = document.getElementById("product_search");
    const productSelect = document.getElementById("product_ids");
    const resetSearchButton = document.getElementById("reset_search");
    const amountPaidInput = document.getElementById("amount_paid");
    const changeDisplay = document.getElementById("change");

    // Calculate Change function
    window.calculateChange = function () {
        const paid = parseFloat(amountPaidInput.value) || 0;
        const total = window.cart.reduce((sum, item) => sum + item.quantity * item.price, 0);
        const change = paid - total;

        changeDisplay.value = change.toFixed(2);
        changeDisplay.style.color = change < 0 ? "red" : "green";
    };

    //=============================================================
    // Product Search Input event


//====================================================================
    // Reset Search Button event
    
    if (resetSearchButton && productSearchInput && productSelect) {
        resetSearchButton.addEventListener("click", function () {
            productSearchInput.value = "";
            Array.from(productSelect.options).forEach(opt => opt.selected = false);
        });
    }
});



// Helper to read CSRF token from cookie
function getCookie(name) {
  let cookieValue = null;
  document.cookie.split(';').forEach(cookie => {
    cookie = cookie.trim();
    if (cookie.startsWith(name + '=')) {
      cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
    }
  });
  return cookieValue;
}
const csrftoken = getCookie('csrftoken');

function resetModal(modalElement) {
  modalElement.classList.remove('show');
  modalElement.setAttribute('aria-hidden', 'true');
  modalElement.style.display = 'none';
  document.body.classList.remove('modal-open');
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
}

//===================================================================
// Generate Invoice js
document.addEventListener("DOMContentLoaded", function () {
  const generateBtn = document.getElementById("generate_invoice_btn");
  const confirmBtn = document.getElementById("confirmInvoiceBtn");

  const invoiceModalEl = document.getElementById("invoiceConfirmModal");
  const emptyCartModal1El = document.getElementById("emptyCartModal1");

  // Only initialize Bootstrap modals if their elements exist
  const invoiceModal = invoiceModalEl ? new bootstrap.Modal(invoiceModalEl) : null;
  const emptyCartModal1 = emptyCartModal1El ? new bootstrap.Modal(emptyCartModal1El) : null;

  if (generateBtn && invoiceModal && emptyCartModal1) {
    // Show appropriate modal based on cart contents
    generateBtn.addEventListener("click", function () {
        console.log("Generate Invoice button clicked.");
      if (!window.cart || window.cart.length === 0) {
        console.log("Cart is empty, showing emptyCartModal1.");
        emptyCartModal1.show();
      } else {
        console.log(`Cart has ${window.cart.length} items, showing invoiceConfirmModal.`);
        invoiceModal.show();
      }
    });
  } else {
    console.warn("Generate button or modals not found in DOM.");
  }

  if (confirmBtn && invoiceModal) {
    // When confirming invoice
    confirmBtn.addEventListener("click", function () {
      invoiceModal.hide();
      if (typeof checkout === "function") {
        checkout();
      } else {
        console.error("checkout() function not found");
      }
    });
  } else {
    console.warn("Confirm button or invoice modal not found in DOM.");
  }

  // Checkout logic
  window.checkout = function () {
    const phoneNumberInput = document.getElementById("phone_number");
    const customerNameInput = document.getElementById("customer_name");
    const amountPaidInput = document.getElementById("amount_paid");
    const paymentMethodInput = document.getElementById("payment_method");

    if (!phoneNumberInput || !customerNameInput || !amountPaidInput || !paymentMethodInput) {
      showCustomAlert("One or more required input fields are missing.", "danger");
      return;
    }

    const payload = {
      customer_name: customerNameInput.value.trim(),
      phone_number: phoneNumberInput.value.trim(),
      amount_paid: amountPaidInput.value,
      payment_method: paymentMethodInput.value,
      cart: window.cart.map(item => ({
        product_id: item.id,
        quantity: item.quantity,
        price: item.price
      }))
    };

    fetch("/billing/generate_invoice/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken
      },
      body: JSON.stringify(payload)
    })
      .then(resp => resp.json())
      .then(data => {
        if (data.invoice_id) {
          showCustomAlert("Invoice generated successfully!", "success");
          window.location.href = `/billing/invoice_receipt/${data.invoice_id}/`;
        } else {
          showCustomAlert("Failed to generate invoice: " + (data.error || "Unknown error"), "danger");
        }
      })
      .catch(err => {
        console.error("Error:", err);
        showCustomAlert("An error occurred while generating the invoice.", "danger");
      });
  };

  // Alert display
  window.showCustomAlert = function (message, type = "warning") {
    const alertDiv = document.getElementById("customAlert");
    if (!alertDiv) {
      console.warn("Alert div #customAlert not found");
      return;
    }

    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    alertDiv.classList.remove("d-none");

    // Auto-dismiss after 3 seconds
    setTimeout(() => {
      alertDiv.classList.add("d-none");
    }, 10000);
  };
});


// Focus search input after emptyCartModal hides
document.getElementById("emptyCartModal1").addEventListener("hidden.bs.modal", function () {
    const searchInput = document.getElementById("product_search");
    if (searchInput) {
        setTimeout(() => {
            searchInput.focus();
            searchInput.select();
        }, 100);
    }

    
});

// Focus search input after generateInvoice modal hides, whether by clicking cancel button or clicking outside the page
document.addEventListener("DOMContentLoaded", function () {
  const cancelBtn = document.getElementById("invoiceCancelBtn");
  const searchInput = document.getElementById("product_search");
  const invoiceModal = document.getElementById("invoiceConfirmModal"); // Correct ID

  function focusSearch() {
    setTimeout(() => {
      if (searchInput) {
        searchInput.focus();
        searchInput.select();
        console.log("Search input focused");
      }
    }, 100);
  }

  // Works when Cancel is clicked
  if (cancelBtn) {
    cancelBtn.addEventListener("click", focusSearch);
  }

  // Works when modal is closed via backdrop click or Esc
  if (invoiceModal) {
    invoiceModal.addEventListener("hidden.bs.modal", focusSearch);
  } else {
    console.warn("invoiceConfirmModal not found.");
  }
});

//==================================================================
// Product search
// this function is responsible for showing displaying the lowstock and expiry modal
function checkSingleSelectedOption(option) {
    const stockLevel = parseInt(option.getAttribute("data-stock")) || 0;
    const expiryDateStr = option.getAttribute("data-expiry");

    const lowStockModalEl = document.getElementById("lowStockModal");
    const expiryModalEl = document.getElementById("expiryModal");

    const lowStockModal = bootstrap.Modal.getInstance(lowStockModalEl) || new bootstrap.Modal(lowStockModalEl);
    const expiryModal = bootstrap.Modal.getInstance(expiryModalEl) || new bootstrap.Modal(expiryModalEl);

    let showExpiryLater = false;

    if (stockLevel > 0 && stockLevel <= 3) {
        const msg = `⚠️ Warning: '${option.text}' is running low on stock (Only ${stockLevel} left).`;
        document.getElementById("lowStockMessage").textContent = msg;

        lowStockModalEl.addEventListener("hidden.bs.modal", function handler() {
            lowStockModalEl.removeEventListener("hidden.bs.modal", handler);
            if (showExpiryLater) {
                expiryModal.show();
            } else {
                cleanupModals();
            }
        }, { once: true });

        lowStockModal.show();
    }

    if (expiryDateStr) {
        const expiryDate = new Date(expiryDateStr);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const daysUntilExpiry = (expiryDate - today) / (1000 * 60 * 60 * 24);

        if (daysUntilExpiry <= 30) {
            let msg = `⚠️ Warning: '${option.text}' is expiring soon (Expiry Date: ${expiryDateStr}).`;
            if (daysUntilExpiry < 0) {
                msg = `❌ Alert: '${option.text}' has already expired (Expiry Date: ${expiryDateStr}).`;
            }
            document.getElementById("expiryMessage").textContent = msg;

            if (stockLevel > 0 && stockLevel <= 3) {
                showExpiryLater = true;
            } else {
                expiryModalEl.addEventListener("hidden.bs.modal", function handler() {
                    expiryModalEl.removeEventListener("hidden.bs.modal", handler);
                    cleanupModals();
                }, { once: true });

                expiryModal.show();
            }
        }
    }
}

function cleanupModals() {
    const backdrop = document.querySelector('.modal-backdrop');
    if (backdrop) backdrop.remove();
    document.body.classList.remove('modal-open');
    document.body.style.overflow = 'auto';
}

function focusSearchInput() {
    const searchInput = document.getElementById("product_search");
    if (searchInput) {
        setTimeout(() => {
            searchInput.focus();
            searchInput.select();
        }, 100);
    }
}

document.getElementById("lowStockModal").addEventListener("hidden.bs.modal", focusSearchInput);
document.getElementById("expiryModal").addEventListener("hidden.bs.modal", focusSearchInput);


//=================================================================

document.addEventListener("DOMContentLoaded", function () {
    const productSearchInput = document.getElementById("product_search");
    const productSelect = document.getElementById("product_ids");
    const quantityInput = document.getElementById("quantity");
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Reset Search Function
    function resetSearch() {
        productSearchInput.value = "";
        productSearchInput.focus();  // autofocus here!

        productSelect.selectedIndex = -1;  // Deselect the currently selected product

        for (let i = 0; i < productSelect.options.length; i++) {
            productSelect.options[i].style.display = "block";
        }
    }

    // Reset when clicking the Reset button
    document.getElementById("reset_search").addEventListener("click", resetSearch);


//==============================================================    
// This is Manual typing for search Code. Reset when search field is manually cleared, 
productSearchInput.addEventListener("input", function () {
    const query = productSearchInput.value.trim().toLowerCase();

    if (query.length === 0) {
        resetSearch();
    } else if (query.length < 3) {
        // Show all options but don't clear input or reset focus
        for (let i = 0; i < productSelect.options.length; i++) {
            productSelect.options[i].style.display = "block";
            productSelect.options[i].selected = false;
        }
        productSelect.selectedIndex = -1;
    } else {
        let matchedOption = null;
        const isBarcodeQuery = /^[0-9]+$/.test(query); // true if query only digits

        for (let i = 0; i < productSelect.options.length; i++) {
            const option = productSelect.options[i];
            const text = option.textContent.toLowerCase();
            const barcode = option.getAttribute("data-barcode").toLowerCase();

            if (isBarcodeQuery) {
                // exact match for barcode queries
                if (barcode === query) {
                    option.style.display = "block";
                    if (!matchedOption) matchedOption = option;
                } else {
                    option.style.display = "none";
                    option.selected = false;
                }
            } else {
                // partial match on product name for non-barcode queries
                if (text.includes(query)) {
                    option.style.display = "block";
                    if (!matchedOption) matchedOption = option;
                } else {
                    option.style.display = "none";
                    option.selected = false;
                }
            }
        }

        if (matchedOption) {
            matchedOption.selected = true;
            checkSingleSelectedOption(matchedOption);
        } else {
            productSelect.selectedIndex = -1;

            if (!isBarcodeQuery) {
                // Show modal for no matches on alphabet search
                const modalEl = document.getElementById("productNotFoundModal");
                const messageEl = document.getElementById("productNotFoundMessage");

                if (modalEl && typeof bootstrap !== 'undefined') {
                    messageEl.textContent = `No product found matching: "${query}"`;
                    const modalInstance = new bootstrap.Modal(modalEl);
                    modalInstance.show();

                    // Trigger reset button click after showing modal
                    const resetSearchBtn = document.getElementById('reset_search');
                    if (resetSearchBtn) {
                        resetSearchBtn.click();
                    }
                } else {
                    // fallback if modal missing, just reset
                    resetSearch();
                }
            }
        }
    }
});



//==================================================================
// This is barcode scanning code. Autofocus on search input, 
productSearchInput.focus();

productSearchInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        const inputVal = productSearchInput.value.trim().toLowerCase();
        
        if (inputVal.length >= 4) {
            let matchFound = false;

            for (let option of productSelect.options) {
                const barcode = option.dataset.barcode?.toLowerCase();
                if (barcode === inputVal) {
                    productSelect.value = option.value;
                    quantityInput.value = 1;

                    // ✅ Delay modal check slightly
                    setTimeout(() => {
                        checkSingleSelectedOption(option);
                    }, 50);

                    // ✅ Delay addToCart slightly after modal
                    setTimeout(() => {
                        addToCart();
                    }, 150);

                    matchFound = true;
                    break;
                }
            }

            if (matchFound) {
                productSearchInput.value = ''; // ✅ Clear input if match found
            } else {
                // ✅ Clear input even when not found
                productSearchInput.value = '';

                // ✅ Try showing modal
                const modalEl = document.getElementById("productNotFoundModal");
                const messageEl = document.getElementById("productNotFoundMessage");

                if (modalEl && typeof bootstrap !== 'undefined') {
                    // Set custom message
                    messageEl.textContent = `No product found with barcode: "${inputVal}"`;

                    // Show Bootstrap modal
                    const modalInstance = new bootstrap.Modal(modalEl);
                    modalInstance.show();

                    // ✅ Trigger reset search button click to reset input and dropdown
                    const resetSearchBtn = document.getElementById('reset_search');
                    if (resetSearchBtn) {
                        resetSearchBtn.click();
                    }
                } else {
                    // Fallback alert
                    alert(`No product found with barcode: "${inputVal}"`);
                }
            }
        }
    }
});


// Focus search input again when modal is closed
const modalEl = document.getElementById("productNotFoundModal");
if (modalEl) {
  modalEl.addEventListener('hidden.bs.modal', () => {
    productSearchInput.focus();
  });
}



 

    //=============================================================
    // Product selection handler
    function handleProductSelection(event) {
    const selectedOption = event.target.selectedOptions[0];
    if (!selectedOption) return;

    const stockLevel = parseInt(selectedOption.getAttribute("data-stock")) || 0;
    const expiryDateStr = selectedOption.getAttribute("data-expiry");

    const today = new Date();
    today.setHours(0, 0, 0, 0);  // reset time to midnight for consistent comparison

    if (stockLevel === 0) {
        alert("⚠️ This product is out of stock!");
        productSelect.value = "";
        return;
    }

    if (stockLevel > 0 && stockLevel <= 3) {
        const msg = `⚠️ Warning: The selected product '${selectedOption.text}' is running low on stock (Only ${stockLevel} left).`;
        document.getElementById("lowStockMessage").textContent = msg;
        new bootstrap.Modal(document.getElementById("lowStockModal")).show();
    }

    if (expiryDateStr) {
        const expiryDate = new Date(expiryDateStr);
        const daysUntilExpiry = (expiryDate - today) / (1000 * 60 * 60 * 24);

        let msg = `⚠️ Warning: '${selectedOption.text}' is expiring soon (Expiry Date: ${expiryDateStr}).`;

        if (daysUntilExpiry < 0) {
            msg = `❌ Alert: '${selectedOption.text}' has already expired (Expiry Date: ${expiryDateStr}).`;
        } else if (daysUntilExpiry <= 30) {
            msg = `⚠️ Warning: '${selectedOption.text}' is expiring within 30 days (Expiry Date: ${expiryDateStr}).`;
        } else {
            // No expiry warning needed; maybe skip showing modal here
            return; // exit early so no modal shown
        }

        document.getElementById("expiryMessage").textContent = msg;
        new bootstrap.Modal(document.getElementById("expiryModal")).show();
    }
}

    // Attach change event to product dropdown
    document.addEventListener("change", function (event) {
        if (event.target && event.target.id === "product_ids") {
            handleProductSelection(event);
        }
    });

});


//==================================================================
// Constants and variables
const searchUrl = "/store/search-products/";  // Define your search API endpoint here
let debounceTimer = null;
let lastQuery = "";


// Flags to prevent multiple modal popups stacking
let stockExpiryModalShown = {
  lowStock: false,
  expiry: false
};




//===============================================================
// Function must be declared before use
let lastNotifiedProductId = null;  // Add this near the top of your script, globally

function checkStockAndExpiryForSearchResults() {
    const options = productDropdown.options;
    let foundLowStock = false;
    let foundExpiry = false;

    for (let option of options) {
        if (option.disabled) continue;

        const stockLevel = parseInt(option.getAttribute("data-stock")) || 0;
        const expiryDateStr = option.getAttribute("data-expiry");
        const productId = option.value;

        // Low stock modal logic
        if (!foundLowStock && stockLevel > 0 && stockLevel <= 3 && !stockExpiryModalShown.lowStock) {
            if (lastNotifiedProductId !== productId) {
                const msg = `⚠️ Warning: '${option.text}' is running low on stock (Only ${stockLevel} left).`;
                console.log(msg);
                document.getElementById("lowStockMessage").textContent = msg;

                const lowStockModal = new bootstrap.Modal(document.getElementById("lowStockModal"));
                lowStockModal.show();

                lowStockModal._element.addEventListener('hidden.bs.modal', () => {
                    stockExpiryModalShown.lowStock = false; // Reset flag when modal closes
                }, { once: true });

                stockExpiryModalShown.lowStock = true;
                lastNotifiedProductId = productId;
                foundLowStock = true;
            }
        }

        // Expiry modal logic
        if (!foundExpiry && expiryDateStr && !stockExpiryModalShown.expiry) {
            const expiryDate = new Date(expiryDateStr);
            const daysUntilExpiry = (expiryDate - today) / (1000 * 60 * 60 * 24);

            if (daysUntilExpiry <= 30) {
                if (lastNotifiedProductId !== productId) {
                    let msg = `⚠️ Warning: '${option.text}' is expiring soon (Expiry Date: ${expiryDateStr}).`;
                    if (daysUntilExpiry < 0) {
                        msg = `❌ Alert: '${option.text}' has already expired (Expiry Date: ${expiryDateStr}).`;
                    }
                    console.log(msg);
                    document.getElementById("expiryMessage").textContent = msg;

                    const expiryModal = new bootstrap.Modal(document.getElementById("expiryModal"));
                    expiryModal.show();

                    expiryModal._element.addEventListener('hidden.bs.modal', () => {
                        stockExpiryModalShown.expiry = false; // Reset flag when modal closes
                    }, { once: true });

                    stockExpiryModalShown.expiry = true;
                    lastNotifiedProductId = productId;
                    foundExpiry = true;
                }
            }
        }
    }
}



//===================================================================
///==============================================================
// Declare and initialize the search input listener safely
const searchInput = document.getElementById("product_search");
const productDropdown = document.getElementById("product_dropdown");

if (searchInput && productDropdown) {
    searchInput.addEventListener("input", function () {
        const query = searchInput.value.trim();

        clearTimeout(debounceTimer);
        if (query.length >= 2) {
            debounceTimer = setTimeout(() => {
                if (query === lastQuery) return;
                lastQuery = query;

                fetch(`${searchUrl}?q=${encodeURIComponent(query)}`)
                    .then(res => res.json())
                    .then(products => {
                        const productList = Array.isArray(products) ? products : products.results || [];

                        productDropdown.innerHTML = "";
                        productDropdown.size = productList.length > 0 ? Math.min(productList.length, 7) : 1;

                        if (productList.length === 0) {
                            const option = document.createElement("option");
                            option.textContent = "No matching products found";
                            option.disabled = true;
                            productDropdown.appendChild(option);
                            return;
                        }

                        productList.forEach(product => {
                            const option = document.createElement("option");
                            option.value = product.id;
                            option.textContent = `${product.name} - ₵${product.selling_price}`;

                            const stock = product.quantity !== undefined ? product.quantity : "0";
                            option.setAttribute("data-stock", stock);
                            option.setAttribute("data-expiry", product.expiry_date || "");

                            if (parseInt(stock) === 0) {
                                option.disabled = true;
                                option.textContent += " (Out of Stock)";
                            }

                            productDropdown.appendChild(option);
                        });

                        checkStockAndExpiryForSearchResults();

                        if (productList.length === 1) {
                            productDropdown.selectedIndex = 0;
                            productDropdown.dispatchEvent(new Event("change", { bubbles: true }));
                        }
                    })
                    .catch(err => console.error("Error fetching products:", err));
            }, 250);
        } else if (query.length === 0) {
            productDropdown.innerHTML = allProducts;
            productDropdown.size = 7;
            lastQuery = "";

            stockExpiryModalShown.lowStock = false;
            stockExpiryModalShown.expiry = false;
            lastNotifiedProductId = null;
        }
    });
} else {
    console.warn("⚠️ Required elements (searchInput or productDropdown) not found in DOM!");
}

    
    // Clean up modal backdrops
    document.querySelectorAll('[data-bs-dismiss="modal"]').forEach(btn => {
        btn.addEventListener("click", function () {
            setTimeout(() => {
                document.body.classList.remove("modal-open");
                const backdrop = document.querySelector(".modal-backdrop");
                if (backdrop) backdrop.remove();
            }, 300);
        });
    });

    document.querySelectorAll(".modal").forEach(modal => {
        modal.addEventListener("hidden.bs.modal", () => {
            document.body.style.overflow = "auto";
        });
    });

    // Cancel invoice modal close
    const cancelBtn = document.getElementById('cancelInvoiceBtn');
    const emptyCartModal = document.getElementById('emptyCartModal');
    if (cancelBtn && emptyCartModal) {
        cancelBtn.addEventListener('click', () => {
            const modalInstance = bootstrap.Modal.getInstance(emptyCartModal) || bootstrap.Modal.getOrCreateInstance(emptyCartModal);
            modalInstance.hide();
        });
    }

    





function showModalsIfNeeded(product) {
    const quantity = parseInt(product.quantity || 0);
    const expiryDate = product.expiry_date ? new Date(product.expiry_date) : null;

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (quantity <= 5) {
        const stockMsg = `${product.name} is low in stock (${quantity} left).`;
        console.log('Low Stock:', stockMsg);
        document.getElementById('lowStockMessage').textContent = stockMsg;

        const lowStockModal = new bootstrap.Modal(document.getElementById('lowStockModal'));
        lowStockModal.show();
    }

    if (expiryDate && expiryDate <= today) {
        const expiryMsg = `${product.name} has expired on ${product.expiry_date}.`;
        console.log('Expired:', expiryMsg);
        document.getElementById('expiryMessage').textContent = expiryMsg;

        const expiryModal = new bootstrap.Modal(document.getElementById('expiryModal'));
        expiryModal.show();
    }
}


document.addEventListener("DOMContentLoaded", function () {
    const productSearchInput = document.getElementById("product_search");

    // Function to focus on search input
    function focusSearchInput() {
        productSearchInput.focus();
    }

    // Attach event listeners to modal hidden events
    const lowStockModal = document.getElementById("lowStockModal");
    const expiryModal = document.getElementById("expiryModal");

    if (lowStockModal) {
        lowStockModal.addEventListener('hidden.bs.modal', focusSearchInput);
    }

    if (expiryModal) {
        expiryModal.addEventListener('hidden.bs.modal', focusSearchInput);
    }
});



document.addEventListener("DOMContentLoaded", function () {
    const expiryModal = document.getElementById("expiryModal");

    if (expiryModal) {
        expiryModal.addEventListener("hidden.bs.modal", function () {
            const searchInput = document.getElementById("product_search");

            if (searchInput && !searchInput.disabled && searchInput.offsetParent !== null) {
                setTimeout(() => {
                    searchInput.focus();
                    searchInput.select();
                }, 300);  // Increase delay slightly to wait for Bootstrap's fade transition
            }
        });
    }
});

