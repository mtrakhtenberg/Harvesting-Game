import random

from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'harvesting'
    PLAYERS_PER_GROUP = 9
    NUM_ROUNDS = 4 #one practice, three real rounds


class Subsession(BaseSubsession):
    acres_remaining = models.IntegerField() #running count of acres remaining per player
    #do I need a game finished?
    payround = models.IntegerField() #randomly selected round used for payment

def creating_session(subsession: Subsession):
   random.seed()
   #counters used this round
   subsession.acres_remaining = 40 # initially set to total number of acres available
   subsession.payround = 0 #initialize it to zero, changes in stage 3 when payround is randomly selected

   #set payment round
   if subsession.round_number == C.NUM_ROUNDS: #choose payment round after the third stage
       subsession.payround = random.randint(2, C.NUM_ROUNDS)

class Group(BaseGroup):
    pass


class Player(BasePlayer):
    #identification
    
    #payment
    final_pay = models.IntegerField(initial=0) #final pay
    payment_round = models.IntegerField(initial=0) #randomly selected round used for payment
    pay = models.IntegerField(initial=0) #pay for the round

    #attention check
    attention_check = models.Stringfield(
        choices=[
            ['strongly disagree', 'Strongly disagree'],
            ['somewhat disagree', 'Somewhat disagree'],
            ['Neither agree nor disagree', 'Neither agree nor disagree'],
            ['somewhat agree', 'Somewhat agree'],
            ['strongly agree', 'Strongly agree'],
        ],
        label=" "
    )

    #comprehension quiz
    Q1 = models.StringField(
        choices=[
            ['4', '4'],
            ['20', '20'],
            ['25', '25'],
            ['5', '5'],
        ],
        label="do i want to put the answer here"
    )

    Q2 = models.StringField(
            choices=[
                ['2', '2'],
                ['7', '7'],
                ['3', '3'],
                ['2.8', '2.8'],
            ],
            label="do i want to put the answer here"
        )

# PAGES
class Consent(Page):
    # consent form
    pass

class attention_check(Page):
    form_model = 'player'
    form_fields = ['attention_check']

class Introduction(Page):
    #description of the game
    pass

class Instructions(Page):
    #instructions for the game
    pass


class StartWaitPage(WaitPage):
    #pass the wait page once everyone is done with the attention check
    pass

class comprehension_quiz(Page):
    form_model = 'player'
    form_fields = ['Q1', 'Q2']

class display_round(Page):
    #display the rounds and offerings
    pass
class Results(Page):
    pass


page_sequence = [Consent, attention_check, Introduction, Instructions, StartWaitPage, comprehension_quiz, display_round, Results]
