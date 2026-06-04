import re

with open('student_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace import to remove curriculumAPI
content = content.replace(
    "import { curriculumAPI, contentAPI } from './js/api.js';",
    "// Direct fetch used instead of API"
)

# Find and replace the loadSubjects function with new implementation
old_pattern = r'async function loadSubjects\(\).*?\n        \}\n\n        loadSubjects\(\);'

new_func = '''async function loadSubjects() {
            if (!user) return;
            const grid = document.getElementById('subjectsGrid');
            grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px;">Loading...</div>';
            try {
                const response = await fetch('./data/collegesubjects/subjects.json');
                if (!response.ok) throw new Error('Failed to load subjects');
                const data = await response.json();
                const userBranch = user.branch || 'CSE';
                const userSemester = user.semester || 1;
                const semKey = 'sem' + userSemester;
                const branchData = data.branches?.[userBranch];
                if (!branchData) {
                    grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px;">No curriculum for ' + userBranch + '</div>';
                    return;
                }
                const semData = branchData.semesters?.[semKey];
                if (!semData || !semData.subjects || semData.subjects.length === 0) {
                    grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px;">No subjects for ' + userBranch + ' - Sem ' + userSemester + '</div>';
                    return;
                }
                const subjects = semData.subjects;
                document.getElementById('subCount').textContent = subjects.length + ' Subjects Total';
                grid.innerHTML = '';
                subjects.forEach((subName, index) => {
                    const theme = getSubjectTheme(subName);
                    const card = document.createElement('a');
                    const subjectId = userBranch + '-' + userSemester + '-' + index;
                    card.href = 'subject_details.html?id=' + encodeURIComponent(subjectId) + '&name=' + encodeURIComponent(subName) + '&branch=' + userBranch + '&sem=' + userSemester;
                    card.className = 'subject-card';
                    card.style.borderLeft = '5px solid ' + theme.primary;
                    card.innerHTML = '<div class="sub-icon" style="background: ' + theme.primary + '20; color: ' + theme.primary + ';">📚</div><div style="flex-grow: 1;"><h3 style="color: var(--navy);">' + subName + '</h3><p style="margin-bottom: 10px;">' + userBranch + ' - Sem ' + userSemester + '</p></div><div class="card-footer"><span class="stat-badge" style="background: ' + theme.primary + '15; color: ' + theme.primary + '; border: 1px solid ' + theme.primary + '30;">Curriculum 2024</span><span style="color: ' + theme.primary + '; font-weight: 800;">Study →</span></div>';
                    grid.appendChild(card);
                });
            } catch (error) {
                console.error('Failed to load subjects:', error);
                grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--coral);">Failed to load curriculum.</div>';
            }
        }
        function getSubjectTheme(name) {
            name = name.toLowerCase();
            if (name.includes('programming') || name.includes('java') || name.includes('python')) return { primary: '#3b82f6' };
            if (name.includes('math') || name.includes('algebra')) return { primary: '#8b5cf6' };
            if (name.includes('physics') || name.includes('chemistry')) return { primary: '#06b6d4' };
            if (name.includes('network') || name.includes('security')) return { primary: '#10b981' };
            return { primary: '#6366f1' };
        }

        loadSubjects();'''

content = re.sub(old_pattern, new_func, content, flags=re.DOTALL)

with open('student_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated successfully')
