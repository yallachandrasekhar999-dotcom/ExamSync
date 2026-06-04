with open('subject_details.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add Course Outcomes section after the Roadmap section
old_section = '''        <div class="section-card">
            <div class="section-header">
                <span style="font-size: 24px;">🛣️</span>
                <h2>Course Roadmap</h2>
            </div>
            <div id="roadmapContent" class="roadmap-container">
                <p style="color: var(--text-light);">Loading roadmap items...</p>
            </div>
        </div>

        <div class="section-card">
            <div class="section-header">
                <span style="font-size: 24px;">📄</span>
                <h2>Previous Year Questions</h2>
            </div>'''

new_section = '''        <div class="section-card">
            <div class="section-header">
                <span style="font-size: 24px;">🛣️</span>
                <h2>Course Roadmap</h2>
            </div>
            <div id="roadmapContent" class="roadmap-container">
                <p style="color: var(--text-light);">Loading roadmap items...</p>
            </div>
        </div>

        <div class="section-card">
            <div class="section-header">
                <span style="font-size: 24px;">🎯</span>
                <h2>Course Outcomes</h2>
            </div>
            <div id="coContent">
                <p style="color: var(--text-light);">Loading course outcomes...</p>
            </div>
        </div>

        <div class="section-card">
            <div class="section-header">
                <span style="font-size: 24px;">📄</span>
                <h2>Previous Year Questions</h2>
            </div>'''

content = content.replace(old_section, new_section)

with open('subject_details.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Course Outcomes section added successfully')
