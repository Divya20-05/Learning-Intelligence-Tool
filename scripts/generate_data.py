"""
Generate realistic synthetic learner data for training and testing
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)

def generate_learner_data(n_students=1000, n_courses=10):
    """
    Generate synthetic learner data with realistic patterns
    
    Patterns implemented:
    - Students with low scores are more likely to drop out
    - Difficult chapters have lower scores and higher time spent
    - Engagement (time spent) correlates with completion
    - Some courses are harder than others
    """
    
    data = []
    student_id = 1
    
    # Define course characteristics
    courses = []
    for course_id in range(1, n_courses + 1):
        n_chapters = np.random.randint(5, 16)  # 5-15 chapters per course
        difficulty = np.random.uniform(0.3, 0.8)  # Course difficulty
        courses.append({
            'course_id': course_id,
            'n_chapters': n_chapters,
            'difficulty': difficulty
        })
    
    for _ in range(n_students):
        # Select a random course
        course = np.random.choice(courses)
        course_id = course['course_id']
        n_chapters = course['n_chapters']
        course_difficulty = course['difficulty']
        
        # Student characteristics
        student_ability = np.random.uniform(0.3, 0.95)  # Student ability level
        student_motivation = np.random.uniform(0.2, 1.0)  # Motivation level
        
        # Determine if student will complete (based on ability and motivation)
        completion_probability = (student_ability * 0.6 + student_motivation * 0.4)
        will_complete = np.random.random() < completion_probability
        
        # Determine how many chapters to complete
        if will_complete:
            chapters_to_complete = n_chapters
        else:
            # Drop out somewhere in the middle
            dropout_point = np.random.randint(1, max(2, int(n_chapters * 0.7)))
            chapters_to_complete = dropout_point
        
        # Generate chapter-level data
        for chapter in range(1, chapters_to_complete + 1):
            # Chapter difficulty (some chapters are harder)
            chapter_difficulty = course_difficulty * np.random.uniform(0.7, 1.3)
            chapter_difficulty = min(1.0, max(0.1, chapter_difficulty))
            
            # Score based on student ability and chapter difficulty
            expected_score = (student_ability - chapter_difficulty + 1) / 2
            score = np.random.normal(expected_score * 100, 10)
            score = max(0, min(100, score))  # Clip to [0, 100]
            
            # Time spent based on difficulty and student ability
            # Difficult chapters take more time, low ability students take more time
            base_time = 30  # Base time in minutes
            time_multiplier = (chapter_difficulty / student_ability) * student_motivation
            time_spent = np.random.gamma(2, base_time * time_multiplier)
            time_spent = max(5, min(300, time_spent))  # Clip to reasonable range
            
            # Completion status for this chapter
            chapter_completed = 1 if chapter < chapters_to_complete else 0
            if chapter == chapters_to_complete and will_complete:
                chapter_completed = 1
            
            data.append({
                'student_id': student_id,
                'course_id': course_id,
                'chapter_order': chapter,
                'time_spent': round(time_spent, 2),
                'score': round(score, 2),
                'completion_status': chapter_completed
            })
        
        student_id += 1
    
    df = pd.DataFrame(data)
    return df

def generate_sample_input(df, n_samples=50):
    """
    Generate sample input file for testing (subset of students)
    """
    # Select random students
    unique_students = df['student_id'].unique()
    sample_students = np.random.choice(unique_students, size=min(n_samples, len(unique_students)), replace=False)
    
    sample_df = df[df['student_id'].isin(sample_students)].copy()
    return sample_df

if __name__ == "__main__":
    # Generate training data
    print("Generating synthetic learner data...")
    df = generate_learner_data(n_students=1000, n_courses=10)
    
    # Save training data
    output_path = Path(__file__).parent.parent / "data" / "training_data.csv"
    df.to_csv(output_path, index=False)
    print(f"✓ Training data saved: {output_path}")
    print(f"  Total records: {len(df)}")
    print(f"  Unique students: {df['student_id'].nunique()}")
    print(f"  Unique courses: {df['course_id'].nunique()}")
    
    # Generate sample input
    sample_df = generate_sample_input(df, n_samples=50)
    sample_path = Path(__file__).parent.parent / "data" / "sample_input.csv"
    sample_df.to_csv(sample_path, index=False)
    print(f"✓ Sample input saved: {sample_path}")
    print(f"  Sample records: {len(sample_df)}")
    print(f"  Sample students: {sample_df['student_id'].nunique()}")
    
    # Print statistics
    print("\nData Statistics:")
    print(f"  Average score: {df['score'].mean():.2f}")
    print(f"  Average time spent: {df['time_spent'].mean():.2f} minutes")
    print(f"  Completion rate: {df['completion_status'].mean():.2%}")
