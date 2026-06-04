const defaultData = {
    users: [
        {
            id: "u1",
            username: "student",
            password: "123",
            role: "student",
            name: "Alex Student"
        },
        {
            id: "u2",
            username: "admin",
            password: "123",
            role: "admin",
            name: "Super Admin"
        },
        {
            id: "u3",
            username: "author",
            password: "123",
            role: "author",
            name: "Dr. Smith",
            assignedSubjects: ["s1", "s2"] // Linked to Subject IDs
        }
    ],

    // Curriculum Hierarchy: Year -> Semester -> Subjects
    curriculum: [
        {
            id: "y1",
            year: "First Year",
            semesters: [
                {
                    id: "sem1",
                    name: "Semester 1",
                    subjects: [
                        { id: "s1", name: "Engineering Mathematics I", code: "MAT101" },
                        { id: "s2", name: "Engineering Physics", code: "PHY101" }
                    ]
                },
                {
                    id: "sem2",
                    name: "Semester 2",
                    subjects: [
                        { id: "s3", name: "Engineering Mathematics II", code: "MAT102" },
                        { id: "s4", name: "Basic Electronics", code: "ECE101" }
                    ]
                }
            ]
        },
        {
            id: "y2",
            year: "Second Year",
            semesters: [
                {
                    id: "sem3",
                    name: "Semester 3",
                    subjects: [
                        { id: "s5", name: "Data Structures", code: "CS201" },
                        { id: "s6", name: "Digital Logic", code: "CS202" }
                    ]
                }
            ]
        }
    ],

    // Content linked by Subject ID
    content: {
        "s1": {
            courseOutcomes: [
                "CO1: Understand calculus basics.",
                "CO2: Apply differential equations."
            ],
            pyqs: [
                { title: "2023 End Sem", link: "#" },
                { title: "2022 End Sem", link: "#" }
            ],
            importantQuestions: [
                { question: "Explain Leibnitz theorem.", marks: 5 },
                { question: "Solve the differential equation...", marks: 10 }
            ],
            roadmap: [
                { step: 1, title: "Limits & Continuity", description: "Understand the behavior of functions." },
                { step: 2, title: "Derivatives", description: "Learn rules of differentiation." },
                { step: 3, title: "Integrals", description: "Master definite and indefinite integrals." },
                { step: 4, title: "Differential Equations", description: "Solve first and second order DEs." }
            ]
        },
        "s5": {
            courseOutcomes: [
                "CO1: Analyze algorithms.",
                "CO2: Implement linked lists and trees."
            ],
            pyqs: [
                { title: "2024 Mid Sem", link: "#" }
            ],
            importantQuestions: [
                { question: "Difference between BFS and DFS?", marks: 5 },
                { question: "Explain QuickSort algorithm.", marks: 10 }
            ],
            roadmap: [
                { step: 1, title: "Arrays & Strings", description: "Basic manipulation and memory layout." },
                { step: 2, title: "Linked Lists", description: "Singly, Doubly, and Circular lists." },
                { step: 3, title: "Stacks & Queues", description: "LIFO and FIFO principles." },
                { step: 4, title: "Trees & Graphs", description: "Hierarchical data structures and traversals." },
                { step: 5, title: "Sorting & Searching", description: "Efficient algorithms for data retrieval." }
            ]
        }
    }
};

// Initialize from LocalStorage or use Default
const storedData = localStorage.getItem('examSyncData');
export const mockData = storedData ? JSON.parse(storedData) : defaultData;

// Function to save changes
export function saveMockData() {
    localStorage.setItem('examSyncData', JSON.stringify(mockData));
}
