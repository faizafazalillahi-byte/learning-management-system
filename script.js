// Sample Data
const coursesData = [
    {
        id: 1,
        title: "Python Fundamentals",
        category: "python",
        level: "beginner",
        description: "Learn Python basics from scratch",
        icon: "🐍",
        rating: 4.8,
        students: 15420,
        duration: "40 hours",
        progress: 65
    },
    {
        id: 2,
        title: "Machine Learning Basics",
        category: "ai",
        level: "intermediate",
        description: "Introduction to ML concepts and algorithms",
        icon: "🤖",
        rating: 4.9,
        students: 12300,
        duration: "60 hours",
        progress: 45
    },
    {
        id: 3,
        title: "Web Development with React",
        category: "web",
        level: "intermediate",
        description: "Build modern web applications with React",
        icon: "⚛️",
        rating: 4.7,
        students: 18900,
        duration: "50 hours",
        progress: 80
    },
    {
        id: 4,
        title: "Data Science Masterclass",
        category: "data",
        level: "advanced",
        description: "Advanced data analysis and visualization",
        icon: "📊",
        rating: 4.9,
        students: 8700,
        duration: "80 hours",
        progress: 30
    },
    {
        id: 5,
        title: "JavaScript Essentials",
        category: "web",
        level: "beginner",
        description: "Master JavaScript fundamentals",
        icon: "✨",
        rating: 4.8,
        students: 21000,
        duration: "35 hours",
        progress: 90
    },
    {
        id: 6,
        title: "Deep Learning with TensorFlow",
        category: "ai",
        level: "advanced",
        description: "Build neural networks with TensorFlow",
        icon: "🧠",
        rating: 4.6,
        students: 5600,
        duration: "90 hours",
        progress: 20
    }
];

const skillsAcquired = [
    "Python Programming",
    "Machine Learning",
    "Data Analysis",
    "Web Development",
    "React.js",
    "JavaScript",
    "SQL",
    "Data Visualization",
    "APIs",
    "Cloud Computing"
];

const aiResponses = [
    {
        keywords: ["machine learning", "ml", "learn"],
        response: "Machine Learning is a subset of artificial intelligence that enables systems to learn from data. There are three main types: supervised learning, unsupervised learning, and reinforcement learning. Would you like me to explain any of these in detail?"
    },
    {
        keywords: ["python", "coding"],
        response: "Python is a versatile and beginner-friendly programming language. It's widely used in data science, web development, and automation. Key concepts include variables, functions, loops, and object-oriented programming. What aspect of Python would you like to learn?"
    },
    {
        keywords: ["web", "web development", "react", "javascript"],
        response: "Web development involves creating websites and web applications. Key technologies include HTML for structure, CSS for styling, and JavaScript for interactivity. Modern frameworks like React make it easier to build complex applications. Interested in any specific technology?"
    },
    {
        keywords: ["data", "analysis", "visualization"],
        response: "Data science involves extracting insights from data. Key steps include data collection, cleaning, analysis, and visualization. Popular libraries include Pandas, NumPy, and Matplotlib. What data science topic interests you?"
    },
    {
        keywords: ["help", "how", "what", "why"],
        response: "I'm here to help! I can assist you with learning various programming and tech topics. You can ask me about specific concepts, best practices, or general guidance. What would you like to learn about?"
    }
];

// DOM Elements
const navLinks = document.querySelectorAll('.nav-link');
const sections = document.querySelectorAll('.section');
const coursesGrid = document.getElementById('coursesGrid');
const searchCourses = document.getElementById('searchCourses');
const categoryFilter = document.getElementById('categoryFilter');
const levelFilter = document.getElementById('levelFilter');
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const quickBtns = document.querySelectorAll('.quick-btn');
const modal = document.getElementById('courseModal');
const closeBtn = document.querySelector('.close');
const recentCourses = document.getElementById('recentCourses');
const recommendations = document.getElementById('recommendations');
const courseProgress = document.getElementById('courseProgress');
const skillsTags = document.getElementById('skillsTags');
const profileForm = document.getElementById('profileForm');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    displayCourses(coursesData);
    displayRecentCourses();
    displayRecommendations();
    displayCourseProgress();
    displaySkills();
    setupChartData();
    setupEventListeners();
});

// Navigation
function initNavigation() {
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            showSection(targetId);
            
            // Update active link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
}

function showSection(sectionId) {
    sections.forEach(section => section.classList.remove('active'));
    document.getElementById(sectionId).classList.add('active');
    window.scrollTo(0, 0);
}

// Display Courses
function displayCourses(courses) {
    coursesGrid.innerHTML = '';
    courses.forEach(course => {
        const courseCard = document.createElement('div');
        courseCard.className = 'course-card';
        courseCard.innerHTML = `
            <div class="course-image">${course.icon}</div>
            <div class="course-info">
                <span class="course-category">${course.category}</span>
                <h3>${course.title}</h3>
                <p class="course-description">${course.description}</p>
                <div class="course-meta">
                    <span>⭐ ${course.rating}</span>
                    <span>${course.students.toLocaleString()} students</span>
                    <span class="course-level">${course.level}</span>
                </div>
                <button class="btn-primary" onclick="showCourseDetail(${course.id})">Enroll Now</button>
            </div>
        `;
        coursesGrid.appendChild(courseCard);
    });
}

// Filter Courses
searchCourses.addEventListener('input', filterCourses);
categoryFilter.addEventListener('change', filterCourses);
levelFilter.addEventListener('change', filterCourses);

function filterCourses() {
    const searchTerm = searchCourses.value.toLowerCase();
    const category = categoryFilter.value;
    const level = levelFilter.value;

    const filteredCourses = coursesData.filter(course => {
        const matchesSearch = course.title.toLowerCase().includes(searchTerm) ||
                            course.description.toLowerCase().includes(searchTerm);
        const matchesCategory = !category || course.category === category;
        const matchesLevel = !level || course.level === level;
        
        return matchesSearch && matchesCategory && matchesLevel;
    });

    displayCourses(filteredCourses);
}

// Show Course Detail
function showCourseDetail(courseId) {
    const course = coursesData.find(c => c.id === courseId);
    const courseDetails = document.getElementById('courseDetails');
    
    courseDetails.innerHTML = `
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">${course.icon}</div>
            <h2>${course.title}</h2>
            <p style="color: #64748b; margin: 1rem 0;">${course.description}</p>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 2rem;">
            <div>
                <p><strong>Level:</strong> ${course.level}</p>
                <p><strong>Duration:</strong> ${course.duration}</p>
                <p><strong>Students:</strong> ${course.students.toLocaleString()}</p>
            </div>
            <div>
                <p><strong>Rating:</strong> ⭐ ${course.rating}</p>
                <p><strong>Category:</strong> ${course.category}</p>
                <p><strong>Your Progress:</strong> ${course.progress}%</p>
            </div>
        </div>
        <div style="margin-bottom: 2rem;">
            <h3>Course Overview</h3>
            <p>This comprehensive course covers all essential topics you need to master ${course.title.toLowerCase()}. 
            Learn from industry experts and practice with real-world projects. Upon completion, you'll receive a certificate 
            and be ready for professional roles in this field.</p>
        </div>
        <button class="btn-primary" style="margin-bottom: 1rem;">Enroll Now</button>
        <button class="btn-secondary" onclick="closeModal()">Close</button>
    `;
    
    modal.classList.add('show');
}

function closeModal() {
    modal.classList.remove('show');
}

closeBtn.addEventListener('click', closeModal);
window.addEventListener('click', (event) => {
    if (event.target === modal) {
        closeModal();
    }
});

// Display Recent Courses
function displayRecentCourses() {
    const recent = coursesData.slice(0, 3);
    recentCourses.innerHTML = '';
    
    recent.forEach(course => {
        const courseItem = document.createElement('div');
        courseItem.className = 'course-item';
        courseItem.innerHTML = `
            <h3>${course.icon} ${course.title}</h3>
            <p>${course.description}</p>
            <div class="course-progress-bar">
                <div class="progress-fill" style="width: ${course.progress}%"></div>
            </div>
            <p style="margin-top: 0.5rem; font-size: 0.9rem; color: #64748b;">${course.progress}% Complete</p>
        `;
        recentCourses.appendChild(courseItem);
    });
}

// Display Recommendations
function displayRecommendations() {
    const recommendedCourses = coursesData.filter(c => c.level === 'intermediate').slice(0, 3);
    recommendations.innerHTML = '';
    
    recommendedCourses.forEach(course => {
        const recItem = document.createElement('div');
        recItem.className = 'recommendation-item';
        recItem.innerHTML = `
            <h3>${course.icon} ${course.title}</h3>
            <p style="font-size: 0.9rem; color: #64748b;">${course.description}</p>
            <p style="margin-top: 0.5rem; font-size: 0.85rem; color: #6366f1; font-weight: 600;">
                ⭐ Recommended for you
            </p>
        `;
        recommendations.appendChild(recItem);
    });
}

// Display Course Progress
function displayCourseProgress() {
    courseProgress.innerHTML = '';
    
    coursesData.forEach(course => {
        const progressItem = document.createElement('div');
        progressItem.className = 'progress-item';
        progressItem.innerHTML = `
            <div class="progress-item-name">
                <h4>${course.title}</h4>
                <p>${course.duration}</p>
            </div>
            <div class="progress-item-bar">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${course.progress}%"></div>
                </div>
            </div>
            <div class="progress-value">${course.progress}%</div>
        `;
        courseProgress.appendChild(progressItem);
    });
}

// Display Skills
function displaySkills() {
    skillsTags.innerHTML = '';
    
    skillsAcquired.forEach(skill => {
        const skillTag = document.createElement('span');
        skillTag.className = 'skill-tag';
        skillTag.textContent = skill;
        skillsTags.appendChild(skillTag);
    });
}

// Chat Functionality
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

quickBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const question = btn.getAttribute('data-question');
        userInput.value = question;
        sendMessage();
    });
});

function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message) return;

    // Add user message
    addMessage(message, 'user');
    userInput.value = '';

    // Get AI response
    setTimeout(() => {
        const response = getAIResponse(message);
        addMessage(response, 'bot');
    }, 500);
}

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.innerHTML = `
        <div class="message-content">
            <p>${text}</p>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function getAIResponse(userMessage) {
    const userMsg = userMessage.toLowerCase();
    
    for (let responseObj of aiResponses) {
        for (let keyword of responseObj.keywords) {
            if (userMsg.includes(keyword)) {
                return responseObj.response;
            }
        }
    }

    // Default response
    return "That's an interesting question! I'm here to help you learn. Could you provide more details about what you'd like to know? Try asking about specific topics like Python, Machine Learning, Web Development, or Data Science.";
}

// Setup Chart Data
function setupChartData() {
    const ctx = document.getElementById('progressChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Learning Hours',
                    data: [3, 4, 2, 5, 4.5, 3, 3.5],
                    backgroundColor: [
                        '#6366f1',
                        '#6366f1',
                        '#6366f1',
                        '#ec4899',
                        '#6366f1',
                        '#6366f1',
                        '#6366f1'
                    ],
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 6
                    }
                }
            }
        });
    }
}

// Setup Event Listeners
function setupEventListeners() {
    profileForm.addEventListener('submit', (e) => {
        e.preventDefault();
        alert('Profile updated successfully!');
    });
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        if (this.getAttribute('href') !== '#') {
            e.preventDefault();
        }
    });
});

