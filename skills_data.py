"""
A curated vocabulary of skill phrases used for explainable matching.

This is intentionally a plain Python list rather than a database table —
it's easy to read, easy to extend, and doesn't need a migration to update.
Feel free to add domain-specific terms for your own use case.
"""

SKILLS = [
    # Programming languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "kotlin", "swift", "php", "ruby", "scala", "r", "matlab", "sql",

    # Web / frontend
    "html", "css", "react", "angular", "vue", "next.js", "node.js", "express",
    "redux", "tailwind css", "bootstrap", "jquery", "webpack",

    # Backend / frameworks
    "flask", "django", "spring boot", "fastapi", "graphql", "rest api",
    "microservices", "grpc",

    # Data / ML
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "pandas", "numpy", "scikit-learn", "tensorflow",
    "pytorch", "keras", "data analysis", "data visualization", "tableau",
    "power bi", "spacy", "opencv", "statistics", "a/b testing",

    # Databases
    "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle",
    "elasticsearch", "dynamodb",

    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
    "ci/cd", "git", "github", "gitlab", "linux", "bash", "nginx",

    # Mobile
    "android", "ios", "react native", "flutter",

    # Testing / QA
    "unit testing", "pytest", "junit", "selenium", "test automation",

    # Project management / tools
    "agile", "scrum", "kanban", "jira", "confluence", "product management",

    # Soft skills
    "communication", "leadership", "teamwork", "problem solving",
    "critical thinking", "time management", "collaboration",
    "adaptability", "mentoring", "public speaking",
]
