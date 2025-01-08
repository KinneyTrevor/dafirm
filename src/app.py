from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flash messages

# Mock product data
products = [
    {"id": 1, "name": "Laptop", "price": 999.99},
    {"id": 2, "name": "Smartphone", "price": 599.99},
    {"id": 3, "name": "Headphones", "price": 99.99},
]

@app.route("/")
def home():
    return render_template("home.html", products=products)

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        address = request.form.get("address")
        payment_method = request.form.get("payment_method")
        product_id = request.form.get("product_id")
        quantity = int(request.form.get("quantity", 1))

        # Validate input
        if not name or not address or not payment_method:
            flash("All fields are required!", "error")
            return redirect(url_for("checkout"))

        # Mock processing
        selected_product = next((p for p in products if str(p["id"]) == product_id), None)
        if not selected_product:
            flash("Invalid product selected!", "error")
            return redirect(url_for("home"))

        total_price = selected_product["price"] * quantity

        if payment_method == "affirm":
            # Call Affirm Direct API
            affirm_response = requests.post("https://sandbox.affirm.com/api/v2/checkout", json={
                "merchant": {
                    "public_api_key": "YOUR_AFFIRM_PUBLIC_API_KEY"
                },
                "shipping": {
                    "name": name,
                    "address": address
                },
                "items": [
                    {
                        "display_name": selected_product["name"],
                        "sku": str(selected_product["id"]),
                        "unit_price": int(selected_product["price"] * 100),  # price in cents
                        "qty": quantity
                    }
                ],
                "total": int(total_price * 100)  # total price in cents
            })

            if affirm_response.status_code == 200:
                flash("Order placed successfully with Affirm!", "success")
            else:
                flash("Affirm payment failed!", "error")
                return redirect(url_for("checkout"))
        else:
            flash(f"Order placed successfully for {selected_product['name']} (${total_price:.2f})!", "success")

        return redirect(url_for("home"))

    return render_template("checkout.html", products=products)

if __name__ == "__main__":
    app.run(debug=True)
