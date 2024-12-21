let questions = [];
let currentQuestionIndex = 0;
let selectedAnswer = null;
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
    fetch(`/get_questions?question_number=${questionNumber}`)
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                questions = data; // Now the data is a list
                showQuestion(0);
                questionNumberInput.value = questionNumber;
                updateProgressBar();
            } else {
                // Handle case where no question is found for the given number
                questionNumberElement.innerText = `Question: N/A`;
                questionTextElement.innerText = "No question found for this number.";
                optionButtonA.innerText = "";
                optionButtonB.innerText = "";
                optionButtonC.innerText = "";
                optionButtonD.innerText = "";
                optionButtonE.innerText = "";
                answerText.innerText = "";
            }
        })
        .catch(error => console.error('Error fetching questions:', error));
}

function showQuestion(index) {
    if (index < questions.length) {
        const currentQuestion = questions[index];
        questionNumberElement.innerText = `Question: ${currentQuestion.question_id}`;
        questionTextElement.innerText = currentQuestion.question_text;
        optionButtonA.innerText = "A : " + (currentQuestion.option_a ? currentQuestion.option_a : "");
        optionButtonB.innerText = "B : " + (currentQuestion.option_b ? currentQuestion.option_b : "");
        optionButtonC.innerText = "C : " + (currentQuestion.option_c ? currentQuestion.option_c : "");
        optionButtonD.innerText = "D : " + (currentQuestion.option_d ? currentQuestion.option_d : "");
        optionButtonE.innerText = "E : " + (currentQuestion.option_e ? currentQuestion.option_e : "");
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
    if (questions.length > 0) {
        const currentQuestion = questions[0]; // Since get_questions returns a list with one question
        fetch('/update_question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question_id: currentQuestion.question_id,
                correct_answer: selectedAnswer,
                flagged: true
            }),
        })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                loadQuestions(parseInt(currentQuestion.question_id) + 1);
            })
            .catch(error => console.error('Error updating question:', error));
    }
}

function nextQuestion() {
    if (questions.length > 0) {
        const currentQuestion = questions[0]; // Since get_questions returns a list with one question
        if (selectedAnswer) {
            fetch('/update_question', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question_id: currentQuestion.question_id,
                    correct_answer: selectedAnswer,
                    flagged: false
                }),
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data.message);
                    loadQuestions(parseInt(currentQuestion.question_id) + 1);
                })
                .catch(error => console.error('Error updating question:', error));
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

// Update Progress Bar (Needs Adjustment if loading single questions)
function updateProgressBar() {
    // This function needs to be adjusted based on how you want to track progress
    // If you load one question at a time, the concept of total questions needs to be handled differently
    // For now, it will just show 100% when a question is loaded.
    const progressBar = document.querySelector('.progress-bar');
    progressBar.style.width = "100%";
}

window.onload = function () {
    questionNumberInput.focus();
    loadQuestions(1);
};