# 🌾 CropCircle

A smart agricultural marketplace connecting Farmers, Distributors, and Retailers.

## Quick Start

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the app:
   ```
   python app.py
   ```

3. Open your browser at: http://127.0.0.1:5000

## Features
- Register as Farmer, Distributor, or Retailer
- Post crop listings with photos, price, and quantity
- Place and manage orders
- Built-in chat with digital receipts
- Like posts, edit profile, role-based dashboards

## Bugs Fixed
- session['user'] → session['username'] in navbar (was always showing Login/Register)
- home.html referenced post['role'], post['date'], post['product'] etc. — fields that didn't exist in the post model
- profile.html form posted wrong fields and wrong route
- my_orders.html referenced order['product'] which didn't exist
- All 3 dashboard templates titled "Farmer Dashboard" regardless of role
- Order rejection was missing (only accept existed)

## New Features Added
- ❤️ Like/Unlike posts (AJAX, no page reload)
- 🔍 Search + filter feed by role (sidebar)
- ✏️ Edit profile (name, bio, location, picture)
- 📸 Inline create post from feed
- 🛒 Order quantity input before placing order
- ❌ Reject order button for sellers
- 💬 Chat linked directly from posts and orders
- 📊 Stats cards on dashboards (total orders, pending, accepted)
- 🏪 Role-specific badge colors (green/blue/purple)
- 📱 Fully responsive design
