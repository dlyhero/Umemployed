"""
Management command to populate the question pool with common questions.
Run: python manage.py populate_question_pool
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from job.models import QuestionPool
from resume.models import Skill


class Command(BaseCommand):
    help = 'Populate the question pool with common programming questions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skill',
            type=str,
            help='Specific skill name to populate (e.g., Python)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing questions before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write("Clearing existing question pool...")
            QuestionPool.objects.all().delete()

        skill_name = options.get('skill')
        if skill_name:
            self.populate_skill(skill_name)
        else:
            self.populate_common_skills()

        self.stdout.write(
            self.style.SUCCESS('Question pool populated successfully!')
        )

    def populate_common_skills(self):
        """Populate questions for common programming skills"""
        skills_to_populate = [
            'Python', 'JavaScript', 'React', 'Django', 'Node.js',
            'SQL', 'HTML', 'CSS', 'Git', 'Linux'
        ]
        
        for skill_name in skills_to_populate:
            self.populate_skill(skill_name)

    def populate_skill(self, skill_name):
        """Populate questions for a specific skill"""
        try:
            skill = Skill.objects.get(name=skill_name)
        except Skill.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(f'Skill "{skill_name}" not found. Creating it...')
            )
            # You might want to create the skill or skip
            return

        questions_data = self.get_questions_for_skill(skill_name)
        
        with transaction.atomic():
            created_count = 0
            for question_data in questions_data:
                question, created = QuestionPool.objects.get_or_create(
                    skill=skill,
                    question=question_data['question'],
                    defaults={
                        'option_a': question_data['option_a'],
                        'option_b': question_data['option_b'],
                        'option_c': question_data['option_c'],
                        'option_d': question_data['option_d'],
                        'correct_answer': question_data['correct_answer'],
                        'difficulty': question_data['difficulty'],
                        'area': question_data.get('area', ''),
                    }
                )
                if created:
                    created_count += 1

        self.stdout.write(f'Added {created_count} questions for {skill_name}')

    def get_questions_for_skill(self, skill_name):
        """Return sample questions for each skill"""
        
        if skill_name.lower() == 'python':
            return [
                {
                    'question': 'What is the output of print(type([]))?',
                    'option_a': '<class \'list\'>',
                    'option_b': '<class \'array\'>',
                    'option_c': 'list',
                    'option_d': 'array',
                    'correct_answer': 'A',
                    'difficulty': 'beginner',
                    'area': 'Data Types'
                },
                {
                    'question': 'Which of the following is used to define a function in Python?',
                    'option_a': 'function',
                    'option_b': 'def',
                    'option_c': 'define',
                    'option_d': 'func',
                    'correct_answer': 'B',
                    'difficulty': 'beginner',
                    'area': 'Functions'
                },
                {
                    'question': 'What does the "self" parameter refer to in Python class methods?',
                    'option_a': 'The current instance of the class',
                    'option_b': 'The class itself',
                    'option_c': 'A global variable',
                    'option_d': 'The parent class',
                    'correct_answer': 'A',
                    'difficulty': 'intermediate',
                    'area': 'Object-Oriented Programming'
                },
                {
                    'question': 'What is a Python decorator?',
                    'option_a': 'A design pattern',
                    'option_b': 'A function that modifies another function',
                    'option_c': 'A type of loop',
                    'option_d': 'A data structure',
                    'correct_answer': 'B',
                    'difficulty': 'advanced',
                    'area': 'Advanced Concepts'
                },
                {
                    'question': 'Which method is used to add an element to a Python list?',
                    'option_a': 'add()',
                    'option_b': 'append()',
                    'option_c': 'insert()',
                    'option_d': 'Both b and c',
                    'correct_answer': 'D',
                    'difficulty': 'beginner',
                    'area': 'Data Structures'
                }
            ]
        
        elif skill_name.lower() == 'javascript':
            return [
                {
                    'question': 'What is the correct way to declare a variable in JavaScript?',
                    'option_a': 'var x = 5;',
                    'option_b': 'let x = 5;',
                    'option_c': 'const x = 5;',
                    'option_d': 'All of the above',
                    'correct_answer': 'D',
                    'difficulty': 'beginner',
                    'area': 'Variables'
                },
                {
                    'question': 'What does "=== " do in JavaScript?',
                    'option_a': 'Assignment',
                    'option_b': 'Equality comparison',
                    'option_c': 'Strict equality comparison',
                    'option_d': 'Not equal',
                    'correct_answer': 'C',
                    'difficulty': 'intermediate',
                    'area': 'Operators'
                },
                {
                    'question': 'What is a closure in JavaScript?',
                    'option_a': 'A loop construct',
                    'option_b': 'A function with access to outer variables',
                    'option_c': 'A data type',
                    'option_d': 'An error handling mechanism',
                    'correct_answer': 'B',
                    'difficulty': 'advanced',
                    'area': 'Functions'
                }
            ]
        
        elif skill_name.lower() == 'react':
            return [
                {
                    'question': 'What is JSX in React?',
                    'option_a': 'A JavaScript library',
                    'option_b': 'A syntax extension for JavaScript',
                    'option_c': 'A CSS framework',
                    'option_d': 'A testing tool',
                    'correct_answer': 'B',
                    'difficulty': 'beginner',
                    'area': 'JSX'
                },
                {
                    'question': 'What is the purpose of React hooks?',
                    'option_a': 'To catch fish',
                    'option_b': 'To use state in functional components',
                    'option_c': 'To style components',
                    'option_d': 'To handle errors',
                    'correct_answer': 'B',
                    'difficulty': 'intermediate',
                    'area': 'Hooks'
                }
            ]
        
        # Default fallback questions for any skill
        return [
            {
                'question': f'What is the most important concept to understand in {skill_name}?',
                'option_a': 'Syntax',
                'option_b': 'Best practices',
                'option_c': 'Core concepts',
                'option_d': 'All of the above',
                'correct_answer': 'D',
                'difficulty': 'beginner',
                'area': 'General'
            },
            {
                'question': f'Which of the following is a best practice when working with {skill_name}?',
                'option_a': 'Write clean, readable code',
                'option_b': 'Follow established conventions',
                'option_c': 'Comment your code appropriately',
                'option_d': 'All of the above',
                'correct_answer': 'D',
                'difficulty': 'intermediate',
                'area': 'Best Practices'
            }
        ]
