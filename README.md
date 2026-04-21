# 🌾 CropCircle

<img width="1883" height="881" alt="Screenshot 2026-04-21 120504" src="https://github.com/user-attachments/assets/db7967e1-0e36-4b7c-b99e-5703eee2a8ee" />

<img width="1881" height="902" alt="Screenshot 2026-04-21 120549" src="https://github.com/user-attachments/assets/23624e95-88df-49a2-82e6-79fd217b82eb" />

<img width="1905" height="887" alt="Screenshot 2026-04-21 120655" src="https://github.com/user-attachments/assets/56a2fe8b-ff2e-4617-9f25-ae63032a7f20" />

<img width="1876" height="910" alt="Screenshot 2026-04-21 120821" src="https://github.com/user-attachments/assets/39e006e7-ba59-444b-b792-10a78b8d859a" />

<img width="1880" height="895" alt="Screenshot 2026-04-21 120902" src="https://github.com/user-attachments/assets/76050c01-64a0-43fd-b784-220b8489f915" />






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
