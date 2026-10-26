import random

from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'harvesting'
    PLAYERS_PER_GROUP = 9
    NUM_ROUNDS = 20

    #block one (practice) = rounds 1-5
    #block two (real_ = rounds 6-20)
        #round 1 = 6-10
        #round 2 = 11-15
        #round 3 = 16-20


class Subsession(BaseSubsession):
    #do I need a game finished?
    payround = models.IntegerField() #randomly selected round used for payment

def creating_session(subsession: Subsession):
   random.seed()
   #counters used this round
   subsession.payround = 0 #initialize it to zero, changes in stage 3 when payround is randomly selected

   for player in subsession.get_players():
       if subsession.round_number in [1, 6, 11, 16]:
           player.acres_remaining = 40
       else:
           player.acres_remaining = player.in_round(
               subsession.round_number - 1
           ).acres_remaining

   #set payment round
   if subsession.round_number == C.NUM_ROUNDS: #choose payment round after the third stage
       subsession.payround = random.randint(2, C.NUM_ROUNDS)

class Group(BaseGroup):
    pass


class Player(BasePlayer):
    #identification

    block = models.IntegerField() #1 is practice, 2 is real
    real_round = models.IntegerField() #0 for practice, 1-3 for real
    stage = models.IntegerField() #1-5

    acres_remaining = models.IntegerField(initial=40) #running count of acres remaining per player
    acres_harvested = models.IntegerField(min=0, max=40) #acres harvested this round
    trees = models.FloatField(initial=0) #number of trees remaining at the end of the game

    
    #payment
    final_pay = models.IntegerField(initial=0) #final pay
    payment_round = models.IntegerField(initial=0) #randomly selected round used for payment
    pay = models.IntegerField(initial=0) #pay for the round

    #attention check
    attention_check = models.StringField(
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

def set_labels(player: Player):
    rn = player.round_number
    if rn <= 5:
        player.block = 1
        player.real_round = 0
        player.stage = rn
    else:
        player.block = 2
        player.real_round = (rn-6) // 5 + 1
        player.stage = (rn-6) % 5 + 1

def set_payoffs(player: Player):
    #set payoffs for the round
    #earn 9 points for each acre harvested
    player.pay = player.acres_harvested * 9
    player.acres_remaining -= player.acres_harvested
    #1 acre of forested land will regrow for every 4 acres of forested land remaining in rounds 1-4
    if player.subsession.round_number in [1, 2, 3, 4]:
        player.acres_remaining += player.acres_remaining // 4
        player.acres_remaining = min(player.acres_remaining, 40)
    #payment stage = each point earned is worth 0.01 dollars, so multiply by 0.01 to get the final pay in dollars
    #if the final round, then set the payment round to the randomly selected round
    if player.subsession.round_number == C.NUM_ROUNDS:
        player.payment_round = player.subsession.vars['payround']
        points = sum(
            p.pay for p in player.in_all_rounds()
            if p.block ==2 and p.real_round == player.payment_round
        )
        player.final_pay = points * 0.01
        player.trees = player.acres_remaining // 10
        #1 tree for every 10 acres remaining, can be partial trees


# PAGES
class Consent(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class attention_check(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
    form_model = 'player'
    form_fields = ['attention_check']

class Intro(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class Instructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class begin_practice(Page):
    #begin practice round
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
    #start of block one

class begin_real(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number in [6,11,16]


class Harvest(Page):
    @staticmethod
    def vars_for_template(player: Player):
        participants = {
            participant.id_in_group: participant
            for participant in player.group.get_players()
        }
        ordered_ids = [
            participant_id
            for participant_id in participants
            if participant_id != player.id_in_group
        ]
        ordered_ids.insert(4, player.id_in_group)

        return dict(
            forest_views=[
                dict(
                    number=participant_id,
                    is_self=participant_id == player.id_in_group,
                    acres=participants[participant_id].acres_remaining,
                    image=(
                        f'harvesting/forest_'
                        f'{participants[participant_id].acres_remaining}.png'
                    ),
                )
                for participant_id in ordered_ids
            ]
        )

    def before_next_page(player: Player, timeout_happened):
        set_labels(player)
        set_payoffs(player)

    form_model = 'player'
    form_fields = ['acres_harvested']

    @staticmethod
    def error_message(player: Player, values):
        harvested = values['acres_harvested']
        if harvested > player.acres_remaining:
            return (
                'You cannot harvest more acres than you currently have '
                f'({player.acres_remaining}).'
            )

class RoundResults(Page):
    #display the results of the round
    pass

class FinalResults(Page):
    #display the final results
    @staticmethod
    def is_displayed(player: Player):
        return player.subsession.round_number == C.NUM_ROUNDS


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

class GroupStatus(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group_players = sorted(
            player.group.get_players(),
            key=lambda participant: participant.id_in_group
        )
        return dict(
            group_players=[
                dict(
                    number=participant.id_in_group,
                    acres=participant.acres_remaining,
                    image=f'....'
                )
                for participant in group_players
            ]
        )


#consent, attention check, intro, instructions, comprehension questions, practice rounds, 3 real stages, final results
#within comprehension questions, one question per page (with instructions on each?) to allow 3 trys on both (unless prof goff says otherwise)
#for practice rounds, begin practice page, then rounds 1-5, end practice stage page
#for each stage, can code for the page to reflect which round, so begin, 5 rounds, end stage page
#then demographics, end page, etc.
#check how many wait pages are needed, for when what harvesting looks like needs to be updated
page_sequence = [
    Consent,
    attention_check,
    Intro,
    Instructions,
    StartWaitPage,
    comprehension_quiz,
    Harvest,
    Results,
]
