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
}

function purchaseClicked() {
    // alert('Items Cleared')
    var cartItems = document.getElementsByClassName('cart-items')[0]
    while (cartItems.hasChildNodes()) {
        cartItems.removeChild(cartItems.firstChild)
    }
	checkpackaged()
    updateCartTotal()
}

function removeCartItem(event) {
    var buttonClicked = event.target
    buttonClicked.parentElement.parentElement.remove()
    checkpackaged()
    updateCartTotal()
}

function addToCartClicked(event) {

    var button = event.target
    var shopItem = button.parentElement.parentElement
    var title = shopItem.getElementsByClassName('shop-item-title')[0].innerText
    var price = shopItem.getElementsByClassName('shop-item-price')[0].innerText
    // checkpackaged(title)
    
    addItemToCart(title, price)
    checkpackaged()
    updateCartTotal()
}

function checkpackaged(){
    var priceElement = document.getElementsByClassName('total-price')[0].textContent
    total = parseFloat(priceElement.replace('$', ''))
	/*
	$(function() {
	    $(button).click(function() {
		    $.ajax({
			    url: '/addItem/item/<search>/<item>',
			    type: 'POST',
			    datatype: "data",
			    data: {name: $("#INPUTNAME").val()},
			    success: function(result) {
	 			alert('ok');
		    	},
			   error: function(error) {
			    alert('error');
		    }
	    });
    });
}); */
	alert('entered this function')
	$("#addition").click(function() {
		$.getJSON('/addItem/item/<search>/<item>/packaged', function(dat) {
			alert(dat);
			print(dat);
		});
	});
}

function checkpackaged(title) {
    // alert('yes or no');
    return 0
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
    cartItems.append(cartBlock)
    cartBlock.getElementsByClassName('btn-danger')[0].addEventListener('click', removeCartItem)
    
}

function addItem(itemName) {
    // alert("Item added.");
    str = "/removeItem/" + itemName;
    window.location=str;
}

function removeItem(itemName) {
    // alert("Item removed.");
    str = "/addItem/" + itemName;
    window.location=str;
}

function updateCartTotal() {
    alert('in updateCartTotal function')
    //var cartItemContainer = document.getElementsByClassName('cart-items')[0]
    //var cartBlocks = cartItemContainer.getElementsByClassName('cart-block')
    var total = 0
    var maxPrice = 0
    /*for (var i = 0; i < cartBlocks.length; i++) {
        var cartBlock = cartBlocks[i]
        var priceElement = cartBlock.getElementsByClassName('cart-price')[0]
        var price = parseFloat(priceElement.innerText.replace('$', ''))
        total = total + price
    }*/
    
    var priceElement = document.getElementsByClassName('total-price')[0].textContent
    total = parseFloat(priceElement.replace('$', ''))
    //total = Math.round(priceElement * 100) / 100
    
    if (getTime() == 0) {
        maxPrice = 6
    }
    else {
        maxPrice = 7
    }
    alert("maxPrice = "  + maxPrice + " total = " + total);
    // COLOR FOR TOTAL WHEN IT BECOMES GREATER THAN LATEMEAL PRICE
    if (total > maxPrice) {
    	document.getElementsByClassName('cart-total-price')[0].style.color = "red";
        document.getElementsByClassName('cart-dif')[0].innerText = '- $' + (total - maxPrice).toFixed(2);
        document.getElementsByClassName('cart-dif')[0].style.color = "red";
    }
    else {
    	document.getElementsByClassName('cart-total-price')[0].style.color = "green";
        document.getElementsByClassName('cart-dif')[0].innerText = '';
        /*if (total < maxPrice) {
            document.getElementsByClassName('suggested')[0].innerText = "Suggested Items<br>" + getSuggested(maxPrice - total);
        }*/
    }
    document.getElementsByClassName('cart-total-price')[0].innerText = '$' + total.toFixed(2)

}

/* return 0 for lunchtime, 1 for dinner */
function getTime() {
    var time = new Date()
    if (time.getHours() * 60 + time.getMinutes() <= 945) { // lunch time
        return 0
    }
    else { // dinner time
        return 1
    }
}

/* return a string of suggested items based on money left (difference) */
/*function getSuggested(difference) {
    var retStr = "";
    // connect to database 
    var pg = require(‘pg’);
    var connectionString = "postgres://gniojkvxziujuu:1c53b1d388891669097c66f2e618d42e31ffffa249aaaef45ccf72034503106c@ec2-184-73-153-64.compute-1.amazonaws.com:5432/d1ipk1vqr3fslq";
    var pgClient = new pg.Client(connectionString);
    pgClient.connect(connectionString, function(err, client, done) {
       client.query('SELECT name, price FROM food', function(err, result) {
          done();
          if(err) return console.error(err);
          for (let row of res.rows) {
          if (row[1] <= difference) {
            retStr = JSON.stringify(row[0]) + "<br>";
          }
      }
      client.end();
       });
    });
    return retStr;
}*/

function includeHTML() {
	  var z, i, elmnt, file, xhttp;
	  /* Loop through a collection of all HTML elements: */
	  z = document.getElementsByTagName("*");
	  for (i = 0; i < z.length; i++) {
	    elmnt = z[i];
	    /*search for elements with a certain atrribute:*/
	    file = elmnt.getAttribute("w3-include-html");
	    if (file) {
	      /* Make an HTTP request using the attribute value as the file name: */
	      xhttp = new XMLHttpRequest();
	      xhttp.onreadystatechange = function() {
		if (this.readyState == 4) {
		  if (this.status == 200) {elmnt.innerHTML = this.responseText;}
		  if (this.status == 404) {elmnt.innerHTML = "Page not found.";}
		  /* Remove the attribute, and call this function once more: */
		  elmnt.removeAttribute("w3-include-html");
		  includeHTML();
		}
	      } 
	      xhttp.open("GET", file, true);
	      xhttp.send();
	      /* Exit the function: */
	      return;
	    }
	  }
	}
