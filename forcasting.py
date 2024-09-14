import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

# Memuat data
data = pd.read_csv('model/data_hasil_preprocessing_koordinat.csv')

# Fungsi untuk menggabungkan kategori kejahatan yang memiliki makna sama


def normalize_kategori_pelanggaran(kategori_pelanggaran):
    if kategori_pelanggaran in ['PERKELAHIAN', 'PERKELAHIAN KELUARGA', 'PERKELAHIAN YANG MENIMBULKAN LUKA PARAH']:
        return 'PERKELAHIAN'
    elif kategori_pelanggaran in ['PENCURIAN KENDARAAN BERMOTOR', 'PENCURIAN RODA DUA', 'PENCURIAN MOTOR', 'CURANMOR']:
        return 'PENCURIAN KENDARAAN BERMOTOR'
    elif kategori_pelanggaran in ['BEGAL', 'BEGAL - TAWURAN - GENG MOTOR']:
        return 'BEGAL'
    elif kategori_pelanggaran in ['BALAP LIAR', 'KERIBUTAN WARGA']:
        return 'GANGGUAN KETERTIBAN UMUM'
    else:
        return kategori_pelanggaran


# Normalisasi kategori pelanggaran
data['kategori_pelanggaran'] = data['kategori_pelanggaran'].apply(
    normalize_kategori_pelanggaran)

# Inisialisasi LabelEncoder
label_encoder = LabelEncoder()

# Encode kolom kategorikal menjadi numerik
data['kategori_pelanggaran'] = label_encoder.fit_transform(
    data['kategori_pelanggaran'])
data['bps_nama_kecamatan'] = label_encoder.fit_transform(
    data['bps_nama_kecamatan'])
data['bps_desa_kelurahan'] = label_encoder.fit_transform(
    data['bps_desa_kelurahan'])

# Normalisasi data
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(
    data[['kategori_pelanggaran', 'bps_nama_kecamatan', 'bps_desa_kelurahan']])

# Memisahkan fitur (X) dan target (y)
X, y = [], []
time_step = 5  # Jumlah langkah waktu yang digunakan untuk memprediksi langkah waktu berikutnya

for i in range(len(scaled_data) - time_step):
    X.append(scaled_data[i:i + time_step])
    y.append(scaled_data[i + time_step])

X = np.array(X)
y = np.array(y)

# Membagi data menjadi data latih dan uji
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# Membuat model LSTM
model = tf.keras.Sequential([
    tf.keras.layers.LSTM(50, return_sequences=True, input_shape=(
        X_train.shape[1], X_train.shape[2])),
    tf.keras.layers.LSTM(50),
    tf.keras.layers.Dense(X_train.shape[2])
])

# Mengonfigurasi model yang telah dibuat dengan TensorFlow/Keras sebelum melatihnya.
model.compile(optimizer='adam', loss='mean_squared_error')

# Melatih model sebanyak 200 kali
model.fit(X_train, y_train, epochs=200, batch_size=32, validation_split=0.1)

# Evaluasi model
loss = model.evaluate(X_test, y_test)
print(f"Test Loss: {loss}")

# Prediksi pada data uji
y_pred = model.predict(X_test)

# Menghitung dan menampilkan MAE, MSE, dan RMSE
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)

print(f"Mean Absolute Error (MAE): {mae}")
print(f"Mean Squared Error (MSE): {mse}")
print(f"Root Mean Squared Error (RMSE): {rmse}")

# Menyimpan model
model.save('model/dataLatih.h5')

# Fungsi untuk memprediksi 12 bulan ke depan


def predict_future_months(model, initial_input, num_months):
    predictions = []
    current_input = np.reshape(
        initial_input, (1, X_train.shape[1], X_train.shape[2]))

    for _ in range(num_months):
        # Predict next month
        next_pred = model.predict(current_input)
        predictions.append(next_pred[0])

        # Update input for the next prediction
        next_input = np.append(
            current_input[:, 1:, :], next_pred.reshape(1, 1, -1), axis=1)
        current_input = next_input

    return np.array(predictions)


# Load the model and predict
loaded_model = tf.keras.models.load_model('model/dataLatih.h5')

# Ambil input awal untuk prediksi (misalnya data terakhir dari X_test)
initial_input = X_test[-1]
num_months = 12
future_predictions = predict_future_months(
    loaded_model, initial_input, num_months)

# Scaler inverse transform untuk mendapatkan nilai asli
future_predictions = scaler.inverse_transform(
    np.concatenate(
        [future_predictions, np.zeros(
            (future_predictions.shape[0], scaled_data.shape[1] - future_predictions.shape[1]))],
        axis=1
    )
)[:, :scaled_data.shape[1]]

print("Future Predictions:", future_predictions)

# Visualisasi data aktual dan prediksi
plt.figure(figsize=(12, 6))
# Menggunakan kolom pertama untuk plotting
plt.plot(range(len(y_test)), y_test[:, 0], label='Data Aktual')
# Menggunakan kolom pertama untuk plotting
plt.plot(range(len(y_pred)), y_pred[:, 0], label='Prediksi')
plt.legend()
plt.xlabel('Indeks Data')
plt.ylabel('Jumlah Kasus')
plt.title('Perbandingan Data Aktual dan Prediksi')
plt.show()
