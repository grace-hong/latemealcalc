if (document.readyState == 'loading') {
    document.addEventListener('DOMContentLoaded', ready)
} else {
    ready()
}

function ready() {
    var removeCartItemButtons = document.getElementsByClassName('btn-danger')
    for (var i = 0; i < removeCartItemButtons.length; i++) {
        var button = removeCartItemButtons[i]
        button.addEventListener('click', removeCartItem)
    }

    var addToCartButtons = document.getElementsByClassName('shop-item-button')
    for (var i = 0; i < addToCartButtons.length; i++) {
        var button = addToCartButtons[i]
        button.addEventListener('click', addToCartClicked)
    }

    document.getElementsByClassName('btn-purchase')[0].addEventListener('click', purchaseClicked)
}

function purchaseClicked() {
    alert('Items Cleared')
    var cartItems = document.getElementsByClassName('cart-items')[0]
    while (cartItems.hasChildNodes()) {
        cartItems.removeChild(cartItems.firstChild)
    }
    updateCartTotal()
}

function removeCartItem(event) {
    var buttonClicked = event.target
    buttonClicked.parentElement.parentElement.remove()
    updateCartTotal()
}

function addToCartClicked(event) {
    var button = event.target
    var shopItem = button.parentElement
    var title = shopItem.getElementsByClassName('shop-item-title')[0].innerText
    var price = shopItem.getElementsByClassName('shop-item-price')[0].innerText
    addItemToCart(title, price)
    updateCartTotal()
}

function addItemToCart(title, price) {
    var cartBlock = document.createElement('div')
    cartBlock.classList.add('cart-block')
    var cartItems = document.getElementsByClassName('cart-items')[0]
    var cartItemNames = cartItems.getElementsByClassName('cart-item-title')
  
    var cartBlockContents = `
    <div class = "cart-item">

    <span class="cart-item-title">${title}</span>
    <span class="cart-price">${price}</span>
    
     <button class="btn btn-danger fas fa-minus" type="button"></button>

    </div>
      
        `
    cartBlock.innerHTML = cartBlockContents
    shopItems.append(cartBlock)
    cartBlock.getElementsByClassName('btn-danger')[0].addEventListener('click', removeCartItem)
    
}

function updateCartTotal() {
    var cartItemContainer = document.getElementsByClassName('cart-items')[0]
    var cartBlocks = cartItemContainer.getElementsByClassName('cart-block')
    var total = 0
    for (var i = 0; i < cartBlocks.length; i++) {
        var cartBlock = cartBlocks[i]
        var priceElement = cartBlock.getElementsByClassName('cart-price')[0]
        var price = parseFloat(priceElement.innerText.replace('$', ''))
        total = total + price
    }
    total = Math.round(total * 100) / 100
    // COLOR FOR TOTAL WHEN IT BECOMES GREATER THAN LATEMEAL PRICE
    if (total <= 20) {
    	document.getElementsByClassName('cart-total-price')[0].style.color = "green";
    }
    if (total > 20) {
    	document.getElementsByClassName('cart-total-price')[0].style.color = "red";
    }
    document.getElementsByClassName('cart-total-price')[0].innerText = '$' + total


}
