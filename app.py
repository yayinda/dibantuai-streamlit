import streamlit as st
import time
import os
import base64
import requests

st.set_page_config(
    page_title="coba beli | dibantu.ai",
    page_icon="🤖",
    layout="wide"
)

# --- KONFIGURASI MIDTRANS ---
is_production = False
server_key = st.secrets.get("MIDTRANS_SERVER_KEY") or os.environ.get("MIDTRANS_SERVER_KEY")
environment = "api.midtrans.com" if is_production else "api.sandbox.midtrans.com"
auth_header = base64.b64encode(f"{server_key}:".encode()).decode()

# --- CEK STATUS TRANSAKSI DARI URL ---
query_params = st.query_params
order_id_from_url = query_params.get("order_id")

if order_id_from_url:
    st.info(f"🔄 Mengecek status pembayaran untuk Order ID `{order_id_from_url}`...")
    try:
        resp = requests.get(
            f"https://{environment}/v2/{order_id_from_url}/status",
            headers={
                "Accept": "application/json",
                "Authorization": f"Basic {auth_header}"
            },
            timeout=10
        )
        data = resp.json()
        if resp.status_code == 200:
            status = data.get("transaction_status", "UNKNOWN").upper()
            st.success(f"✅ Status Pembayaran: **{status}**")
        else:
            st.warning(f"⚠️ Gagal ambil status pembayaran. Status code: {resp.status_code}")
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan saat cek status pembayaran: {e}")
    st.write("---")

# --- SESSION STATE ---
if 'cart' not in st.session_state:
    st.session_state.cart = {}

if 'customer_name' not in st.session_state:
    st.session_state.customer_name = ""
    st.session_state.customer_email = ""
    st.session_state.customer_phone = ""

st.title("🛒 Keranjang Belanja")

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Isi Keranjang")
    if not st.session_state.cart:
        st.info("Keranjang kosong. Tambahkan item terlebih dahulu.")
    else:
        total = 0
        item_details = []
        for item, qty in st.session_state.cart.items():
            price = 10000
            subtotal = price * qty
            total += subtotal
            st.write(f"- {item} x {qty} = Rp{subtotal:,}")
            item_details.append({
                "id": item.lower(),
                "price": price,
                "quantity": qty,
                "name": item
            })
        st.write(f"**Total: Rp{total:,}**")

with col2:
    st.subheader("Informasi Pembeli")
    st.session_state.customer_name = st.text_input("Nama", st.session_state.customer_name)
    st.session_state.customer_email = st.text_input("Email", st.session_state.customer_email)
    st.session_state.customer_phone = st.text_input("Nomor HP", st.session_state.customer_phone)

if st.button("Checkout Sekarang", use_container_width=True, type="primary"):
    if not st.session_state.cart:
        st.warning("Keranjang kosong.")
    elif not all([
        st.session_state.customer_name,
        st.session_state.customer_email,
        st.session_state.customer_phone
    ]):
        st.warning("Lengkapi informasi pembeli terlebih dahulu.")
    else:
        order_id = f"order-{uuid.uuid4().hex[:10]}"
        payload = {
            "transaction_details": {
                "order_id": order_id,
                "gross_amount": total
            },
            "customer_details": {
                "first_name": st.session_state.customer_name,
                "email": st.session_state.customer_email,
                "phone": st.session_state.customer_phone
            },
            "item_details": item_details,
            "callbacks": {
                "finish": f"https://dibantuai-cobamidtrans.streamlit.app/?order_id={order_id}"
            }
        }

        try:
            response = requests.post(
                f"https://{environment}/v1/payment-links",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {auth_header}"
                },
                json=payload,
                timeout=10
            )
            result = response.json()
            if response.status_code == 201:
                st.success("Link pembayaran berhasil dibuat!")
                st.markdown(f"[Klik di sini untuk bayar]({result['payment_url']})")
                st.session_state.cart = {}
            else:
                st.error(f"Gagal membuat payment link: {result}")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat membuat payment link: {e}")

# --- SESSION STATE ---
if 'cart' not in st.session_state:
    st.session_state.cart = {}
for field in ("customer_name", "customer_email", "customer_phone"):
    if field not in st.session_state:
        st.session_state[field] = ""
# Simpan link yang di-create
if 'payment_link_url' not in st.session_state:
    st.session_state.payment_link_url = None

# --- Fungsi Keranjang ---
def add_to_cart(product):
    name = product['name']
    if name in st.session_state.cart:
        st.session_state.cart[name]['quantity'] += 1
    else:
        st.session_state.cart[name] = {
            "name": name,
            "price": product['price'],
            "quantity": 1
        }
    st.toast(f"'{name}' ditambahkan ke keranjang!", icon="🛒")

def remove_from_cart(product_name):
    if product_name in st.session_state.cart:
        st.session_state.cart[product_name]['quantity'] -= 1
        if st.session_state.cart[product_name]['quantity'] <= 0:
            del st.session_state.cart[product_name]
        st.rerun()

def increase_quantity(product_name):
    if product_name in st.session_state.cart:
        st.session_state.cart[product_name]['quantity'] += 1
        st.rerun()

# --- Data Produk ---
products = [
    {
        "name": "Chatbot AI",
        "image": "https://placehold.co/600x300/E0E7FF/4F46E5?text=Chatbot+AI",
        "description": "Menggunakan Pemahaman Bahasa Alami (NLP) dan dapat terintegrasi dengan berbagai sistem seperti CRM, ERP, dan Helpdesk dengan dukungan multi-channel.",
        "price": 6000
    },
    {
        "name": "Sistem Pengajaran AI",
        "image": "https://placehold.co/600x300/D1FAE5/065F46?text=Sistem+Pengajaran+AI",
        "description": "Personalisasi pembelajaran yang berbasis AI dan dapat beradaptasi dengan kebutuhan individu.",
        "price": 6500
    },
    {
        "name": "Kiosk Interaktif",
        "image": "https://placehold.co/600x300/FEF2F2/991B1B?text=Kiosk+Interaktif",
        "description": "Solusi untuk layanan mandiri dengan layar sentuh responsif yang dapat digunakan di berbagai lokasi.",
        "price": 8500
    },
    {
        "name": "Agen Virtual",
        "image": "https://placehold.co/600x300/FFFBEB/B45309?text=Agen+Virtual",
        "description": "Dapat berinteraksi secara alami dengan pelanggan melalui berbagai platform digital.",
        "price": 5500
    },
    {
        "name": "Analisis Prediktif",
        "image": "https://placehold.co/600x300/EFF6FF/1E40AF?text=Analisis+Prediktif",
        "description": "Menggunakan machine learning dan data historis untuk memprediksi tren dan mendukung pengambilan keputusan strategis.",
        "price": 6500
    },
    {
        "name": "Pengenalan Objek",
        "image": "https://placehold.co/600x300/F3F4F6/1F2937?text=Pengenalan+Objek",
        "description": "Solusi vision intelligence yang mampu mengenali, mengklasifikasi, dan melacak objek secara otomatis.",
        "price": 9500
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
            st.button("Tambah ke Keranjang", key=f"btn_{i}", on_click=add_to_cart, args=(product,))
        st.write("")


# --- Sidebar --}}
with st.sidebar:
    st.title("🛒 Keranjang")
    st.write("---")
    total = 0
    item_details = []
    if not st.session_state.cart:
        st.info("Keranjang masih kosong.")
    else:
        for nm, d in st.session_state.cart.items():
            subtotal = d['price'] * d['quantity']
            total += subtotal
            item_details.append({
                "id": nm.replace(" ", "_"),
                "price": d['price'],
                "quantity": d['quantity'],
                "name": d['name']
            })
            c1, c2 = st.columns([3, 1])
            with c1:
                st.subheader(d['name'])
                st.write(f"Jumlah: {d['quantity']} × Rp{d['price']:,}".replace(",", "."))
                sub = f"Rp{subtotal:,}".replace(",", ".")
                st.write(f"**Subtotal: {sub}**")
            with c2:
                st.button("➕", key=f"in_{nm}", on_click=increase_quantity, args=(nm,))
                st.button("➖", key=f"out_{nm}", on_click=remove_from_cart, args=(nm,))
            st.write("---")

    st.subheader("Total Belanja")
    total_fmt = f"Rp{total:,}".replace(",", ".")
    st.markdown(f"<h2><font color='#22c55e'>{total_fmt}</font></h2>", unsafe_allow_html=True)
    st.write("---")

    st.subheader("Detail Pelanggan")
    st.session_state.customer_name = st.text_input("Nama Lengkap", st.session_state.customer_name)
    st.session_state.customer_email = st.text_input("Alamat Email", st.session_state.customer_email)
    st.session_state.customer_phone = st.text_input("Nomor Telepon", st.session_state.customer_phone)

    empty = not st.session_state.cart
    incomplete = not (st.session_state.customer_name and st.session_state.customer_email and st.session_state.customer_phone)
    if empty:
        st.warning("Keranjang Anda kosong.")
    elif incomplete:
        st.warning("Lengkapi semua detail pelanggan.")

    if st.button("Checkout Sekarang", disabled=(empty or incomplete)):
        order_id = f"order-dibantuai-{int(time.time())}"
        url = f"https://{environment}/v1/payment-links"
        auth_header = base64.b64encode(f"{server_key}:".encode()).decode()
        payload = {
            "transaction_details": {
                "order_id": order_id,
                "gross_amount": total
            },
            "customer_details": {
                "first_name": st.session_state.customer_name,
                "email": st.session_state.customer_email,
                "phone": st.session_state.customer_phone,
                "customer_details_required_fields": ["first_name", "email", "phone"]
            },
            "item_details": item_details
        }
        try:
            resp = requests.post(
                url,
                json=payload,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {auth_header}"
                },
                timeout=15
            )
            data = resp.json()
            if 200 <= resp.status_code < 300:
                link = data.get("payment_url") or data.get("payment_link_url")
                st.session_state.payment_link_url = link
            else:
                msgs = data.get("error_messages") or [str(data)]
                st.error(f"Gagal membuat payment link: {msgs}")
        except Exception as e:
            st.error(f"Error saat request Midtrans: {e}")

# --- Tampilkan link pembayaran ---
if st.session_state.payment_link_url:
    st.write("---")
    st.success("🌐 Payment link berhasil dibuat:")
    st.markdown(
        f"[Klik di sini untuk melakukan pembayaran]({st.session_state.payment_link_url})",
        unsafe_allow_html=True
    )
    # Kosongkan keranjang & form
    st.session_state.cart = {}
    st.session_state.customer_name = ""
    st.session_state.customer_email = ""
    st.session_state.customer_phone = ""
    st.session_state.payment_link_url = None

# --- FOOTER ---
st.write("---")
st.write("© 2025 dibantu.ai | Untuk informasi lebih lanjut, hubungi kami di mana ya.")

