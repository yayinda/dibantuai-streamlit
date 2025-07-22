import streamlit as st
import midtransclient
import time
import os
import re # Modul untuk validasi format email (regex)

# Mengatur konfigurasi halaman Streamlit
st.set_page_config(
    page_title="coba beli | dibantu.ai",
    page_icon="🤖",
    layout="wide"
)

# --- KONFIGURASI MIDTRANS ---
# Inisialisasi klien Midtrans menggunakan st.secrets untuk keamanan
snap = midtransclient.Snap(
    is_production=False, # Ganti menjadi True jika sudah di production
    server_key=st.secrets.get("MIDTRANS_SERVER_KEY", os.environ.get("MIDTRANS_SERVER_KEY")),
    client_key=st.secrets.get("MIDTRANS_CLIENT_KEY", os.environ.get("MIDTRANS_CLIENT_KEY"))
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

# --- FUNGSI-FUNGSI BANTUAN ---
def clear_cart_and_customer_info():
    """Mengosongkan keranjang dan data pelanggan."""
    st.session_state.cart = {}
    st.session_state.customer_name = ""
    st.session_state.customer_email = ""
    st.session_state.customer_phone = ""
    st.session_state.payment_token = None

def add_to_cart(product):
    """Menambahkan produk ke keranjang."""
    name = product['name']
    if name in st.session_state.cart:
        st.session_state.cart[name]['quantity'] += 1
    else:
        st.session_state.cart[name] = {"name": product['name'], "price": product['price'], "quantity": 1}
    st.toast(f"'{name}' ditambahkan ke keranjang!", icon="🛒")

def remove_from_cart(product_name):
    """Menghapus satu kuantitas produk."""
    if product_name in st.session_state.cart:
        st.session_state.cart[product_name]['quantity'] -= 1
        if st.session_state.cart[product_name]['quantity'] == 0:
            del st.session_state.cart[product_name]
        st.rerun()

def increase_quantity(product_name):
    """Menambah satu kuantitas produk."""
    if product_name in st.session_state.cart:
        st.session_state.cart[product_name]['quantity'] += 1
        st.rerun()

# --- PENANGANAN STATUS PEMBAYARAN (DARI URL) ---
payment_status = st.query_params.get("payment_status")
if payment_status:
    if payment_status == "success":
        st.success("Pembayaran berhasil! Terima kasih telah berbelanja.")
        st.balloons()
        # Panggil fungsi untuk membersihkan state setelah pembayaran berhasil
        clear_cart_and_customer_info()
    elif payment_status == "closed":
        st.warning("Anda menutup jendela pembayaran sebelum transaksi selesai.")
    elif payment_status == "error":
        st.error("Pembayaran gagal. Silakan coba lagi.")
    
    # Hapus query parameter dari URL agar pesan tidak muncul terus
    st.query_params.clear()

# --- DATA PRODUK ---
products = [
    {"name": "Chatbot AI", "image": "https://placehold.co/600x300/E0E7FF/4F46E5?text=Chatbot+AI", "description": "Menggunakan Pemahaman Bahasa Alami (NLP) dan dapat terintegrasi dengan berbagai sistem seperti CRM, ERP, dan Helpdesk dengan dukungan multi-channel.", "price": 600000},
    {"name": "Sistem Pengajaran AI", "image": "https://placehold.co/600x300/D1FAE5/065F46?text=Sistem+Pengajaran+AI", "description": "Personalisasi pembelajaran yang berbasis AI dan dapat beradaptasi dengan kebutuhan individu.", "price": 650000},
    {"name": "Kiosk Interaktif", "image": "https://placehold.co/600x300/FEF2F2/991B1B?text=Kiosk+Interaktif", "description": "Solusi untuk layanan mandiri dengan layar sentuh responsif yang dapat digunakan di berbagai lokasi.", "price": 850000},
    {"name": "Agen Virtual", "image": "https://placehold.co/600x300/FFFBEB/B45309?text=Agen+Virtual", "description": "Dapat berinteraksi secara alami dengan pelanggan melalui berbagai platform digital.", "price": 550000},
    {"name": "Analisis Prediktif", "image": "https://placehold.co/600x300/EFF6FF/1E40AF?text=Analisis+Prediktif", "description": "Menggunakan machine learning dan data historis untuk memprediksi tren dan mendukung pengambilan keputusan strategis.", "price": 650000},
    {"name": "Pengenalan Objek", "image": "https://placehold.co/600x300/F3F4F6/1F2937?text=Pengenalan+Objek", "description": "Solusi vision intelligence yang mampu mengenali, mengklasifikasi, dan melacak objek secara otomatis.", "price": 950000}
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
            item_details.append({"id": product_name.replace(" ", "_"), "price": details['price'], "quantity": details['quantity'], "name": details['name']})
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(details['name'])
                st.write(f"Jumlah: {details['quantity']} x Rp{details['price']:,}".replace(',', '.'))
            with col2:
                st.button("➕", key=f"add_{product_name}", on_click=increase_quantity, args=(product_name,))
                st.button("➖", key=f"rem_{product_name}", on_click=remove_from_cart, args=(product_name,))
            st.write("---")
    st.subheader("Total Belanja")
    st.markdown(f"<h2><font color='#22c55e'>Rp{total_price:,}".replace(',', '.')+"</font></h2>", unsafe_allow_html=True)
    st.write("---")
    st.subheader("Detail Pelanggan")
    st.session_state.customer_name = st.text_input("Nama Lengkap", st.session_state.customer_name)
    st.session_state.customer_email = st.text_input("Alamat Email", st.session_state.customer_email)
    st.session_state.customer_phone = st.text_input("Nomor Telepon", st.session_state.customer_phone)
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_email_valid = re.match(email_regex, st.session_state.customer_email) is not None if st.session_state.customer_email else False
    is_cart_empty = not st.session_state.cart
    is_form_incomplete = not (st.session_state.customer_name and st.session_state.customer_email and st.session_state.customer_phone)
    if is_cart_empty: st.warning("Keranjang Anda kosong.")
    elif is_form_incomplete: st.warning("Harap lengkapi semua detail pelanggan.")
    elif not is_email_valid: st.error("Format alamat email tidak valid.")
    if st.button("Checkout Sekarang", disabled=(is_cart_empty or is_form_incomplete or not is_email_valid)):
        order_id = f"order-dibantuai-{int(time.time())}"
        transaction_details = {"order_id": order_id, "gross_amount": total_price}
        customer_details = {"first_name": st.session_state.customer_name, "email": st.session_state.customer_email, "phone": st.session_state.customer_phone}
        try:
            with st.spinner("Membuat transaksi..."):
                transaction = snap.create_transaction({"transaction_details": transaction_details, "item_details": item_details, "customer_details": customer_details})
            st.session_state.payment_token = transaction['token']
            st.rerun() # Rerun untuk memicu script pop-up di bawah
        except Exception as e:
            st.error(f"Gagal membuat transaksi Midtrans: {e}")
            st.session_state.payment_token = None

# --- FOOTER ---
st.write("---")
st.write("© 2025 dibantu.ai | Untuk informasi lebih lanjut, hubungi kami di mana ya.")

# --- TRIGGER SNAP POP-UP ---
# Bagian ini akan dieksekusi jika ada token pembayaran
if st.session_state.get('payment_token'):
    # HTML ini hanya untuk menyuntikkan script, tidak untuk ditampilkan
    snap_trigger_html = f"""
        <html>
            <head>
                <script type="text/javascript"
                        src="https://app.sandbox.midtrans.com/snap/snap.js"
                        data-client-key="{snap.client_key}"></script>
            </head>
            <body>
                <script type="text/javascript">
                    snap.pay('{st.session_state.payment_token}', {{
                        onSuccess: function(result){{
                            // Arahkan kembali ke halaman utama dengan status sukses
                            window.parent.location.href = window.parent.location.pathname + "?payment_status=success";
                        }},
                        onPending: function(result){{
                            console.log("wating your payment!"); console.log(result);
                        }},
                        onError: function(result){{
                            // Arahkan kembali ke halaman utama dengan status error
                            window.parent.location.href = window.parent.location.pathname + "?payment_status=error";
                        }},
                        onClose: function(){{
                            // Arahkan kembali ke halaman utama dengan status ditutup
                            window.parent.location.href = window.parent.location.pathname + "?payment_status=closed";
                        }}
                    }})
                </script>
            </body>
        </html>
    """
    # Gunakan komponen HTML untuk menjalankan script di atas
    st.components.v1.html(snap_trigger_html, height=1)
    # Reset token segera setelah script dijalankan untuk mencegah pop-up muncul lagi
    st.session_state.payment_token = None
