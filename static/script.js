let questions = [];
let currentQuestionIndex = 0;
let selectedAnswer = null;
let csvFileName = 'mcq_csv_final.csv'; //set your csv file name here.
let questionNumberElement = document.getElementById("question-number");
let questionTextElement = document.getElementById("question-text");
let optionButtonA = document.getElementById("optionA");
let optionButtonB = document.getElementById("optionB");
let optionButtonC = document.getElementById("optionC");
let optionButtonD = document.getElementById("optionD");
let optionButtonE = document.getElementById("optionE");
let answerText = document.getElementById("answer-text");
let questionNumberInput = document.getElementById("question-number-input");

// Load Questions
function loadQuestions(questionNumber = 1) {
    fetch('get_questions?csv_file=' + csvFileName + '&question_number=' + questionNumber)
        .then(response => response.json())
        .then(data => {
            questions = data;
            showQuestion(0);
            questionNumberInput.value = questionNumber;
            updateProgressBar();
        })
        .catch(error => console.error('Error fetching questions:', error));
}

function showQuestion(index) {
    if (index < questions.length) {
        const currentQuestion = questions[index];
        questionNumberElement.innerText = `Question: ${currentQuestion.question_id}`;
        questionTextElement.innerText = currentQuestion.question;
        optionButtonA.innerText = "A : " + (currentQuestion.options[0] ? currentQuestion.options[0] : "");
        optionButtonB.innerText = "B : " + (currentQuestion.options[1] ? currentQuestion.options[1] : "");
        optionButtonC.innerText = "C : " + (currentQuestion.options[2] ? currentQuestion.options[2] : "");
        optionButtonD.innerText = "D : " + (currentQuestion.options[3] ? currentQuestion.options[3] : "");
        optionButtonE.innerText = "E : " + (currentQuestion.options[4] ? currentQuestion.options[4] : "");
        selectedAnswer = null;
        answerText.innerText = "Not Answered";
    } else {
        questionNumberElement.innerText = `No More Questions`;
        questionTextElement.innerText = "You have finished adding answers for all questions.";
    }
}

function selectAnswer(option) {
    selectedAnswer = option;
    answerText.innerText = "Your answer is: " + option;
}

function flagQuestion() {
    if (currentQuestionIndex < questions.length) {
        const currentQuestion = questions[currentQuestionIndex];
        fetch('update_question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question_id: currentQuestion.question_id,
                correct_answer: selectedAnswer,
                flagged: true,
                csv_file: csvFileName
            }),
        })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                loadQuestions(parseInt(currentQuestion.question_id) + 1);
            })
            .catch(error => console.error('Error updating CSV:', error));
    }
}

function nextQuestion() {
    if (currentQuestionIndex < questions.length) {
        const currentQuestion = questions[currentQuestionIndex];
        if (selectedAnswer) {
            fetch('update_question', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question_id: currentQuestion.question_id,
                    correct_answer: selectedAnswer,
                    flagged: false,
                    csv_file: csvFileName
                }),
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data.message);
                    loadQuestions(parseInt(currentQuestion.question_id) + 1);
                })
                .catch(error => console.error('Error updating CSV:', error));
        } else {
            alert("Please select an answer before going to the next question");
        }
    }
}

function goToQuestion() {
    let questionNumber = questionNumberInput.value;
    if (questionNumber) {
        loadQuestions(parseInt(questionNumber));
    } else {
        alert("Please enter the question number");
    }
}

// Dark/Light Mode Toggle
function toggleMode() {
    document.body.classList.toggle('dark-mode');
    document.body.classList.toggle('light-mode');
}

// Update Progress Bar
function updateProgressBar() {
    const progressBar = document.querySelector('.progress-bar');
    if (questions.length > 0) {
        const progress = ((currentQuestionIndex + 1) / questions.length) * 100;
        progressBar.style.width = progress + "%";
    }
}

window.onload = function () {
    questionNumberInput.focus();
    loadQuestions(1);
};
