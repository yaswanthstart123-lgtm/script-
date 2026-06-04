document.addEventListener('DOMContentLoaded', async () => {
    if (!ApiClient.getToken()) {
        window.location.href = 'index.html';
        return;
    }

    await loadUserProfile();
    await loadStudentDetails();
    await loadQuizzes();
    await loadResults();

    // Student profile form submission
    document.getElementById('profile-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            name: document.getElementById('prof-name').value,
            department: document.getElementById('prof-dept').value,
            section: document.getElementById('prof-sec').value
        };
        const msgDiv = document.getElementById('profile-msg');
        msgDiv.className = 'msg';
        msgDiv.innerText = 'Saving...';

        try {
            // Determine if create or update by checking if we had data
            let hasDetails = !document.getElementById('profile-display').classList.contains('hidden');
            let res;
            if (hasDetails) {
                res = await ApiClient.put('/students/me', data);
            } else {
                res = await ApiClient.post('/students/details', data);
            }
            msgDiv.innerText = 'Profile saved successfully!';
            msgDiv.classList.add('success-msg');
            
            // Update display
            document.getElementById('disp-name').innerText = res.name;
            document.getElementById('disp-dept').innerText = res.department;
            document.getElementById('disp-sec').innerText = res.section;
            document.getElementById('profile-display').classList.remove('hidden');
            document.getElementById('profile-form').style.display = 'none';

            setTimeout(() => { msgDiv.innerText = ''; }, 3000);
        } catch (err) {
            msgDiv.innerText = err.message;
            msgDiv.classList.add('error-msg');
        }
    });
});

async function loadUserProfile() {
    try {
        const user = await ApiClient.get('/auth/me');
        document.getElementById('user-display').innerText = `Welcome, ${user.email}`;
    } catch (err) {
        console.error("Failed to load user profile", err);
    }
}

async function loadStudentDetails() {
    try {
        const details = await ApiClient.get('/students/me');
        const display = document.getElementById('profile-display');
        const form = document.getElementById('profile-form');
        
        document.getElementById('disp-name').innerText = details.name;
        document.getElementById('disp-dept').innerText = details.department;
        document.getElementById('disp-sec').innerText = details.section;

        // Pre-fill form
        document.getElementById('prof-name').value = details.name;
        document.getElementById('prof-dept').value = details.department;
        document.getElementById('prof-sec').value = details.section;

        display.classList.remove('hidden');
        form.style.display = 'none';
    } catch (err) {
        if (err.message.includes('404')) {
            // No details yet, show form
            document.getElementById('profile-display').classList.add('hidden');
            document.getElementById('profile-form').style.display = 'block';
        }
    }
}

function editProfile() {
    document.getElementById('profile-display').classList.add('hidden');
    const form = document.getElementById('profile-form');
    form.style.display = 'block';
    document.getElementById('profile-cancel-btn').classList.remove('hidden');
}

function cancelEdit() {
    document.getElementById('profile-display').classList.remove('hidden');
    document.getElementById('profile-form').style.display = 'none';
}

async function loadQuizzes() {
    const container = document.getElementById('quizzes-container');
    try {
        const quizzes = await ApiClient.get('/quiz/list');
        if (quizzes.length === 0) {
            container.innerHTML = '<p class="empty-state">No active quizzes available.</p>';
            return;
        }
        
        container.innerHTML = quizzes.map(q => `
            <div class="card glass-card">
                <h3>${q.title}</h3>
                <p>${q.description || 'Test your knowledge.'}</p>
                <div class="card-meta">
                    <span>${q.question_count} Questions</span>
                </div>
                <a href="quiz.html?id=${q.id}" class="btn primary-btn small mt-1">Take Quiz</a>
            </div>
        `).join('');
    } catch (err) {
        container.innerHTML = `<p class="error-msg">Failed to load quizzes: ${err.message}</p>`;
    }
}

async function loadResults() {
    const container = document.getElementById('results-container');
    try {
        const data = await ApiClient.get('/quiz/results');
        const results = data.results || [];
        if (results.length === 0) {
            container.innerHTML = '<p class="empty-state">You have not taken any quizzes yet.</p>';
            return;
        }
        
        container.innerHTML = results.map(r => `
            <div class="card glass-card">
                <h3>${r.quiz_title}</h3>
                <div class="score-pill">
                    <span class="score">${r.score}/${r.total_questions}</span>
                    <span class="percentage">(${r.percentage}%)</span>
                </div>
                <p class="mt-1">Date: ${new Date(r.created_at).toLocaleDateString()}</p>
            </div>
        `).join('');
    } catch (err) {
        container.innerHTML = `<p class="error-msg">Failed to load results: ${err.message}</p>`;
    }
}
