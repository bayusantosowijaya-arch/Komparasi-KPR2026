import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import locale

# ─── PAGE CONFIG ────────────────────────────────────────────
st.set_page_config(
    page_title="KPR Simulator Pro",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Header */
.main-header {
    background: linear-gradient(135deg, #0b1628 0%, #112240 100%);
    border: 1px solid rgba(201,168,76,0.3);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
}
.main-title {
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    font-weight: 900;
    color: #f4f1ea;
    margin: 0;
    line-height: 1.2;
}
.main-title em { font-style: normal; color: #c9a84c; }
.main-sub { font-size: 13px; color: #7a90b0; margin-top: 4px; }
.data-badge {
    background: rgba(46,204,138,0.12);
    border: 1px solid rgba(46,204,138,0.35);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 11px;
    color: #2ecc8a;
    font-weight: 600;
    letter-spacing: 1px;
    white-space: nowrap;
}
.wa-contact {
    background: linear-gradient(135deg, #25D366, #1ebe5d);
    border-radius: 30px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 700;
    color: white;
    text-decoration: none;
    white-space: nowrap;
}

/* Cards */
.metric-card {
    background: rgba(13,26,50,0.9);
    border: 1px solid rgba(201,168,76,0.2);
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
    margin-bottom: 10px;
}
.metric-label { font-size: 11px; color: #7a90b0; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.metric-value { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 700; color: #f4f1ea; }
.metric-value.gold { color: #e8c97a; }
.metric-value.green { color: #2ecc8a; }
.metric-value.red { color: #e05c5c; }
.metric-value.orange { color: #f0a500; }

/* Big result */
.cicilan-hero {
    background: linear-gradient(135deg, rgba(201,168,76,0.15), rgba(201,168,76,0.05));
    border: 2px solid rgba(201,168,76,0.4);
    border-radius: 16px;
    padding: 28px;
    text-align: center;
    margin: 16px 0;
}
.cicilan-label { font-size: 11px; color: #c9a84c; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px; }
.cicilan-amount { font-family: 'Playfair Display', serif; font-size: 42px; font-weight: 900; color: #f4f1ea; }
.cicilan-sub { font-size: 13px; color: #7a90b0; margin-top: 6px; }

/* Status boxes */
.status-layak {
    background: rgba(46,204,138,0.08);
    border: 1px solid rgba(46,204,138,0.35);
    border-radius: 12px;
    padding: 16px 20px;
}
.status-tidak {
    background: rgba(224,92,92,0.08);
    border: 1px solid rgba(224,92,92,0.35);
    border-radius: 12px;
    padding: 16px 20px;
}
.status-batas {
    background: rgba(240,165,0,0.08);
    border: 1px solid rgba(240,165,0,0.35);
    border-radius: 12px;
    padding: 16px 20px;
}

/* Bank table */
.bank-best {
    background: rgba(201,168,76,0.12) !important;
    border: 1px solid rgba(201,168,76,0.4) !important;
}
.note-box {
    background: rgba(240,165,0,0.07);
    border: 1px solid rgba(240,165,0,0.25);
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 12px;
    color: rgba(240,165,0,0.9);
    margin-top: 12px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0b1628;
    border-right: 1px solid rgba(201,168,76,0.15);
}
section[data-testid="stSidebar"] .stMarkdown p {
    color: #7a90b0;
    font-size: 12px;
}

/* Hide default streamlit menu items */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─── BANK DATA ───────────────────────────────────────────────
BANKS_DEFAULT = [
    {"name": "Bank BTN",     "type": "BUMN",   "product": "KPR BTN Non-Subsidi", "fixed": 6.50, "fix_prd": "3 thn", "float": 11.5, "max_tnr": 30},
    {"name": "Bank BRI",     "type": "BUMN",   "product": "KPR BRI Griya",       "fixed": 6.75, "fix_prd": "3 thn", "float": 13.0, "max_tnr": 30},
    {"name": "Bank BNI",     "type": "BUMN",   "product": "BNI Griya",           "fixed": 6.99, "fix_prd": "3 thn", "float": 12.0, "max_tnr": 30},
    {"name": "Bank Mandiri", "type": "BUMN",   "product": "Mandiri KPR",         "fixed": 7.25, "fix_prd": "3 thn", "float": 13.0, "max_tnr": 30},
    {"name": "CIMB Niaga",   "type": "Swasta", "product": "KPR Xtra Manfaat",    "fixed": 7.25, "fix_prd": "2-3 thn","float": 11.5, "max_tnr": 25},
    {"name": "Bank BCA",     "type": "Swasta", "product": "KPR BCA / KPR Xtra",  "fixed": 7.49, "fix_prd": "3 thn", "float": 11.0, "max_tnr": 25},
    {"name": "Permata Bank", "type": "Swasta", "product": "KPR Permata",         "fixed": 7.50, "fix_prd": "3 thn", "float": 12.5, "max_tnr": 20},
    {"name": "Maybank",      "type": "Swasta", "product": "Maybank KPR Plus",    "fixed": 7.75, "fix_prd": "3-5 thn","float": 12.0, "max_tnr": 25},
    {"name": "Bank OCBC",    "type": "Swasta", "product": "KPR Easy Start",      "fixed": 7.88, "fix_prd": "3 thn", "float": 12.5, "max_tnr": 25},
    {"name": "Bank Danamon", "type": "Swasta", "product": "KPR Danamon",         "fixed": 8.00, "fix_prd": "2-3 thn","float": 12.5, "max_tnr": 20},
]

# ─── HELPER FUNCTIONS ────────────────────────────────────────
def fmt_rp(n):
    """Format number as Rp x.xxx.xxx"""
    if n is None or np.isnan(n):
        return "—"
    return f"Rp {int(round(n)):,}".replace(",", ".")

def anuitas(pokok, rate_ann, tenor_thn):
    """Hitung cicilan anuitas bulanan"""
    r = rate_ann / 100 / 12
    n = tenor_thn * 12
    if r == 0:
        return pokok / n
    return pokok * r * (1 + r)**n / ((1 + r)**n - 1)

def anuitas_inv(cicilan, rate_ann, tenor_thn):
    """Hitung maks pokok dari cicilan"""
    r = rate_ann / 100 / 12
    n = tenor_thn * 12
    if r == 0:
        return cicilan * n
    return cicilan * ((1 + r)**n - 1) / (r * (1 + r)**n)

# ─── SESSION STATE ───────────────────────────────────────────
if "bank_rates" not in st.session_state:
    st.session_state.bank_rates = {
        b["name"]: {"fixed": b["fixed"], "float": b["float"]}
        for b in BANKS_DEFAULT
    }

# ─── HEADER ─────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <div>
    <div class="main-title">🏠 KPR Simulator <em>Pro</em></div>
    <div class="main-sub">Platform Simulasi KPR Profesional untuk Agen Properti</div>
  </div>
  <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
    <div class="data-badge">✅ Data Riset: 2026</div>
    <a class="wa-contact" href="https://wa.me/6287884256765?text=Halo%2C%20konsultasi%20KPR" target="_blank">💬 0878 8425 6765</a>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR: DATA KONSUMEN ──────────────────────────────────
with st.sidebar:
    st.markdown("### 👤 Data Konsumen")

    nama = st.text_input("Nama Lengkap", placeholder="cth: Budi Santoso")
    hp_konsumen = st.text_input("No. Handphone", placeholder="08xx-xxxx-xxxx")
    tgl_simulasi = st.date_input("Tanggal Simulasi", value=date.today())
    status = st.selectbox("Status Pernikahan", ["", "Lajang", "Menikah", "Cerai"])

    st.markdown("---")
    st.markdown("### 💼 Pekerjaan")

    bidang = st.selectbox("Bidang Usaha / Profesi", [
        "", "Karyawan Swasta", "Pegawai Negeri (ASN/PNS)", "TNI / Polri",
        "Wiraswasta / Pengusaha", "Dokter / Tenaga Kesehatan",
        "Profesional (Lawyer, Arsitek)", "Freelancer", "Pensiunan", "Lainnya"
    ])
    perusahaan = st.text_input("Nama Perusahaan / Usaha", placeholder="cth: PT Maju Jaya Tbk")
    jabatan = st.text_input("Jabatan / Posisi", placeholder="cth: Senior Manager")
    lama_kerja = st.selectbox("Lama Bekerja", [
        "", "< 1 Tahun", "1 – 2 Tahun", "2 – 5 Tahun", "> 5 Tahun"
    ])

    st.markdown("---")
    st.markdown("### 💰 Penghasilan")

    gaji = st.number_input("Penghasilan Bulanan (Rp)", min_value=0, step=500_000, format="%d")
    gaji2 = st.number_input("Penghasilan Lain / Pasangan (Rp)", min_value=0, step=500_000, format="%d")
    total_gaji = gaji + gaji2

    if total_gaji > 0:
        st.markdown(f"**Total:** {fmt_rp(total_gaji)}/bln")
        st.markdown(f"**Maks. Cicilan (30%):** {fmt_rp(total_gaji * 0.3)}/bln")

    st.markdown("---")
    st.markdown("### 🏡 Preferensi")

    tujuan = st.selectbox("Tujuan Pembelian", ["", "Hunian Utama", "Investasi / Sewa", "Rumah Kedua"])
    lokasi = st.text_input("Lokasi Properti", placeholder="cth: Serpong, Tangerang")
    catatan = st.text_input("Catatan Agen", placeholder="cth: Hot prospect pameran")

    st.markdown("---")
    st.markdown("""
    <div style='text-align:center;padding:10px'>
      <a href='https://wa.me/6287884256765' target='_blank' style='background:linear-gradient(135deg,#25D366,#1ebe5d);border-radius:25px;padding:10px 20px;color:white;font-weight:700;text-decoration:none;font-size:13px;display:inline-block'>
        💬 Hubungi Agen<br><small>0878 8425 6765</small>
      </a>
    </div>
    """, unsafe_allow_html=True)

# ─── MAIN TABS ───────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🧮 Simulasi KPR", "🏦 Komparasi Bank", "📊 Hasil Analisis"])

# ════════════════════════════════════════════════════════════
#  TAB 1: SIMULASI KPR
# ════════════════════════════════════════════════════════════
with tab1:
    st.markdown("#### Parameter Pembiayaan")

    col1, col2 = st.columns([3, 2])
    with col1:
        harga = st.number_input(
            "🏡 Harga Properti (Rp)",
            min_value=0, step=50_000_000, format="%d",
            help="Masukkan harga properti yang ingin dibeli"
        )
        if harga > 0:
            st.caption(f"= {fmt_rp(harga)}")

    with col2:
        dp_pct = st.slider("Down Payment (%)", min_value=10, max_value=50, value=20, step=5)
        if harga > 0:
            dp_rp = harga * dp_pct / 100
            st.caption(f"DP: {fmt_rp(dp_rp)}")

    col3, col4 = st.columns(2)
    with col3:
        bunga_rate = st.slider("Suku Bunga Fixed (%/thn)", min_value=4.0, max_value=14.0, value=7.0, step=0.25)
    with col4:
        tenor = st.slider("Tenor (Tahun)", min_value=5, max_value=30, value=20, step=1)

    col5, col6 = st.columns(2)
    with col5:
        cicilan_lain = st.number_input(
            "Cicilan Lain / Bulan (Rp)",
            min_value=0, step=100_000, format="%d"
        )
        if cicilan_lain > 0:
            st.caption(f"= {fmt_rp(cicilan_lain)}")
    with col6:
        jenis_bunga = st.selectbox("Jenis Bunga", ["Fixed (Tetap)", "Floating (Estimasi)"])

    # ─── KALKULASI ───
    if harga > 0:
        pokok = harga * (1 - dp_pct / 100)
        dp = harga * dp_pct / 100
        cicilan = anuitas(pokok, bunga_rate, tenor)
        total_bayar = cicilan * tenor * 12
        total_bunga = total_bayar - pokok
        total_cicilan = cicilan + cicilan_lain
        dti = (total_cicilan / total_gaji * 100) if total_gaji > 0 else 0
        max_beli = anuitas_inv(total_gaji * 0.3, bunga_rate, tenor) * (1 / (1 - dp_pct / 100)) if total_gaji > 0 else 0

        # Big result
        st.markdown(f"""
        <div class="cicilan-hero">
          <div class="cicilan-label">Estimasi Cicilan per Bulan</div>
          <div class="cicilan-amount">{fmt_rp(cicilan)}</div>
          <div class="cicilan-sub">Tenor {tenor} tahun · Bunga {bunga_rate:.2f}%/thn · {jenis_bunga}</div>
        </div>
        """, unsafe_allow_html=True)

        # Stats grid
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div class="metric-card">
              <div class="metric-label">Harga Properti</div>
              <div class="metric-value" style="font-size:16px">{fmt_rp(harga)}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="metric-card">
              <div class="metric-label">Down Payment ({dp_pct}%)</div>
              <div class="metric-value gold" style="font-size:16px">{fmt_rp(dp)}</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="metric-card">
              <div class="metric-label">Total Bunga</div>
              <div class="metric-value" style="font-size:16px">{fmt_rp(total_bunga)}</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class="metric-card">
              <div class="metric-label">Total Kewajiban</div>
              <div class="metric-value" style="font-size:16px">{fmt_rp(total_bayar)}</div>
            </div>""", unsafe_allow_html=True)

        # Kelayakan
        if total_gaji > 0:
            if dti <= 30:
                css_class = "status-layak"
                icon = "✅"
                status_txt = "LAYAK DIPROSES"
                desc = f"Cicilan {fmt_rp(total_cicilan)}/bln = {dti:.1f}% dari penghasilan — aman di bawah 30%"
            elif dti <= 50:
                css_class = "status-batas"
                icon = "⚠️"
                status_txt = "MENDEKATI BATAS"
                desc = f"Cicilan {fmt_rp(total_cicilan)}/bln = {dti:.1f}% dari penghasilan — pertimbangkan tenor lebih panjang"
            else:
                css_class = "status-tidak"
                icon = "❌"
                status_txt = "TIDAK LAYAK"
                desc = f"Cicilan {fmt_rp(total_cicilan)}/bln = {dti:.1f}% dari penghasilan — melebihi batas 30%"

            st.markdown(f"""<div class="{css_class}">
              <strong>{icon} {status_txt}</strong><br>
              <span style="font-size:13px;color:#7a90b0">{desc}</span>
              {f'<br><span style="font-size:12px;color:#f0a500">💡 Saran: tambah DP, perpanjang tenor, atau pilih properti lebih terjangkau</span>' if dti > 50 else ''}
            </div>""", unsafe_allow_html=True)

            if max_beli > 0:
                st.info(f"💡 Berdasarkan penghasilan {fmt_rp(total_gaji)}/bln, maks. harga properti yang direkomendasikan: **{fmt_rp(max_beli)}**")

        # Amortisasi chart
        with st.expander("📈 Lihat Grafik Amortisasi"):
            r = bunga_rate / 100 / 12
            n_total = tenor * 12
            sisa = pokok
            years, pokok_list, bunga_list, sisa_list = [], [], [], []
            for i in range(1, n_total + 1):
                bunga_bln = sisa * r
                pokok_bln = cicilan - bunga_bln
                sisa -= pokok_bln
                if i % 12 == 0:
                    years.append(i // 12)
                    pokok_list.append(round(pokok_bln * 12))
                    bunga_list.append(round(bunga_bln * 12))
                    sisa_list.append(max(0, round(sisa)))

            chart_df = pd.DataFrame({
                "Tahun ke-": years,
                "Pokok (Rp juta)": [p / 1_000_000 for p in pokok_list],
                "Bunga (Rp juta)": [b / 1_000_000 for b in bunga_list],
                "Sisa Hutang (Rp juta)": [s / 1_000_000 for s in sisa_list],
            }).set_index("Tahun ke-")

            st.line_chart(chart_df[["Pokok (Rp juta)", "Bunga (Rp juta)", "Sisa Hutang (Rp juta)"]])
    else:
        st.info("👆 Masukkan harga properti untuk memulai simulasi")

# ════════════════════════════════════════════════════════════
#  TAB 2: KOMPARASI BANK
# ════════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### 🏦 Komparasi Suku Bunga — 10 Bank")
    st.caption("Data riset 16 Mei 2026 · Klik ✏️ Edit Rate untuk ubah rate manual")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        pokok_komp = st.number_input(
            "Pokok Pinjaman (Rp)",
            min_value=0, step=50_000_000, format="%d",
            value=int(harga * (1 - dp_pct / 100)) if harga > 0 else 0,
            key="pk_komp"
        )
        if pokok_komp > 0:
            st.caption(f"= {fmt_rp(pokok_komp)}")
    with col_b:
        tenor_komp = st.selectbox("Tenor", [5, 10, 15, 20, 25, 30], index=3, key="tk_komp")
    with col_c:
        sort_by = st.selectbox("Urutkan", ["Cicilan Terendah", "Bunga Terendah", "Total Bayar Terendah"])

    # ─── EDIT RATE SECTION ───
    with st.expander("✏️ Edit Rate Manual per Bank", expanded=False):
        st.markdown("**Ubah suku bunga sesuai penawaran terbaru dari bank:**")
        cols_edit = st.columns(2)
        for i, bank in enumerate(BANKS_DEFAULT):
            with cols_edit[i % 2]:
                st.markdown(f"**{bank['name']}**")
                c1e, c2e = st.columns(2)
                with c1e:
                    new_fixed = st.number_input(
                        f"Fixed % ({bank['name']})",
                        min_value=0.1, max_value=30.0,
                        value=float(st.session_state.bank_rates[bank["name"]]["fixed"]),
                        step=0.01, format="%.2f",
                        key=f"edit_fixed_{bank['name']}",
                        label_visibility="collapsed"
                    )
                    st.caption(f"Fixed (default: {bank['fixed']}%)")
                with c2e:
                    new_float = st.number_input(
                        f"Float % ({bank['name']})",
                        min_value=0.1, max_value=30.0,
                        value=float(st.session_state.bank_rates[bank["name"]]["float"]),
                        step=0.1, format="%.1f",
                        key=f"edit_float_{bank['name']}",
                        label_visibility="collapsed"
                    )
                    st.caption(f"Float (default: {bank['float']}%)")

                st.session_state.bank_rates[bank["name"]]["fixed"] = new_fixed
                st.session_state.bank_rates[bank["name"]]["float"] = new_float

        if st.button("↺ Reset Semua Rate ke Default", type="secondary"):
            for b in BANKS_DEFAULT:
                st.session_state.bank_rates[b["name"]] = {"fixed": b["fixed"], "float": b["float"]}
            st.rerun()

    # ─── TABEL KOMPARASI ───
    if pokok_komp > 0:
        rows = []
        for b in BANKS_DEFAULT:
            fe = st.session_state.bank_rates[b["name"]]["fixed"]
            fle = st.session_state.bank_rates[b["name"]]["float"]
            is_edited = (fe != b["fixed"] or fle != b["float"])
            c = anuitas(pokok_komp, fe, tenor_komp)
            tot = c * tenor_komp * 12
            rows.append({
                "Bank": b["name"],
                "Tipe": b["type"],
                "Produk": b["product"],
                "Fixed Rate": fe,
                "Fixed Rate Str": f"{fe:.2f}% {'✏️' if is_edited else ''}",
                "Floating": fle,
                "Floating Str": f"{fle:.1f}% {'✏️' if is_edited else ''}",
                "Masa Fixed": b["fix_prd"],
                "Maks Tenor": b["max_tnr"],
                "Cicilan/Bln": c,
                "Cicilan Str": fmt_rp(c),
                "Total Bayar": tot,
                "Total Str": fmt_rp(tot),
                "Total Bunga": tot - pokok_komp,
                "Over Tenor": tenor_komp > b["max_tnr"],
                "Edited": is_edited,
            })

        if sort_by == "Cicilan Terendah":
            rows.sort(key=lambda x: x["Cicilan/Bln"])
        elif sort_by == "Bunga Terendah":
            rows.sort(key=lambda x: x["Fixed Rate"])
        else:
            rows.sort(key=lambda x: x["Total Bayar"])

        if rows:
            min_cicilan = rows[0]["Cicilan/Bln"]

            for i, r in enumerate(rows):
                is_best = i == 0
                selisih = r["Cicilan/Bln"] - min_cicilan
                edited_tag = "✏️" if r["Edited"] else ""
                best_tag = " TERBAIK" if is_best else ""
                over_tag = " ⚠️" if r["Over Tenor"] else ""
                # lanjut kode tabel lo...
else:
    st.info("💡 Isi Pokok Pinjaman dulu untuk melihat perbandingan 10 bank")
