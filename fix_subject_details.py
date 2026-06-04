import re

with open('subject_details.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the loadContent function to properly fetch data from JSON storage
old_pattern = r'async function loadContent\(\).*?\n        \}\n\n        loadContent\(\);'

new_func = '''async function loadContent() {
            try {
                // Get URL parameters
                const urlParams = new URLSearchParams(window.location.search);
                const subjectId = urlParams.get('id');
                const subjectName = urlParams.get('name') || 'Subject';
                const branch = urlParams.get('branch') || 'CSE';
                const sem = urlParams.get('sem') || '1';

                // Set header
                document.getElementById('subName').textContent = subjectName;
                document.getElementById('subCode').textContent = branch + ' - Sem ' + sem;

                const theme = getSubjectTheme(subjectName);
                const hero = document.querySelector('.subject-hero');
                hero.style.background = theme.gradient;

                // Load content from data files
                await loadRoadmap(subjectId, subjectName);
                await loadPYQs(subjectId, subjectName);
                await loadImportantQuestions(subjectId, subjectName);
                await loadCourseOutcomes(subjectId, subjectName);

            } catch (error) {
                console.error("Failed to load content:", error);
            }
        }

        function getSubjectTheme(name) {
            name = name.toLowerCase();
            if (name.includes('programming') || name.includes('java') || name.includes('python')) {
                return { primary: '#3b82f6', gradient: 'linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%)' };
            }
            if (name.includes('math') || name.includes('algebra')) {
                return { primary: '#8b5cf6', gradient: 'linear-gradient(135deg, #6c63ff 0%, #8b5cf6 100%)' };
            }
            if (name.includes('physics') || name.includes('chemistry')) {
                return { primary: '#06b6d4', gradient: 'linear-gradient(135deg, #0891b2 0%, #06b6d4 100%)' };
            }
            if (name.includes('network') || name.includes('security')) {
                return { primary: '#10b981', gradient: 'linear-gradient(135deg, #059669 0%, #10b981 100%)' };
            }
            return { primary: '#6366f1', gradient: 'linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)' };
        }

        async function loadRoadmap(subjectId, subjectName) {
            const roadmapDiv = document.getElementById('roadmapContent');
            roadmapDiv.innerHTML = '<p style="color: var(--text-light);">Loading roadmap...</p>';
            
            try {
                const response = await fetch('./data/roadmap_steps.json');
                const steps = await response.json();
                const subjectSteps = steps.filter(s => s.subject_id === subjectId || s.subject_name === subjectName);
                
                if (subjectSteps && subjectSteps.length > 0) {
                    roadmapDiv.innerHTML = subjectSteps
                        .sort((a, b) => (a.step_number || 0) - (b.step_number || 0))
                        .map(step => `
                            <div class="roadmap-step">
                                <h4>Step ${step.step_number || 1}: ${step.title}</h4>
                                <p>${step.description}</p>
                            </div>
                        `).join('');
                } else {
                    roadmapDiv.innerHTML = '<p style="color: var(--text-light);">No roadmap available yet.</p>';
                }
            } catch (e) {
                roadmapDiv.innerHTML = '<p style="color: var(--text-light);">No roadmap available.</p>';
            }
        }

        async function loadPYQs(subjectId, subjectName) {
            const pyqDiv = document.getElementById('pyqContent');
            pyqDiv.innerHTML = '<p style="color: var(--text-light);">Loading PYQs...</p>';
            
            try {
                const response = await fetch('./data/pyqs.json');
                const pyqs = await response.json();
                const subjectPYQs = pyqs.filter(p => p.subject_id === subjectId || p.subject_name === subjectName);
                
                if (subjectPYQs && subjectPYQs.length > 0) {
                    pyqDiv.innerHTML = subjectPYQs.map(p => `
                        <div class="content-item">
                            <span>${p.title} ${p.year ? '(' + p.year + ')' : ''}</span>
                            <a href="${p.link || '#'})" class="download-btn" target="_blank">View</a>
                        </div>
                    `).join('');
                } else {
                    pyqDiv.innerHTML = '<p style="color: var(--text-light);">No previous year questions available yet.</p>';
                }
            } catch (e) {
                pyqDiv.innerHTML = '<p style="color: var(--text-light);">No PYQs available.</p>';
            }
        }

        async function loadImportantQuestions(subjectId, subjectName) {
            const impDiv = document.getElementById('impContent');
            impDiv.innerHTML = '<p style="color: var(--text-light);">Loading important questions...</p>';
            
            try {
                const response = await fetch('./data/important_questions.json');
                const questions = await response.json();
                const subjectQuestions = questions.filter(q => q.subject_id === subjectId || q.subject_name === subjectName);
                
                if (subjectQuestions && subjectQuestions.length > 0) {
                    impDiv.innerHTML = subjectQuestions.map(q => `
                        <div class="content-item">
                            <span style="flex: 1; margin-right: 20px;">${q.question_text}</span>
                            <span class="marks-badge">${q.marks || 5} Marks</span>
                        </div>
                    `).join('');
                } else {
                    impDiv.innerHTML = '<p style="color: var(--text-light);">No important questions listed yet.</p>';
                }
            } catch (e) {
                impDiv.innerHTML = '<p style="color: var(--text-light);">No important questions available.</p>';
            }
        }

        async function loadCourseOutcomes(subjectId, subjectName) {
            // Check if there's a course outcomes section
            let coSection = document.getElementById('coContent');
            if (!coSection) return;
            
            coSection.innerHTML = '<p style="color: var(--text-light);">Loading course outcomes...</p>';
            
            try {
                const response = await fetch('./data/course_outcomes.json');
                const cos = await response.json();
                const subjectCOs = cos.filter(c => c.subject_id === subjectId || c.subject_name === subjectName);
                
                if (subjectCOs && subjectCOs.length > 0) {
                    coSection.innerHTML = subjectCOs.map((c, i) => `
                        <div class="content-item">
                            <span><strong>CO${c.order || i+1}:</strong> ${c.outcome_text}</span>
                        </div>
                    `).join('');
                } else {
                    coSection.innerHTML = '<p style="color: var(--text-light);">No course outcomes listed yet.</p>';
                }
            } catch (e) {
                coSection.innerHTML = '<p style="color: var(--text-light);">No course outcomes available.</p>';
            }
        }

        loadContent();'''

content = re.sub(old_pattern, new_func, content, flags=re.DOTALL)

with open('subject_details.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Subject details page updated successfully')
