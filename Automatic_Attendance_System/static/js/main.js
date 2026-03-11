document.addEventListener('DOMContentLoaded', () => {

    const startCamBtn = document.getElementById('startCamBtn');
    const stopCamBtn = document.getElementById('stopCamBtn');
    const videoStream = document.getElementById('videoStream');
    const videoPlaceholder = document.getElementById('videoPlaceholder');
    const logsTableBody = document.getElementById('logsTableBody');
    const refreshLogsBtn = document.getElementById('refreshLogsBtn');
    const manualEntryForm = document.getElementById('manualEntryForm');
    const manualMsg = document.getElementById('manualMsg');

    const camStatusDot = document.getElementById('camStatusDot');
    const camStatusText = document.getElementById('camStatusText');

    let logsInterval;
    let audioAlertsEnabled = false;
    let lastLogCount = 0;

    function playAudioAlert() {
        if (!audioAlertsEnabled) return;
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.type = 'sine';
            osc.frequency.setValueAtTime(880, ctx.currentTime);
            gain.gain.setValueAtTime(0.1, ctx.currentTime);
            osc.start();
            gain.gain.exponentialRampToValueAtTime(0.00001, ctx.currentTime + 0.3);
            osc.stop(ctx.currentTime + 0.3);
        } catch (e) {
            console.error('Audio alert failed', e);
        }
    }

    // Fetch camera status on load
    checkCameraStatus();
    fetchLogs();

    // Date
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('currentDate').innerText = new Date().toLocaleDateString('en-US', options);

    startCamBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/camera/start', { method: 'POST' });
            if (response.ok) {
                setCameraState(true);
            }
        } catch (error) {
            console.error('Failed to start camera:', error);
        }
    });

    stopCamBtn.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/camera/stop', { method: 'POST' });
            if (response.ok) {
                setCameraState(false);
            }
        } catch (error) {
            console.error('Failed to stop camera:', error);
        }
    });

    refreshLogsBtn.addEventListener('click', fetchLogs);

    manualEntryForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('manualName').value;
        try {
            const response = await fetch('/api/attendance/manual', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });
            const data = await response.json();

            manualMsg.innerText = data.message;
            manualMsg.className = `feedback-msg ${data.status === 'success' ? 'success' : 'info'}`;
            manualMsg.style.display = 'block';

            setTimeout(() => { manualMsg.style.display = 'none'; }, 3000);
            document.getElementById('manualName').value = '';
            fetchLogs();
        } catch (error) {
            console.error('Manual entry failed:', error);
        }
    });

    async function checkCameraStatus() {
        try {
            const response = await fetch('/api/camera/status');
            const data = await response.json();
            setCameraState(data.active);
            if (data.active) {
                pollRecognition();
            }
        } catch (error) {
            console.error('Status check failed:', error);
        }
    }

    let lastMatchedName = "";
    async function pollRecognition() {
        try {
            const response = await fetch('/api/camera/last_recognized');
            const result = await response.json();

            if (result.status === 'success' || result.status === 'partial') {
                const data = result.data;
                const name = data.name || "Unknown";

                if (name !== lastMatchedName) {
                    lastMatchedName = name;
                    updateRecognitionUI(data);
                }
            }
        } catch (error) {
            console.error('Recognition poll failed:', error);
        }
    }

    function updateRecognitionUI(data) {
        const nameEl = document.getElementById('lastRecName');
        const detailsEl = document.getElementById('lastRecDetails');
        const rollEl = document.getElementById('lastRecRoll');
        const deptEl = document.getElementById('lastRecDept');
        const ageEl = document.getElementById('lastRecAge');
        const statusEl = document.getElementById('lastRecStatus');
        const imgEl = document.getElementById('lastRecImg');

        nameEl.innerText = data.name;

        if (data.roll_no) {
            rollEl.innerText = data.roll_no;
            deptEl.innerText = data.dept || 'N/A';
            ageEl.innerText = data.age || 'N/A';
            detailsEl.style.display = 'block';
            statusEl.style.display = 'inline-block';

            // Show image if available
            imgEl.innerHTML = `<img src="/api/students/photo?name=${encodeURIComponent(data.name)}&t=${Date.now()}" 
                                   style="width: 100%; height: 100%; object-fit: cover;" 
                                   onerror="this.parentElement.innerHTML='<span style=\'font-size: 2em; opacity: 0.2;\'>👤</span>'">`;
        } else {
            detailsEl.style.display = 'none';
            statusEl.style.display = 'none';
            imgEl.innerHTML = '<span style="font-size: 2em; opacity: 0.2;">👤</span>';
        }
    }

    function setCameraState(isActive) {
        if (isActive) {
            videoStream.src = '/video_feed?' + new Date().getTime();
            videoStream.style.display = 'block';
            videoPlaceholder.style.display = 'none';

            startCamBtn.disabled = true;
            stopCamBtn.disabled = false;

            camStatusDot.className = 'status-dot online';
            camStatusText.innerText = 'Scanning Active';

            // Auto-refresh logs while scanning
            if (!logsInterval) {
                logsInterval = setInterval(() => {
                    fetchLogs();
                    pollRecognition();
                }, 2000);
            }
        } else {
            videoStream.src = '';
            videoStream.style.display = 'none';
            videoPlaceholder.style.display = 'flex';

            startCamBtn.disabled = false;
            stopCamBtn.disabled = true;

            camStatusDot.className = 'status-dot offline';
            camStatusText.innerText = 'Camera Offline';

            // Stop auto-refresh
            if (logsInterval) {
                clearInterval(logsInterval);
                logsInterval = null;
            }

            // Reset recognition UI
            lastMatchedName = "";
            document.getElementById('lastRecName').innerText = "Waiting...";
            document.getElementById('lastRecDetails').style.display = 'none';
            document.getElementById('lastRecStatus').style.display = 'none';
            document.getElementById('lastRecImg').innerHTML = '<span style="font-size: 2em; opacity: 0.2;">👤</span>';
        }
    }

    async function fetchLogs() {
        try {
            refreshLogsBtn.classList.add('spinning');
            const response = await fetch('/api/logs?' + new Date().getTime());
            const data = await response.json();

            if (data.status === 'success' && Array.isArray(data.data)) {
                renderLogs(data.data);
            }
        } catch (error) {
            console.error('Failed to fetch logs:', error);
        } finally {
            setTimeout(() => refreshLogsBtn.classList.remove('spinning'), 500);
        }
    }

    function renderLogs(logs) {
        if (lastLogCount > 0 && logs.length > lastLogCount) {
            playAudioAlert();
        }
        lastLogCount = logs.length;

        logsTableBody.innerHTML = '';

        // Take top 15 logs for display
        const recentLogs = logs.slice(0, 15);

        recentLogs.forEach((log, index) => {
            const tr = document.createElement('tr');
            tr.style.animationDelay = `${index * 0.05}s`;

            let statusBadge = '';
            if (log.Status === 'Auto-Detected') {
                statusBadge = `<span class="badge badge-success">Auto-Detected</span>`;
            } else {
                statusBadge = `<span class="badge badge-info">${log.Status}</span>`;
            }

            tr.innerHTML = `
                <td><strong>${log.Name || 'N/A'}</strong></td>
                <td>${log['Roll No'] || 'N/A'}</td>
                <td>${log.Department || 'N/A'}</td>
                <td><span class="text-secondary">${log['In Time'] || 'N/A'}</span></td>
                <td><span class="text-secondary">${log['Out Time'] || 'N/A'}</span></td>
                <td>${statusBadge}</td>
            `;
            logsTableBody.appendChild(tr);
        });

        if (logs.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td colspan="6" style="text-align: center; color: #a0aec0;">No attendance records found.</td>`;
            logsTableBody.appendChild(tr);
        }
    }

    // --- STUDENT LOGIC TAB ---
    const navDashboard = document.getElementById('navDashboard');
    const navStudentLogic = document.getElementById('navStudentLogic');
    const viewDashboard = document.getElementById('viewDashboard');
    const viewStudentLogic = document.getElementById('viewStudentLogic');
    const pageTitle = document.getElementById('pageTitle');

    if (navDashboard && navStudentLogic) {
        const navSettings = document.getElementById('navSettings');
        const viewSettings = document.getElementById('viewSettings');

        function switchTab(activeNav, activeView, title) {
            navDashboard.classList.remove('active');
            navStudentLogic.classList.remove('active');
            if (navSettings) navSettings.classList.remove('active');

            viewDashboard.style.display = 'none';
            viewStudentLogic.style.display = 'none';
            if (viewSettings) viewSettings.style.display = 'none';

            activeNav.classList.add('active');
            activeView.style.display = 'grid'; // grid or block, both work for these containers
            pageTitle.innerText = title;
        }

        navDashboard.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab(navDashboard, viewDashboard, 'Live Dashboard');
        });

        navStudentLogic.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab(navStudentLogic, viewStudentLogic, 'Student Logic');
            fetchProgress();
        });

        if (navSettings) {
            navSettings.addEventListener('click', (e) => {
                e.preventDefault();
                switchTab(navSettings, viewSettings, 'System Settings');
                loadSettings();
            });
        }
    }

    // --- ENROLLMENT & PROGRESS ---
    const enrollmentForm = document.getElementById('enrollmentForm');
    const enrollMsg = document.getElementById('enrollMsg');

    if (enrollmentForm) {
        enrollmentForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData();
            formData.append('name', document.getElementById('enrollName').value);
            formData.append('roll_no', document.getElementById('enrollRoll').value);
            formData.append('dept', document.getElementById('enrollDept').value);
            formData.append('age', document.getElementById('enrollAge').value);
            formData.append('email', document.getElementById('enrollEmail').value);

            const photoInput = document.getElementById('enrollPhoto');
            if (photoInput.files.length > 0) {
                formData.append('photo', photoInput.files[0]);
            }

            try {
                const response = await fetch('/api/students/enroll', {
                    method: 'POST',
                    body: formData
                });
                const resData = await response.json();

                enrollMsg.innerText = resData.message;
                // Treat anything that's not explicitly 'success' or 'info' as an error in style
                enrollMsg.className = `feedback-msg ${resData.status === 'success' ? 'success' : 'info'}`;
                if (resData.status !== 'success' && resData.status !== 'info') {
                    enrollMsg.style.background = 'rgba(239, 68, 68, 0.2)';
                    enrollMsg.style.color = '#ef4444';
                    enrollMsg.style.border = '1px solid #ef4444';
                }

                enrollMsg.style.display = 'block';

                if (resData.status === 'success') {
                    enrollmentForm.reset();
                    fetchProgress();
                }
                setTimeout(() => { enrollMsg.style.display = 'none'; }, 4000);
            } catch (error) {
                console.error('Enrollment failed:', error);
            }
        });
    }

    const refreshProgressBtn = document.getElementById('refreshProgressBtn');
    if (refreshProgressBtn) refreshProgressBtn.addEventListener('click', fetchProgress);

    async function fetchProgress() {
        try {
            if (refreshProgressBtn) refreshProgressBtn.classList.add('spinning');
            const response = await fetch('/api/students/progress?' + new Date().getTime());
            const data = await response.json();

            if (data.status === 'success') {
                renderProgress(data.data);
            }
        } catch (error) {
            console.error('Failed to fetch progress:', error);
        } finally {
            if (refreshProgressBtn) setTimeout(() => refreshProgressBtn.classList.remove('spinning'), 500);
        }
    }

    function renderProgress(progressList) {
        const tbody = document.getElementById('progressTableBody');
        if (!tbody) return;
        tbody.innerHTML = '';

        progressList.forEach((log, index) => {
            const tr = document.createElement('tr');
            tr.style.animationDelay = `${index * 0.05}s`;

            let gradeBadge = '';
            if (log.grade === 'A') gradeBadge = `<span class="badge badge-success">A</span>`;
            else if (log.grade === 'B') gradeBadge = `<span class="badge badge-info">B</span>`;
            else if (log.grade === 'C') gradeBadge = `<span class="badge" style="background:#f59e0b; color:#fff">C</span>`;
            else gradeBadge = `<span class="badge" style="background:var(--danger-color); color:#fff">F</span>`;

            tr.innerHTML = `
                <td><strong>${log.name}</strong></td>
                <td>${log.roll_no}</td>
                <td><span class="text-secondary">${log.attendance_percentage}%</span></td>
                <td>${gradeBadge}</td>
                <td><span class="text-secondary">${log.workflow_status}</span></td>
                <td><button class="btn btn-icon edit-student-btn" data-name="${log.name}">✏️ Edit</button></td>
            `;
            tbody.appendChild(tr);
        });

        // Add event listeners to all edit buttons
        document.querySelectorAll('.edit-student-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const studentName = btn.getAttribute('data-name');
                openEditPanel(studentName);
            });
        });


        if (progressList.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: #a0aec0;">No students enrolled yet.</td></tr>`;
        }
    }

    // --- SETTINGS LOGIC ---
    const settingsForm = document.getElementById('settingsForm');
    const settingsMsg = document.getElementById('settingsMsg');

    async function loadSettings() {
        try {
            const response = await fetch('/api/settings?' + new Date().getTime());
            const result = await response.json();
            if (result.status === 'success') {
                const data = result.data;
                document.getElementById('setAdminName').value = data.profile.admin_name || '';
                document.getElementById('setAdminEmail').value = data.profile.admin_email || '';

                document.getElementById('setAlertEmail').checked = data.notifications.email_alerts || false;
                document.getElementById('setAlertSMS').checked = data.notifications.sms_alerts || false;
                document.getElementById('setWeeklyReport').checked = data.notifications.weekly_reports || false;
                document.getElementById('setAlertAudio').checked = typeof data.notifications.audio_alerts !== 'undefined' ? data.notifications.audio_alerts : true;

                audioAlertsEnabled = data.notifications.audio_alerts !== false;

                document.getElementById('setTotalClasses').value = data.system.total_classes || 30;
                document.getElementById('setAutoLogout').value = data.system.auto_logout_mins || 15;

                if (data.firebase) {
                    document.getElementById('setFirebaseEnabled').checked = data.firebase.enabled || false;
                    document.getElementById('setFirebaseUrl').value = data.firebase.database_url || '';
                    document.getElementById('setFirebasePath').value = data.firebase.service_account_path || 'serviceAccountKey.json';
                }
            }
        } catch (error) {
            console.error('Failed to load settings:', error);
        }
    }

    if (settingsForm) {
        settingsForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                profile: {
                    admin_name: document.getElementById('setAdminName').value,
                    admin_email: document.getElementById('setAdminEmail').value
                },
                notifications: {
                    email_alerts: document.getElementById('setAlertEmail').checked,
                    sms_alerts: document.getElementById('setAlertSMS').checked,
                    weekly_reports: document.getElementById('setWeeklyReport').checked,
                    audio_alerts: document.getElementById('setAlertAudio').checked
                },
                system: {
                    total_classes: parseInt(document.getElementById('setTotalClasses').value) || 30,
                    auto_logout_mins: parseInt(document.getElementById('setAutoLogout').value) || 15
                },
                firebase: {
                    enabled: document.getElementById('setFirebaseEnabled').checked,
                    database_url: document.getElementById('setFirebaseUrl').value,
                    service_account_path: document.getElementById('setFirebasePath').value
                }
            };

            try {
                const response = await fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const resData = await response.json();

                settingsMsg.innerText = resData.message;
                settingsMsg.className = 'feedback-msg success';
                settingsMsg.style.display = 'block';

                setTimeout(() => { settingsMsg.style.display = 'none'; }, 3000);
            } catch (error) {
                console.error('Failed to save settings:', error);
            }
        });
    }

    // --- EDIT STUDENT LOGIC ---
    const editStudentPanel = document.getElementById('editStudentPanel');
    const editForm = document.getElementById('editForm');
    const cancelEditBtn = document.getElementById('cancelEditBtn');
    const editMsg = document.getElementById('editMsg');

    async function openEditPanel(name) {
        try {
            const response = await fetch(`/api/students/get?name=${encodeURIComponent(name)}`);
            const result = await response.json();

            if (result.status === 'success') {
                const s = result.data;
                document.getElementById('editOriginalName').value = s.name;
                document.getElementById('editName').value = s.name;
                document.getElementById('editRoll').value = s.roll_no;
                document.getElementById('editDept').value = s.dept;
                document.getElementById('editAge').value = s.age;
                document.getElementById('editEmail').value = s.email;

                editStudentPanel.style.display = 'block';
                // Scroll to panel
                editStudentPanel.scrollIntoView({ behavior: 'smooth' });
            }
        } catch (error) {
            console.error('Failed to fetch student details:', error);
        }
    }

    if (cancelEditBtn) {
        cancelEditBtn.addEventListener('click', () => {
            editStudentPanel.style.display = 'none';
        });
    }

    if (editForm) {
        editForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                original_name: document.getElementById('editOriginalName').value,
                new_name: document.getElementById('editName').value,
                roll_no: document.getElementById('editRoll').value,
                dept: document.getElementById('editDept').value,
                age: document.getElementById('editAge').value,
                email: document.getElementById('editEmail').value
            };

            try {
                const response = await fetch('/api/students/edit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const resData = await response.json();

                editMsg.innerText = resData.message;
                editMsg.className = `feedback-msg ${resData.status === 'success' ? 'success' : 'error'}`;
                editMsg.style.display = 'block';

                if (resData.status === 'success') {
                    setTimeout(() => {
                        editStudentPanel.style.display = 'none';
                        fetchProgress();
                    }, 1500);
                }
            } catch (error) {
                console.error('Failed to save student edits:', error);
            }
        });
    }

});
