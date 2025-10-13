from typing import List

class Answer:
    # Each answer choice has a point value. A higher point value should indicate recommending
    # a larger/harder workout plan. 
    def __init__(self, answer: str, pointValue: int):
        self.answer = answer
        self.pointValue = pointValue
            
    def get_point_value(self):
        return self.pointValue
    
    def get_answer(self):
        return self.answer  

class Question:
    def __init__(self, question: str, answers: List[Answer]):
        self.question = question
        self.answers = answers
        
    def get_answers(self):
        return self.answers
    
    def get_question(self):
        return self.question
    
questions = [
    Question("What is your gender?", [
        Answer("Female", 1),
        Answer("Male, 2")
    ]),
    Question("How old are you?", [
        Answer("17 or younger", 3),
        Answer("18-25 years old", 4),
        Answer("26-35 years old", 3),
        Answer("36-59 years old", 2),
        Answer("60+ years old", 1)
    ]),
    Question("How experienced are you with strength training?", [
        Answer("Beginner", 1),
        Answer("Intermediate", 2),
        Answer("Advanced", 3)
    ]),
    Question("What is your main goal?", [
        Answer("Lose weight", 1),
        Answer("Build muscle", 2),
        Answer("Increase endurance", 3)
    ]),
    Question("How soon do you want to see results?", [
        Answer("No rush", 1),
        Answer("Within a few months", 2),
        Answer("As fast as possible", 3)
    ]),
    Question("How many days per week can you work out?", [
        Answer("1-2 days", 1),
        Answer("3-4 days", 2),
        Answer("5+ days", 3)
    ]),
    Question("How long are your typical workout sessions?", [
        Answer("Less than 30 minutes", 1),
        Answer("30-60 minutes", 2),
        Answer("Over an hour", 3)
    ]),
    Question("Do you have any current injuries or health limitations?", [
        Answer("Yes", -3),
        Answer("No", 0)
    ]),
]