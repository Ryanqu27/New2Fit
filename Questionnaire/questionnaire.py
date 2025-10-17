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
        text_answers = []
        for answer in self.answers:
            text_answers.append(answer.get_answer())
        return text_answers
    
    def get_question(self):
        return self.question
    
    def get_score_of_response(self, user_response: str) -> int:
        for answer in self.answers:
            if user_response == answer.get_answer():
                return answer.get_point_value()
        
def get_workout(score: int):
    #Higher score indicates more intense workout
    if score <= 10:
        return {
            "Monday": "Full Body (Bodyweight squats, knee pushups, planks, light stretching)",
            "Tuesday": "Rest or light walk (20-30 mins)",
            "Wednesday": "Full Body (Glute bridges, wall pushups, crunches, side planks)",
            "Thursday": "Rest or light yoga",
            "Friday": "Full Body (Bodyweight lunges, bird dogs, supermans, sit-ups)",
            "Saturday": "Rest",
            "Sunday": "Optional light cardio (bike or walk, 30 mins)"
        }

    elif 11 <= score <= 16:
        return {
            "Monday": "Upper Body (Pushups, dumbbell rows, shoulder press, planks)",
            "Tuesday": "Lower Body (Squats, lunges, glute bridges, calf raises)",
            "Wednesday": "Cardio (Jog or cycling, 30–40 mins)",
            "Thursday": "Core & Mobility (Planks, leg raises, yoga stretches)",
            "Friday": "Full Body (Circuit training with moderate weights)",
            "Saturday": "Rest or light walk",
            "Sunday": "Active recovery (yoga, hiking, or swimming)"
        }

    else:
        return {
            "Monday": "Push (Bench press, shoulder press, triceps dips, pushups)",
            "Tuesday": "Pull (Pull-ups, barbell rows, bicep curls, face pulls)",
            "Wednesday": "Legs (Squats, deadlifts, lunges, calf raises)",
            "Thursday": "Core & Conditioning (HIIT + ab circuit)",
            "Friday": "Push (Incline press, overhead press, dips, pushups)",
            "Saturday": "Pull + Cardio (Lat pulldowns, curls, sprints or cycling)",
            "Sunday": "Rest or active recovery (mobility work, foam rolling)"
        }
        
    
    
questions = [
    Question("What is your gender?", [
        Answer("Female", 1),
        Answer("Male", 2)
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