import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans

# Membaca data CSV
df = pd.read_csv('model/data_hasil_preprocessing_koordinat.csv')

# Memilih kolom yang akan digunakan dan membuat salinan DataFrame
df_selected = df[['bps_kode_desa_kelurahan',
                  'bps_desa_kelurahan', 'kategori_pelanggaran',
                  'latitude_desa', 'longitude_desa']].copy()

# Encoding kategori pelanggaran (proses mengubah data kategorikal (non-numerik) menjadi format numerik yang dapat digunakan oleh algoritma machine learning dan analisis data. )
label_encoder = LabelEncoder()
df_selected['kategori_pelanggaran_encoded'] = label_encoder.fit_transform(
    df_selected['kategori_pelanggaran'])

# Normalisasi data yang sudah di encoding
scaler = StandardScaler()
df_selected_scaled = scaler.fit_transform(
    df_selected[['kategori_pelanggaran_encoded']])

# Menentukan jumlah klaster berdasarkan kategori
num_clusters = 5

# Melakukan clustering dengan K-means
# membagi data menjadi grup yang berbeda, di mana setiap grup(klaster) memiliki data yang lebih mirip satu sama lain daripada dengan data di klaster lain.
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
df_selected['cluster'] = kmeans.fit_predict(df_selected_scaled)

# Menghitung jumlah kategori pelanggaran per desa
# menghitung jumlah kasus untuk setiap kombinasi unik dari beberapa atribut dalam DataFrame.
category_count = df_selected.groupby(['bps_kode_desa_kelurahan', 'bps_desa_kelurahan', 'latitude_desa',
                                     'longitude_desa', 'cluster', 'kategori_pelanggaran']).size().reset_index(name='count')

print('hasil hitung : ', category_count)

# Membaca data geospasial
gdf = gpd.read_file('maps.geojson')

# Mengubah CRS ke EPSG:3857 untuk perhitungan centroid
gdf = gdf.to_crs(epsg=3857)

# Menghitung centroid dan mengekstrak koordinat dari centroid
gdf['centroid'] = gdf['geometry'].centroid
gdf['latitude_desa'] = gdf['centroid'].y
gdf['longitude_desa'] = gdf['centroid'].x

# Mengembalikan CRS ke CRS awal jika perlu
gdf = gdf.to_crs(epsg=4326)

# Gabungkan dengan hasil clustering menggunakan kolom 'latitude_desa' dan 'longitude_desa'
df_selected['key'] = df_selected.apply(lambda row: (
    row['latitude_desa'], row['longitude_desa']), axis=1)
gdf['key'] = gdf.apply(lambda row: (
    row['latitude_desa'], row['longitude_desa']), axis=1)

# Menggabungkan data geospasial dengan hasil clustering berdasarkan koordinat
gdf = gdf.merge(df_selected[['key', 'cluster']], on='key', how='left')

# Cek beberapa baris pertama dari gdf setelah penggabungan
print("GeoDataFrame setelah penggabungan:", gdf.head())

# Cek apakah ada nilai NaN atau 'N/A' dalam kolom penting
print("Cek nilai NaN atau 'N/A' dalam data:")
print(df_selected[['latitude_desa',
      'longitude_desa', 'cluster']].isna().sum())
print(gdf[['latitude_desa', 'longitude_desa', 'cluster']].isna().sum())

# Membuat peta menggunakan Folium
m = folium.Map(location=[-6.91475, 107.60981], zoom_start=12)

# Menambahkan marker cluster
marker_cluster = MarkerCluster().add_to(m)

# Menambahkan marker untuk setiap desa dengan jumlah kategori pelanggaran ?
for _, row in category_count.iterrows():
    if pd.notna(row['latitude_desa']) and pd.notna(row['longitude_desa']):
        folium.Marker(
            location=[row['latitude_desa'], row['longitude_desa']],
            popup=f"Desa/Kelurahan: {row['bps_desa_kelurahan']}<br>Cluster: {
                row['cluster']}<br>Kategori: {row['kategori_pelanggaran']}<br>Jumlah: {row['count']}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(marker_cluster)
    else:
        print(f"Koordinat tidak valid untuk desa: {
              row.get('bps_desa_kelurahan', 'N/A')}")

# Menyimpan peta ke file HTML
map_html_path = 'static/maps/peta_clustering.html'
m.save(map_html_path)

print(f"Peta berhasil disimpan di {map_html_path}")
