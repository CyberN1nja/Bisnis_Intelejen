//  // Data from Flask
//         const kategoriKejahatan = {{ kategori_pelanggaran | tojson }};
//         const tahun = {{ tahun | tojson }};
//         const desaKelurahan = {{ desa_kelurahan | tojson }};
//         const kecamatan = {{ kecamatan | tojson }};

//         // Chart for Crime Categories by District
//         new Chart(document.getElementById('barChart'), {
//             type: 'bar',
//             data: {
//                 labels: Object.keys(kecamatan),
//                 datasets: [{
//                     label: 'Jumlah Kejahatan per Jenis',
//                     data: Object.values(kecamatan),
//                     backgroundColor: 'rgba(75, 192, 192, 0.2)',
//                     borderColor: 'rgba(75, 192, 192, 1)',
//                     borderWidth: 1
//                 }]
//             },
//             options: {
//                 scales: {
//                     y: {
//                         beginAtZero: true
//                     }
//                 }
//             }
//         });

//         // Line Chart for Crime Trend Over Years
//         new Chart(document.getElementById('lineChart'), {
//             type: 'line',
//             data: {
//                 labels: Object.keys(tahun),
//                 datasets: [{
//                     label: 'Jumlah Kejahatan per Tahun',
//                     data: Object.values(tahun),
//                     fill: false,
//                     borderColor: 'rgba(75, 192, 192, 1)',
//                     tension: 0.1
//                 }]
//             },
//             options: {
//                 scales: {
//                     y: {
//                         beginAtZero: true
//                     }
//                 }
//             }
//         });

//         // Pie Chart for Crime Proportions
//         new Chart(document.getElementById('pieChart'), {
//             type: 'pie',
//             data: {
//                 labels: Object.keys(kategoriKejahatan),
//                 datasets: [{
//                     label: 'Proporsi Jenis Kejahatan',
//                     data: Object.values(kategoriKejahatan),
//                     backgroundColor: [
//                         'rgba(255, 99, 132, 0.2)',
//                         'rgba(54, 162, 235, 0.2)',
//                         'rgba(255, 206, 86, 0.2)',
//                         'rgba(75, 192, 192, 0.2)',
//                         'rgba(153, 102, 255, 0.2)',
//                         'rgba(255, 159, 64, 0.2)'
//                     ],
//                     borderColor: [
//                         'rgba(255, 99, 132, 1)',
//                         'rgba(54, 162, 235, 1)',
//                         'rgba(255, 206, 86, 1)',
//                         'rgba(75, 192, 192, 1)',
//                         'rgba(153, 102, 255, 1)',
//                         'rgba(255, 159, 64, 1)'
//                     ],
//                     borderWidth: 1
//                 }]
//             }
//         });