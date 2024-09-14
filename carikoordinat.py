import pandas as pd

# Baca file utama yang memerlukan kolom koordinat
df = pd.read_csv('data_combined_preprocessed.csv')

# Baca file referensi yang berisi koordinat
coordinates_ref = pd.read_csv('coordinates_reference.csv')

# Tampilkan beberapa baris pertama dari file referensi
print("File Referensi:")
print(coordinates_ref.head())

# Gabungkan berdasarkan bps_kode_kecamatan
df_with_lat_lon = df.merge(
    coordinates_ref[['bps_kode_kecamatan', 'latitude', 'longitude']],
    on='bps_kode_kecamatan',
    how='left',
    suffixes=('', '_kecamatan')
)

# Gabungkan berdasarkan bps_kode_desa_kelurahan
df_with_lat_lon = df_with_lat_lon.merge(
    coordinates_ref[['bps_kode_desa_kelurahan', 'latitude', 'longitude']],
    on='bps_kode_desa_kelurahan',
    how='left',
    suffixes=('', '_desa')
)

# Tampilkan beberapa baris pertama dari data yang sudah digabungkan
print("Data yang sudah digabungkan:")
print(df_with_lat_lon.head())

# Simpan hasil ke file CSV baru
output_file = 'data_combined_with_coordinates.csv'
df_with_lat_lon.to_csv(output_file, index=False)

print(f"Data dengan koordinat berhasil disimpan ke {output_file}")
