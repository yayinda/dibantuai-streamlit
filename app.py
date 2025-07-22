import streamlit as st
import midtransclient
import time
import os

# Mengatur konfigurasi halaman Streamlit
st.set_page_config(
    page_title="coba beli | dibantu.ai",
    page_icon="🤖",
    layout="wide"
)

# --- KONFIGURASI MIDTRANS ---
# Inisialisasi klien Midtrans menggunakan st.secrets untuk keamanan
# Anda perlu menambahkan Server Key Anda di file secrets.toml
snap = midtransclient.Snap(
    is_production=False, # Ganti menjadi True jika sudah di production
    server_key=st.secrets.get("MIDTRANS_SERVER_KEY", os.environ.get("MIDTRANS_SERVER_KEY")),
)

# --- INISIALISASI SESSION STATE ---
if 'cart' not in st.session_state:
    st.session_state.cart = {}
if 'customer_name' not in st.session_state:
    st.session_state.customer_name = ""
if 'customer_email' not in st.session_state:
    st.session_state.customer_email = ""
if 'customer_phone' not in st.session_state:
    st.session_state.customer_phone = ""
if 'payment_token' not in st.session_state:
    st.session_state.payment_token = None


# --- FUNGSI-FUNGSI UNTUK KERANJANG ---
def add_to_cart(product):
    """Menambahkan produk ke keranjang atau menambah kuantitasnya."""
    name = product['name']
    if name in st.session_state.cart:
        st.session_state.cart[name]['quantity'] += 1
    else:
        st.session_state.cart[name] = {
            "name": product['name'],
            "price": product['price'],
            "quantity": 1
        }
    st.toast(f"'{name}' ditambahkan ke keranjang!", icon="🛒")

def remove_from_cart(product_name):
    """Menghapus satu kuantitas produk dari keranjang."""
    if product_name in st.session_state.cart:
        st.session_state.cart[product_name]['quantity'] -= 1
        if st.session_state.cart[product_name]['quantity'] == 0:
            del st.session_state.cart[product_name]
        st.rerun()

def increase_quantity(product_name):
    """Menambah satu kuantitas produk di keranjang."""
    if product_name in st.session_state.cart:
        st.session_state.cart[product_name]['quantity'] += 1
        st.rerun()

# --- DATA PRODUK ---
products = [
    {
        "name": "Chatbot AI",
        "image": "https://placehold.co/600x300/E0E7FF/4F46E5?text=Chatbot+AI",
        "description": "Menggunakan Pemahaman Bahasa Alami (NLP) dan dapat terintegrasi dengan berbagai sistem seperti CRM, ERP, dan Helpdesk dengan dukungan multi-channel.",
        "price": 600000
    },
    {
        "name": "Sistem Pengajaran AI",
        "image": "https://placehold.co/600x300/D1FAE5/065F46?text=Sistem+Pengajaran+AI",
        "description": "Personalisasi pembelajaran yang berbasis AI dan dapat beradaptasi dengan kebutuhan individu.",
        "price": 650000
    },
    {
        "name": "Kiosk Interaktif",
        "image": "https://placehold.co/600x300/FEF2F2/991B1B?text=Kiosk+Interaktif",
        "description": "Solusi untuk layanan mandiri dengan layar sentuh responsif yang dapat digunakan di berbagai lokasi.",
        "price": 850000
    },
    {
        "name": "Agen Virtual",
        "image": "https://placehold.co/600x300/FFFBEB/B45309?text=Agen+Virtual",
        "description": "Dapat berinteraksi secara alami dengan pelanggan melalui berbagai platform digital.",
        "price": 550000
    },
    {
        "name": "Analisis Prediktif",
        "image": "https://placehold.co/600x300/EFF6FF/1E40AF?text=Analisis+Prediktif",
        "description": "Menggunakan machine learning dan data historis untuk memprediksi tren dan mendukung pengambilan keputusan strategis.",
        "price": 650000
    },
    {
        "name": "Pengenalan Objek",
        "image": "https://placehold.co/600x300/F3F4F6/1F2937?text=Pengenalan+Objek",
        "description": "Solusi vision intelligence yang mampu mengenali, mengklasifikasi, dan melacak objek secara otomatis.",
        "price": 950000
    }
]

# --- TAMPILAN UTAMA (KATALOG PRODUK) ---
st.title("dibantu.ai")
st.write("---")

cols_per_row = 3
main_cols = st.columns(cols_per_row)

for i, product in enumerate(products):
    col_index = i % cols_per_row
    with main_cols[col_index]:
        with st.container(border=True):
            st.image(product["image"])
            st.header(product["name"])
            st.write(product["description"])
            formatted_price = f"Rp{product['price']:,}".replace(',', '.')
            st.markdown(f"<h4>Harga: <font color='#22c55e'>{formatted_price}</font></h4>", unsafe_allow_html=True)
            st.button("Tambahkan ke Keranjang", key=f"btn_{i}", on_click=add_to_cart, args=(product,))
        st.write("")

# --- SIDEBAR (KERANJANG BELANJA) ---
with st.sidebar:
    st.title("🛒 Keranjang Belanja")
    st.write("---")

    total_price = 0
    item_details = []
    if not st.session_state.cart:
        st.info("Keranjang belanja Anda masih kosong.")
    else:
        for product_name, details in st.session_state.cart.items():
            subtotal = details['price'] * details['quantity']
            total_price += subtotal
            item_details.append({
                "id": product_name.replace(" ", "_"), # ID produk untuk Midtrans
                "price": details['price'],
                "quantity": details['quantity'],
                "name": details['name']
            })
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(details['name'])
                formatted_subtotal = f"Rp{subtotal:,}".replace(',', '.')
                st.write(f"Jumlah: {details['quantity']} x Rp{details['price']:,}".replace(',', '.'))
                st.write(f"**Subtotal: {formatted_subtotal}**")

            with col2:
                st.button("➕", key=f"add_{product_name}", on_click=increase_quantity, args=(product_name,))
                st.button("➖", key=f"rem_{product_name}", on_click=remove_from_cart, args=(product_name,))
            st.write("---")

    st.subheader("Total Belanja")
    formatted_total = f"Rp{total_price:,}".replace(',', '.')
    st.markdown(f"<h2><font color='#22c55e'>{formatted_total}</font></h2>", unsafe_allow_html=True)
    st.write("---")

    # --- DETAIL PELANGGAN ---
    st.subheader("Detail Pelanggan")
    st.session_state.customer_name = st.text_input("Nama Lengkap", st.session_state.customer_name)
    st.session_state.customer_email = st.text_input("Alamat Email", st.session_state.customer_email)
    st.session_state.customer_phone = st.text_input("Nomor Telepon", st.session_state.customer_phone)

    # --- LOGIKA TOMBOL CHECKOUT ---
    is_cart_empty = not st.session_state.cart
    is_form_incomplete = not (st.session_state.customer_name and st.session_state.customer_email and st.session_state.customer_phone)
    
    if is_cart_empty:
        st.warning("Keranjang Anda kosong.")
    elif is_form_incomplete:
        st.warning("Harap lengkapi semua detail pelanggan.")

    if st.button("Checkout Sekarang", disabled=(is_cart_empty or is_form_incomplete)):
        # Membuat transaksi ke Midtrans
        order_id = f"order-dibantuai-{int(time.time())}"
        transaction_details = {
            "order_id": order_id,
            "gross_amount": total_price
        }
        customer_details = {
            "first_name": st.session_state.customer_name,
            "email": st.session_state.customer_email,
            "phone": st.session_state.customer_phone
        }
        
        try:
            transaction = snap.create_transaction({
                "transaction_details": transaction_details,
                "item_details": item_details,
                "customer_details": customer_details
            })
            st.session_state.payment_token = transaction['token']
        except Exception as e:
            st.error(f"Gagal membuat transaksi Midtrans: {e}")
            st.session_state.payment_token = None

# --- MENAMPILKAN POP-UP SNAP MIDTRANS ---
if st.session_state.get('payment_token'):
    snap_popup_html = f"""
        <html>
            <head>
                <script type="text/javascript"
                        src="https://app.sandbox.midtrans.com/snap/snap.js"
                        data-client-key="{st.secrets.get('MIDTRANS_CLIENT_KEY', os.environ.get('MIDTRANS_CLIENT_KEY'))}"></script>
            </head>
            <body>
                <script type="text/javascript">
                    snap.pay('{st.session_state.payment_token}', {{
                        onSuccess: function(result){{
                            /* You may add your own implementation here */
                            alert("payment success!"); console.log(result);
                            window.parent.postMessage('payment-success', '*');
                        }},
                        onPending: function(result){{
                            /* You may add your own implementation here */
                            alert("wating your payment!"); console.log(result);
                        }},
                        onError: function(result){{
                            /* You may add your own implementation here */
                            alert("payment failed!"); console.log(result);
                        }},
                        onClose: function(){{
                            /* You may add your own implementation here */
                            console.log('customer closed the popup without finishing the payment');
                            window.parent.postMessage('payment-close', '*');
                        }}
                    }})
                </script>
            </body>
        </html>
    """
    st.components.v1.html(snap_popup_html, height=600)
    # Reset token setelah ditampilkan untuk menghindari pop-up muncul terus
    st.session_state.payment_token = None
    # Kosongkan keranjang setelah checkout
    st.session_state.cart = {}
    st.session_state.customer_name = ""
    st.session_state.customer_email = ""
    st.session_state.customer_phone = ""
    st.success("Silakan selesaikan pembayaran Anda.")
    # Kita tidak rerun di sini agar pop-up tidak langsung hilang

# --- FOOTER ---
st.write("---")
st.write("© 2025 dibantu.ai | Untuk informasi lebih lanjut, hubungi kami di mana ya.")
