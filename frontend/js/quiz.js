let currentQuizId = null;
let timerInterval = null;
let secondsActive = 0;

document.addEventListener('DOMContentLoaded', async () => {
    if (!ApiClient.getToken()) {
        window.location.href = 'index.html';
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    currentQuizId = urlParams.get('id');

    if (!currentQuizId) {
        document.getElementById('quiz-load-error').innerText = 'No quiz specified.';
        document.getElementById('quiz-title').innerText = 'Error';
        return;
    }

    await loadQuizDetails();

    document.getElementById('quiz-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Collect answers
        const formData = new FormData(e.target);
        const answers = [];
        
        // Group by question ID 
        // e.g. name="q_5" value="[option_id]"
        for (let [name, value] of formData.entries()) {
            if (name.startsWith('q_')) {
                const questionId = parseInt(name.split('_')[1]);
                answers.push({
                    question_id: questionId,
                    selected_option_id: parseInt(value)
                });
            }
        }

        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-msg mt-1';
        
        try {
            clearInterval(timerInterval);
            const submitBtn = e.target.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerText = 'Submitting...';
            
            const result = await ApiClient.post('/quiz/submit', {
                quiz_id: parseInt(currentQuizId),
                answers: answers
            });
            
            showResult(result);
        } catch (err) {
            errorDiv.innerText = err.message;
            e.target.appendChild(errorDiv);
            document.querySelector('button[type="submit"]').disabled = false;
        }
    });
});

async function loadQuizDetails() {
    try {
        const quiz = await ApiClient.get(`/quiz/${currentQuizId}/questions`);
        
        document.getElementById('quiz-title').innerText = quiz.title;
        document.getElementById('quiz-desc').innerText = quiz.description || '';
        document.getElementById('start-btn').classList.remove('hidden');
        
        // Pre-build questions UI
        const container = document.getElementById('questions-container');
        container.innerHTML = quiz.questions.map((q, index) => `
            <div class="question-card glass-card">
                <h4><span class="q-num">Q${index + 1}</span> ${q.text}</h4>
                <div class="options">
                    ${q.options.map(opt => `
                        <label class="option-label">
                            <input type="radio" name="q_${q.id}" value="${opt.id}" required>
                            <span class="opt-text">${opt.text}</span>
                        </label>
                    `).join('')}
                </div>
            </div>
        `).join('');
        
    } catch (err) {
        document.getElementById('quiz-load-error').innerText = `Failed to load quiz: ${err.message}`;
        document.getElementById('quiz-title').innerText = 'Quiz Unavailable';
    }
}

window.startQuiz = function() {
    document.getElementById('quiz-intro').classList.add('hidden');
    document.getElementById('quiz-active').classList.remove('hidden');
    
    // Start timer
    timerInterval = setInterval(() => {
        secondsActive++;
        const mins = String(Math.floor(secondsActive / 60)).padStart(2, '0');
        const secs = String(secondsActive % 60).padStart(2, '0');
        document.getElementById('timer-display').innerText = `${mins}:${secs}`;
    }, 1000);
}

function showResult(result) {
    document.getElementById('quiz-active').classList.add('hidden');
    document.getElementById('quiz-header-info').classList.add('hidden');
    document.getElementById('quiz-result').classList.remove('hidden');
    
    document.getElementById('result-score').innerText = `${result.score}/${result.total_questions}`;
    document.getElementById('result-percentage').innerText = `${result.percentage}%`;
    
    const grade = document.getElementById('result-grade');
    if (result.percentage >= 80) {
        grade.innerText = 'Excellent!';
        grade.style.color = '#10b981';
    } else if (result.percentage >= 50) {
        grade.innerText = 'Good job!';
        grade.style.color = '#3b82f6';
    } else {
        grade.innerText = 'Keep practicing.';
        grade.style.color = '#ef4444';
    }
}
