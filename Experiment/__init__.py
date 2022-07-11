import random
import itertools
from otree.api import *

class C(BaseConstants):
    answertime = 180
    button_next = 'Continue'
    max_pay = 100000
    NAME_IN_URL = 'experiment'
    NUM_ROUNDS = 1
    participation_pay = 5
    piece_rate = 0.1
    PLAYERS_PER_GROUP = None
    round_time = 3
    study_time = 10

class Subsession(BaseSubsession):
    pass
#
#
class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.IntegerField(label='What is your age?', min=13, max=125)
    gender = models.StringField(
        choices=[['Male', 'Male'], ['Female', 'Female']],
        label='What is your gender?',
        widget=widgets.RadioSelect)

    q_comprehension_screen_2_1 = models.IntegerField(choices=[[1, 'True'], [0, 'False']],
                                                     label='In each screen, there are only two numbers that sum up to the target number.',
                                                     widget=widgets.RadioSelectHorizontal)

    q_comprehension_screen_2_2 = models.IntegerField(choices=[[1, 'True'], [0, 'False']],
                                                     label='The target number is the same in all screens.',
                                                     widget=widgets.RadioSelectHorizontal)

# FUNCTIONS
# PAGES

class a_Welcome(Page):
    """Display instruction page first round only
    This is a template for all the Welcome Pages"""

    def is_displayed(player: Player):
        return player.round_number == 1

    # def vars_for_template(player: Player):
    #     # player.Prolific_ID = player.participant.label
    #     return dict(quiztype=player.participant.quiztype,
    #                 file_abbr=player.participant.quiztype.replace(" & ", ""))

class b_Instructions_part_1(Page):
    form_model = 'player'
    form_fields = ['q_comprehension_screen_2_1','q_comprehension_screen_2_2']

    def error_message(player, values):
        if values['q_comprehension_screen_2_1'] == 0:
            return "The answer is incorrect. Please consult the instructions and try again."

class c_Before_task_start(Page):
    def before_next_page(player: Player, timeout_happened):
        pass

	# def vars_for_template(player: Player):
	# 	return dict(quiztype = player.participant.quiztype,
	# 		file_abbr = player.participant.quiztype.replace(" & ", ""))

class C_a_Question(Page):
    form_model = 'player'
    form_fields = ['answer']

    timeout_seconds = C.answertime
    timer_text = 'Remaining time:'
    timeout_advice = 30

    @staticmethod
    def vars_for_template(player: Player):
        return dict(question=get_question(player),
                    question_nr=player.round_number)

    # @staticmethod
    # def vars_for_template(player: Player):
    #     return dict(question=get_question(player),
    #                 question_nr=player.round_number)
    #
    # @staticmethod
    # def before_next_page(player: Player, timeout_happened):
    #
    #     solution = get_question(player)["solution"]
    #     # by timeout_happened answer = 0  and therefor incorrect
    #     if (player.answer == solution):
    #         player.correct = True
    #         player.participant.nr_correct_part_1 += 1
    #
    # def is_displayed(player: Player):
    #     # only show the first round
    #     return player.round_number <= Constants.num_questions
    #
    # def error_message(player, values):
    #     if values['answer'] > 5 or values['answer'] < 0:
    #         return "Please select one of the five options"


# class Demographics(Page):
#     form_model = 'player'
#     form_fields = ['age', 'gender']
#
#
# class CognitiveReflectionTest(Page):
#     form_model = 'player'
#     form_fields = ['crt_bat', 'crt_widget', 'crt_lake']


page_sequence = [a_Welcome,
                 b_Instructions_part_1,
                 c_Before_task_start]
