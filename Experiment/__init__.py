from otree.api import *
from otree.api import *
from csv import reader
import itertools
import random
import pathlib

class C(BaseConstants):
    answertime = 10                             # time given to perform
    bonus_amount = 10000                        # Specify bonus amount here
    button_next = 'Continue'
    charity_name = 'the Feast of Saint Patrick' #Specify Charity name here
    GBP_threshold = 10000.99                    #Specify minimum GBP threshold for receiving bonus_amount
    max_pay = 100000
    NAME_IN_URL = 'donations_experiment'
    not_defined = -1
    NUM_ROUNDS = 1
    participation_pay = 5
    piece_rate = 0.1                            # Payment per correct answer
    PLAYERS_PER_GROUP = None
    round_time = answertime//60
    study_time = 10

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    Prolific_ID = models.LongStringField()
    #Correct answers in Part 1 and Part 2:
    nr_correct_1 = models.IntegerField(initial = -1)
    nr_correct_2 = models.IntegerField(initial = -1)
    #Payment info:
    earnings_P2 = models.FloatField(initial = -1)
    #Comprehension Questions:
    q_comprehension_screen_2_1 = models.IntegerField(choices = [[1, 'True'], [0, 'False']],
                                                     label = 'In each screen, there are only two numbers that sum up to the target number.',
                                                     widget = widgets.RadioSelectHorizontal)
    q_comprehension_screen_2_2 = models.IntegerField(choices = [[1, 'True'], [0, 'False']],
                                                     label = 'The target number is the same in all screens.',
                                                     widget = widgets.RadioSelectHorizontal)
    q_comprehension_screen_5 = models.IntegerField(choices = [[1, 'True'], [0, 'False']],
                                                   widget = widgets.RadioSelectHorizontal)
    #Donations decisions:
    donate_ante_abs = models.IntegerField(min = 0,
                                          max = C.max_pay,
                                          label = "How much do you want to donate to the charity from your upcoming earnings in Part 2?")
    donate_ante_abs_hypo = models.IntegerField(min = 0,
                                               max = C.max_pay,
                                               label = "")
    donate_ante_share = models.IntegerField(min = 0,
                                            max = 100,
                                            label = "What share of your upcoming earnings from Part 2 do you want to donate to the charity?")
    donate_ante_share_hypo = models.IntegerField(min = 0,
                                                 max = 100,
                                                 label = "")
    donate_post_hypo = models.IntegerField(min = 0,
                                           max = 100,
                                           label = "What share of your upcoming earnings from Part 2 do you want to donate to the charity?")
    donate_post_share = models.IntegerField(min = 0,
                                            max = 100,
                                            label = "")
    subjective_risk = models.IntegerField(initial = -1)
    #Questionnaire fields:
    # q_don_decision = models.LongStringField()
    # ##Demographics and General:
    # q_age = models.IntegerField(label = 'How old are you?', min = 13, max = 99)
    # q_sex = models.StringField(
    #     choices = [[1, 'Female'], [2, 'Male']],
    #     label = 'What is your sex?',
    #     widget = widgets.RadioSelect)
    # q_uni = models.StringField(choices = [[1, 'Yes'], [2, 'No']],
    #                          label = 'Were you a university student at some point in time, including current enrollment?',
    #                          widget = widgets.RadioSelect)
    # q_subject = models.StringField(
    #     choices=[[1, 'Humanities'], [2, 'Business and Economics'],
    #              [3, 'Other Social Sciences'], [4, 'Engineering and Computer Science'], [5, 'Life Sciences'], [
    #                  6, 'Cognitive Science'], [7, 'Other Natural Sciences and Math'], [8, 'Law']],
    #     label="Which of the following categories best fits the subject you studied?",
    #     initial=0,
    #     blank=True)
    # q_employment = models.StringField(
    #     choices=[[1, 'Full-Time'],
    #              [2, 'Part-Time'], [3, 'Self-employed'], [4, 'No']],
    #     label="Are you currently employed?",
    #     widget=widgets.RadioSelectHorizontal)
    # q_occupation = models.StringField(
    #     initial="",
    #     label="What is your current occupation?",
    #     blank=True)
    # q_political_spect = models.IntegerField(initial=-1)

def creating_session(subsession):
    treated = itertools.cycle([1, 2, 3]) # 1 – ante_share, 2 – ante_absolute, 3 – post_share

    for player in subsession.get_players():
        participant = player.participant
        participant.Prolific_ID = player.participant.label
        participant.treatment = next(treated)

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# FUNCTIONS
def player_get_payment_info(player):
    return player.nr_correct_2 * C.piece_rate

def player_store_data(player):
    player.participant.nr_correct_1 = player.nr_correct_1
    player.participant.nr_correct_2 = player.nr_correct_2
    dict = player.participant.dict
    dict['nr_correct_1'] = player.nr_correct_1
    dict['nr_correct_2'] = player.nr_correct_2
    dict['earnings_P2'] = player.earnings_P2

    # print("*" * 50)
    # print("****** Employee 1:", player.PlayerID, "has finished ******")
    # print("*" * 50)
    # print("*" * 50)

# def get_question_nr(player):
#     """ Cycle through the questions, using remainder operator `%`
#     round 1 -> q1, round 2-> q2 1, ... round 11->q1
#     need to substract 1 first and that afterwards for the formula to work
#     """
#     return ((player.round_number - 1) % C.num_questions) + 1

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# PAGES
class a_Welcome(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        player.Prolific_ID = player.participant.label
        return dict(treatment = player.participant.treatment,
                    )
 #I do not know why it does not show the variable in the database, but it generates it, see welcome page.
class b_Instructions_P1(Page):
    form_model = 'player'
    form_fields = ['q_comprehension_screen_2_1','q_comprehension_screen_2_2']
    @staticmethod
    def error_message(player, values):
        if values['q_comprehension_screen_2_1'] == 0:
            return 'The answer is incorrect. Please consult the instructions and try again.'
        if values['q_comprehension_screen_2_2'] == 1:
            return 'The answer is incorrect. Please consult the instructions and try again.'
    @staticmethod
    def vars_for_template(player: Player):
        player.Prolific_ID = player.participant.label
        #MC: do not forget to put a checker on the second comprehension question too

class c_Before_Task_P1(Page):
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pass
    @staticmethod
    def vars_for_template(player: Player):
        player.Prolific_ID = player.participant.label

class d_Task_P1(Page):
    timeout_seconds = C.answertime
    form_model = 'player'
    form_fields = ['nr_correct_1']

class e_Results_P1_Inst_P2(Page):
    form_model = 'player'
    form_fields = ['q_comprehension_screen_5']
    @staticmethod
    def error_message(player, values):
        if values['q_comprehension_screen_5'] == 0:
            return "The answer is incorrect. Please consult the instructions and try again."
    @staticmethod
    def vars_for_template(player: Player):
        player.Prolific_ID = player.participant.label
        return dict(treatment = player.participant.treatment,
                    comprehension_screen_5_label = 'If after the donation, you earned more than {} in Part 2, you will receive a bonus of {} GBP. Therefore, ultimately, to receive the bonus, one need to earn in Part 2 at least {} plus the chosen donation'.format(C.GBP_threshold, C.bonus_amount, C.GBP_threshold)
                    )

class f_Donation_Ante(Page):
    form_model = 'player'
    form_fields = ['donate_ante_abs', 'donate_ante_share']
    @staticmethod
    def is_displayed(player):
        return player.participant.treatment == 1 or player.participant.treatment == 2
    @staticmethod
    def vars_for_template(player: Player):
        return dict(treatment = player.participant.treatment
                    )
    @staticmethod
    def get_form_fields(player):
        if player.participant.treatment == 1:
            return ['donate_ante_share']
        elif player.participant.treatment == 2:
            return ['donate_ante_abs']
    # @staticmethod
    # def error_message(player, values):
    #     if player.participant.treatment == 1:
    #         if values['donate_ante_share'] < 0:
    #             return "You can not donate negative share of earnings."
    #         elif values['donate_ante_share'] > 100:
    #             return "You can not donate more than 100% of earnings."
    #     elif player.participant.treatment == 2:
    #         if values['donate_ante_abs'] < 0:
    #             return "You can not donate negative amount of money."

class f_Donation_Post_Hypothetical(Page):
    form_model = 'player'
    form_fields = ['donate_post_hypo']
    @staticmethod
    def is_displayed(player):
        return player.participant.treatment == 3
    @staticmethod
    def vars_for_template(player: Player):
        return dict(treatment = player.participant.treatment
                    )
    # @staticmethod
    # def error_message(player, values):
    #     if player.participant.treatment == 3:
    #         if values['donate_post_hypo'] < 0:
    #             return "You can not donate negative share of earnings."
    #         elif values['donate_post_hypo'] > 100:
    #             return "You can not donate more than 100% of earnings."

class g_Subjective_Risk(Page):
    form_model = 'player'
    form_fields = ['subjective_risk']
    @staticmethod
    def vars_for_template(player: Player):
        return dict(treatment = player.participant.treatment
                    )

class h_Before_Task_P2(Page):
    pass

class i_Task_P2(Page):
    timeout_seconds = C.answertime
    form_model = 'player'
    form_fields = ['nr_correct_2']

class j_Results_P2(Page):
    form_model = 'player'
    def before_next_page(player, timeout_happened):
        player.earnings_P2 = player_get_payment_info(player)
        # player.player_store_data()
        # player.player_export_data()

class k_Donation_Ante_Hypothetical(Page):
    form_model = 'player'
    form_fields = ['donate_ante_share_hypo', 'donate_ante_abs_hypo']
    @staticmethod
    def is_displayed(player):
        return player.participant.treatment == 1 or player.participant.treatment == 2
    @staticmethod
    def vars_for_template(player: Player):
        return dict(treatment = player.participant.treatment
                    )
    @staticmethod
    def get_form_fields(player):
        if player.participant.treatment == 1:
            return ['donate_ante_share_hypo']
        elif player.participant.treatment == 2:
            return ['donate_ante_abs_hypo']

class k_Donation_Post(Page):
    form_model = 'player'
    form_fields = ['donate_post_share']
    @staticmethod
    def is_displayed(player):
        return player.participant.treatment == 3
    @staticmethod
    def vars_for_template(player: Player):
        return dict(treatment = player.participant.treatment
                    )

# class l_Questionnaire(Page):
#     form_model = 'player'
#     form_fields = ['q_don_decision',
#                    'q_age',
#                    'q_sex',
#                    'q_uni',
#                    'q_subject',
#                    'q_employment',
#                    'q_occupation']
    # @staticmethod
    # def is_displayed(player: Player):
    #     # Only show on the last round
    #     return player.round_number == 1
#     def before_next_page(player: Player, timeout_happened):
#         if player.q_uni == 'No':
#             player.q_subject = -1
# # ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# PAGE SEQUENCE

page_sequence = [a_Welcome,
                 b_Instructions_P1,
                 c_Before_Task_P1,
                 d_Task_P1,
                 e_Results_P1_Inst_P2,
                 f_Donation_Ante,
                 f_Donation_Post_Hypothetical,
                 g_Subjective_Risk,
                 h_Before_Task_P2,
                 i_Task_P2,
                 j_Results_P2,
                 k_Donation_Ante_Hypothetical,
                 k_Donation_Post]

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------