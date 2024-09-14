document.getElementById('crime-data-form').addEventListener('submit', function (event) {
  event.preventDefault();

  const formData = {
    kategori_pelanggaran: document.getElementById('kategori_pelanggaran').value,
    bps_nama_kecamatan: document.getElementById('bps_nama_kecamatan').value.toUpperCase(),
    bps_desa_kelurahan: document.getElementById('bps_desa_kelurahan').value.toUpperCase(),
  };

  const validKecamatanDesa = {
    ANTAPANI: ['ANTAPANI KIDUL', 'ANTAPANI KULON'],
    'UJUNG BERUNG': ['PASIR ENDAH', 'CIGENDING', 'PASIR WANGI', 'PASIRJATI'],
    GEDEBAGE: ['RANCABOLANG', 'RANCANUMPANG', 'CIMINCRANG'],
    CIDADAP: ['HEGARMANAH', 'CIUMBULEUIT', 'LEDENG'],
    ARCAMANIK: ['CISARANTEN BINA HARAPAN', 'CISARANTEN KULON', 'SUKAMISKIN', 'CISARANTEN ENDAH'],
    'BOJONGLOA KIDUL': ['SITUSAEUR', 'CIBADUYUT KIDUL'],
    BATUNUNGGAL: ['BINONG'],
    SUKASARI: ['GEGERKALONG', 'SUKARASA', 'ISOLA', 'SARIJADI'],
  };

  const kecamatan = formData.bps_nama_kecamatan;
  const desa = formData.bps_desa_kelurahan;

  // Validasi kecamatan dan desa
  if (!validKecamatanDesa[kecamatan] || !validKecamatanDesa[kecamatan].includes(desa)) {
    alert('Desa/Kelurahan tidak valid untuk Kecamatan yang dipilih.');
    return;
  }

  // Fetch data dari server (contoh URL, sesuaikan dengan endpoint Anda)
  fetch('/predict-crime-data', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(formData),
  })
    .then((response) => response.json())
    .then((data) => {
      displayForecast(data);
    })
    .catch((error) => console.error('Error:', error));
});

function displayForecast(data) {
  const ctxBar = document.getElementById('bar-chart').getContext('2d');
  const ctxLine = document.getElementById('line-chart').getContext('2d');
  const forecastTableBody = document.getElementById('forecast-table').getElementsByTagName('tbody')[0];

  // Data untuk grafik bar
  const barChartData = {
    labels: data.bar.labels,
    datasets: [
      {
        label: 'Jumlah Kasus Aktual',
        data: data.bar.values,
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
    ],
  };

  // Data untuk grafik garis
  const lineChartData = {
    labels: data.line.labels,
    datasets: [
      {
        label: 'Prediksi Kasus',
        data: data.line.values,
        fill: false,
        borderColor: 'rgba(255, 99, 132, 1)',
        tension: 0.1,
      },
    ],
  };

  // Membuat grafik bar
  new Chart(ctxBar, {
    type: 'bar',
    data: barChartData,
    options: {
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });

  // Membuat grafik garis
  new Chart(ctxLine, {
    type: 'line',
    data: lineChartData,
    options: {
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });

  // Mengisi tabel peramalan
  forecastTableBody.innerHTML = ''; // Kosongkan tabel sebelum mengisi data
  data.bar.labels.forEach((label, index) => {
    const row = forecastTableBody.insertRow();
    const cellMonth = row.insertCell(0);
    const cellActual = row.insertCell(1);
    const cellPredicted = row.insertCell(2);

    cellMonth.textContent = label;
    cellActual.textContent = data.bar.values[index] || 0; // Menangani nilai yang mungkin tidak ada
    cellPredicted.textContent = data.line.values[index] || 0; // Menangani nilai yang mungkin tidak ada
  });
}

const contactBtn = document.getElementById('contactBtn');
const hiddenText = document.getElementById('hiddenText');

// Menambahkan event listener untuk klik
contactBtn.addEventListener('click', function (event) {
  event.preventDefault(); // Mencegah link membuka URL
  // Menampilkan teks yang disembunyikan
  hiddenText.style.display = 'block';
});
