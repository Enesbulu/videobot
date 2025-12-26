
let eventSource = null;

function log(msg, type = 'info') {
    const consoleDiv = document.getElementById('logConsole');
    const time = new Date().toLocaleTimeString();
    let colorClass = '';

    if (type === 'error') colorClass = 'log-error';
    if (type === 'warning') colorClass = 'log-warning';
    if (type === 'success') colorClass = 'log-success';

    // Console'u temiz tutmak için sadece önemli mesajları yaz
    consoleDiv.innerHTML += `<div class="log-line ${colorClass}"><span class="log-time">[${time}]</span> ${msg}</div>`;
    consoleDiv.scrollTop = consoleDiv.scrollHeight;
}

function updateStats(stats) {
    if (!stats) return;
    document.getElementById('pageCount').innerText = stats.pages + " / " + stats.max_pages;
    document.getElementById('videoCount').innerText = stats.videos;
}

function startScan() {
    const url = document.getElementById('targetUrl').value;
    const isCrawl = document.getElementById('crawlMode').checked;

    if (!url) { alert("URL Giriniz"); return; }

    // UI Temizle
    document.getElementById('logConsole').innerHTML = '';
    document.getElementById('videoTableBody').innerHTML = '';
    document.getElementById('statsArea').style.display = 'flex';
    document.getElementById('consoleArea').style.display = 'block';
    document.getElementById('resultsArea').style.display = 'none';
    document.getElementById('statusText').innerText = 'Başlatılıyor...';

    if (eventSource) eventSource.close();

    eventSource = new EventSource(`/stream_crawl?url=${encodeURIComponent(url)}&crawler=${isCrawl}`);

    eventSource.onmessage = function (e) {
        const data = JSON.parse(e.data);
        const payload = data.payload;

        // 1. İstatistikleri Her Mesajda Güncelle (Canlı Sayaç)
        if (payload.stats) {
            updateStats(payload.stats);
        }

        // 2. Mesaj Türüne Göre İşlem Yap
        switch (data.type) {
            case 'log':
                log(payload.message);
                break;
            case 'status':
                // Status mesajlarını konsola yazma, sadece yukarıdaki kutuya yaz
                document.getElementById('statusText').innerText = payload.message;
                break;
            case 'video_found':
                log(payload.message, 'success');
                break;
            case 'warning':
                log(payload.message, 'warning');
                break;
            case 'error':
                log(payload.message, 'error');
                break;
            case 'finish':
                eventSource.close();
                document.getElementById('statusText').innerText = 'Tamamlandı';
                log("🏁 Tarama bitti. Sonuçlar getiriliyor...", "success");
                loadResults();
                break;
        }
    };

    eventSource.onerror = function () {
        log("Bağlantı kesildi.", 'error');
        eventSource.close();
    };
}

async function loadResults() {
    try {
        const response = await fetch('/get_results');
        const videos = await response.json();
        const tbody = document.getElementById('videoTableBody');
        tbody.innerHTML = '';

        if (videos.length > 0) {
            document.getElementById('resultsArea').style.display = 'block';
            videos.forEach((v, idx) => {
                tbody.innerHTML += `
                        <tr>
                            <td><input type="checkbox" class="form-check-input vid-check" value="${v.url}" data-title="${v.title}"></td>
                            <td class="fw-bold">${v.title}</td>
                            <td><a href="${v.url}" target="_blank" class="text-decoration-none text-muted small">${v.url}</a></td>
                            <td class="status-cell"><span class="badge bg-secondary">Bekliyor</span></td>
                        </tr>`;
            });
        } else {
            log("❌ Video bulunamadı.", 'warning');
        }
    } catch (e) { log(e, 'error'); }
}

function toggleAll(src) { document.querySelectorAll('.vid-check').forEach(c => c.checked = src.checked); }

async function downloadSelected() {
    const checks = document.querySelectorAll('.vid-check:checked');
    if (!checks.length) return alert("Seçim yapın.");
    if (!confirm(checks.length + " video indirilecek?")) return;

    for (let chk of checks) {
        const cell = chk.closest('tr').querySelector('.status-cell');
        cell.innerHTML = '<span class="spinner-border spinner-border-sm text-info"></span>';

        try {
            const res = await fetch('/api/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: chk.value, title: chk.getAttribute('data-title') })
            });
            const r = await res.json();
            cell.innerHTML = r.success ? '<span class="badge bg-success">İndi</span>' : '<span class="badge bg-danger">Hata</span>';
            if (r.success) chk.checked = false;
        } catch (e) { cell.innerHTML = 'Hata'; }
    }
}
