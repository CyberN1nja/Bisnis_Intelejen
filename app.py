from flask import Flask, request, jsonify, render_template
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

app = Flask(__name__)

# Muat model LSTM yang telah dilatih
model = tf.keras.models.load_model('model/dataLatih.h5')

# Muat dan lakukan pra-pemrosesan pada dataset
data = pd.read_csv('model/data_hasil_preprocessing_koordinat.csv')

# Fungsi normalisasi kategori pelanggaran


def normalize_kategori_pelanggaran(kategori):
    if kategori in ['PERKELAHIAN', 'PERKELAHIAN KELUARGA', 'PERKELAHIAN YANG MENIMBULKAN LUKA PARAH']:
        return 'PERKELAHIAN'
    elif kategori in ['PENCURIAN KENDARAAN BERMOTOR', 'PENCURIAN RODA DUA', 'PENCURIAN MOTOR', 'CURANMOR']:
        return 'PENCURIAN KENDARAAN BERMOTOR'
    elif kategori in ['BEGAL', 'BEGAL - TAWURAN - GENG MOTOR']:
        return 'BEGAL'
    elif kategori in ['BALAP LIAR', 'KERIBUTAN WARGA']:
        return 'GANGGUAN KETERTIBAN UMUM'
    else:
        return kategori


# Pra-pemrosesan data
data['kategori_pelanggaran'] = data['kategori_pelanggaran'].apply(
    normalize_kategori_pelanggaran)

label_encoder_pelanggaran = LabelEncoder()
label_encoder_kecamatan = LabelEncoder()
label_encoder_desa = LabelEncoder()

data['kategori_pelanggaran'] = label_encoder_pelanggaran.fit_transform(
    data['kategori_pelanggaran'])
data['bps_nama_kecamatan'] = label_encoder_kecamatan.fit_transform(
    data['bps_nama_kecamatan'])
data['bps_desa_kelurahan'] = label_encoder_desa.fit_transform(
    data['bps_desa_kelurahan'])

scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(
    data[['kategori_pelanggaran', 'bps_nama_kecamatan', 'bps_desa_kelurahan']])

# Fungsi prediksi


def predict_future_months(model, initial_input, num_months):
    predictions = []
    current_input = np.reshape(initial_input, (1, 1, -1))

    for _ in range(num_months):
        next_pred = model.predict(current_input)
        predictions.append(next_pred[0])

        next_pred_reshaped = np.reshape(next_pred, (1, 1, -1))
        current_input = np.concatenate(
            (current_input[1:], next_pred_reshaped), axis=0)

    return np.array(predictions)

# Route utama untuk menampilkan visualisasi


@app.route('/')
def index():
    return visualisasi()


@app.route('/visualisasi')
def visualisasi():
    # Membaca file CSV
    df = pd.read_csv('model/data_hasil_preprocessing_koordinat.csv')

    kategori_pelanggaran = df['kategori_pelanggaran'].value_counts().to_dict()
    tahun = df['tahun'].value_counts().to_dict()
    desa_kelurahan = df['bps_desa_kelurahan'].value_counts().to_dict()
    kecamatan = df['bps_nama_kecamatan'].value_counts().to_dict()

    return render_template(
        'index.html',
        kategori_pelanggaran=kategori_pelanggaran,
        tahun=tahun,
        desa_kelurahan=desa_kelurahan,
        kecamatan=kecamatan
    )

# Route untuk halaman analisis


@app.route('/analisis')
def analisis():
    return render_template('hasilanalisis.html')

# Route untuk prediksi data kejahatan


@app.route('/predict-crime-data', methods=['POST'])
def predict_crime_data():
    try:
        input_data = request.json
        kategori_pelanggaran = input_data['kategori_pelanggaran']
        nama_kecamatan = input_data['bps_nama_kecamatan']
        desa_kelurahan = input_data['bps_desa_kelurahan']

        # Normalisasi kategori pelanggaran input dari pengguna
        kategori_pelanggaran = normalize_kategori_pelanggaran(
            kategori_pelanggaran)

        # Encode input user dengan LabelEncoder yang telah digunakan sebelumnya
        encoded_pelanggaran = label_encoder_pelanggaran.transform(
            [kategori_pelanggaran])
        encoded_kecamatan = label_encoder_kecamatan.transform([nama_kecamatan])
        encoded_desa = label_encoder_desa.transform([desa_kelurahan])

        # Kombinasikan fitur yang telah diencode dan lakukan normalisasi
        input_features = np.array(
            [[encoded_pelanggaran[0], encoded_kecamatan[0], encoded_desa[0]]])
        scaled_input = scaler.transform(input_features)
        scaled_input = np.reshape(scaled_input, (1, 1, scaled_input.shape[1]))

        # Prediksi 12 bulan ke depan
        num_months = 12
        future_predictions = predict_future_months(
            model, scaled_input, num_months)

        # Scaler inverse transform untuk mendapatkan nilai asli
        future_predictions_expanded = np.concatenate(
            [future_predictions, np.zeros(
                (future_predictions.shape[0], scaled_data.shape[1] - future_predictions.shape[1]))],
            axis=1
        )
        future_predictions_original = scaler.inverse_transform(
            future_predictions_expanded)[:, :scaled_data.shape[1]]

        # Nama bulan
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        # Buat data untuk dikirimkan ke frontend
        bar_chart_data = {
            "labels": months,
            "values": [pred[0] for pred in future_predictions_original]
        }

        line_chart_data = {
            "labels": months,
            "values": [pred[0] * 0.8 for pred in future_predictions_original]
        }

        return jsonify({
            "bar": bar_chart_data,
            "line": line_chart_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
