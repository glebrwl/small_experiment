from otree.api import *
import itertools

class C(BaseConstants):
    answertime = 30                             # Time given to perform tasks
    bonus_amount = 10000                        # Specify bonus amount here
    button_next = 'Continue'
    charity_name = 'the Feast of Saint Patrick' # Specify the Charity name here
    GBP_threshold = 0.1                         # Specify minimum GBP threshold for receiving bonus_amount
    max_pay = 100000
    NAME_IN_URL = 'donations_experiment'
    not_defined = -1
    NUM_ROUNDS = 1
    participation_pay = 5                       # Payment for participation
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
    treatment = models.IntegerField(initial = 0)
    #Correct answers in Part 1 and Part 2:
    nr_correct_1 = models.IntegerField(initial = -1)
    nr_correct_2 = models.IntegerField(initial = -1)
    #Payment info:
    earnings_P1 = models.FloatField(initial=-1)
    earnings_P2 = models.FloatField(initial = -1)
    P1_GBP = models.FloatField(initial=-1)
    P2_GBP = models.FloatField(initial=-1)
    don_amount = models.FloatField(initial=-1)
    bonus = models.FloatField(initial = 0)
    total_earnings = models.FloatField(initial = 0)
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
    donate_ante_abs = models.FloatField(min = 0,
                                          max = C.max_pay,
                                          label = "")
    donate_ante_abs_hypo = models.FloatField(min = 0,
                                             label = "")
    donate_ante_share = models.IntegerField(min = 0,
                                            max = 100,
                                            label = "")
    donate_ante_share_hypo = models.IntegerField(min = 0,
                                                 max = 100,
                                                 label = "")
    donate_post_hypo = models.IntegerField(min = 0,
                                           max = 100,
                                           label = "")
    donate_post_share = models.IntegerField(min = 0,
                                          max = 100,
                                          label = "")
    subjective_risk = models.IntegerField(initial = -1)
    # k_Questionnaire:
    q_age = models.IntegerField(min = 18,
                                max = 99,
                                label = "How old are you?")
    q_gender = models.StringField(choices = [['Female', 'Female'], ['Male', 'Male']],
                                  label = "What is your sex?",
                                  widget = widgets.RadioSelectHorizontal)
    q_Alevel = models.BooleanField( choices = [['Yes', 'Yes'], ['No', 'No']],
                                    label = "Have you completed A levels or an equivalent level of education that qualifies you for university studies?",
                                    widget = widgets.RadioSelectHorizontal)
    q_degree = models.BooleanField(choices = [['Yes', 'Yes'], ['No', 'No']],
                                   label = "Were you a university student at some point in time during your life, including current enrollment?",
                                   widget = widgets.RadioSelectHorizontal)
    q_subject = models.StringField(choices = [[1, 'Humanities'], [2, 'Business and Economics'],
                                              [3, 'Other Social Sciences'], [4, 'Engineering and Computer Science'],
                                              [5, 'Life Sciences'], [6, 'Cognitive Science'], [7, 'Other Natural Sciences and Math'], [8, 'Law']],
                                   label = "Which of the following categories best fits the subject you studied?",
                                   initial = 0,
                                   blank = True)
    q_employment = models.StringField(choices = [['Full-Time', 'Full-Time'],
                                                 ['Part-Time', 'Part-Time'],
                                                 ['Self-employed', 'Self-employed'],
                                                 ['No', 'No']],
                                      label = "Are you currently employed?",
                                      widget = widgets.RadioSelectHorizontal)
    q_occupation = models.StringField(initial = "",
                                      label = "What is your current occupation?",
                                      blank = True)

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
def player_get_earnings(player):
    player.earnings_P1 = round(player.nr_correct_1 * C.piece_rate, 2)
    player.earnings_P2 = round(player.nr_correct_2 * C.piece_rate, 2)

def player_calculate_payoffs(player):
    player.P1_GBP = player.earnings_P1

    if player.participant.treatment == 1:
        player.P2_GBP = round(player.earnings_P2 * (1 - player.donate_ante_share/100), 2)
        player.don_amount = round(player.earnings_P2 * player.donate_ante_share/100, 2)

    elif player.participant.treatment == 2:
        if player.donate_ante_abs >= player.earnings_P2:
            player.P2_GBP = 0
            player.don_amount = player.earnings_P2
        else:
            player.P2_GBP = round(player.earnings_P2 - player.donate_ante_abs, 2)
            player.don_amount = round(player.donate_ante_abs, 2)

    else:
        player.P2_GBP = round(player.earnings_P2 * (1 - player.donate_post_share / 100), 2)
        player.don_amount = round(player.earnings_P2 * player.donate_post_share / 100, 2)

    if player.P2_GBP >= C.GBP_threshold:
        player.bonus = C.bonus_amount

    player.total_earnings = round(C.participation_pay + player.P1_GBP + player.P2_GBP + player.bonus, 2)
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
        player.treatment = player.participant.treatment
        return dict(treatment = player.treatment)
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

# class d_Task_P1(Page):
#     timeout_seconds = C.answertime
#     form_model = 'player'
#     form_fields = ['nr_correct_1']

class d_Task_P1_nice(Page):
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
                    comprehension_screen_5_label = 'If after the donation is deducted, the earnings from Part 2 are higher than {}, one receives the bonus of {} GBP.'.format(C.GBP_threshold, C.bonus_amount)
                    )

class f_Donation_Ante(Page):
    form_model = 'player'
    form_fields = ['donate_ante_share', 'donate_ante_abs']
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

class g_Subjective_Risk(Page):
    form_model = 'player'
    form_fields = ['subjective_risk']
    @staticmethod
    def vars_for_template(player: Player):
        return dict(treatment = player.participant.treatment
                    )

class g2_Subjective_Risk2(Page):
    form_model = 'player'
    form_fields = ['subjective_risk']
    @staticmethod
    def vars_for_template(player: Player):
        return dict(treatment = player.participant.treatment
                    )

class h_Before_Task_P2(Page):
    pass

# class i_Task_P2(Page):
#     timeout_seconds = C.answertime
#     form_model = 'player'
#     form_fields = ['nr_correct_2']
#     @staticmethod
#     def before_next_page(player, timeout_happened):
#         player_get_earnings(player)

class i_Task_P2_nice(Page):
    timeout_seconds = C.answertime
    form_model = 'player'
    form_fields = ['nr_correct_2']
    @staticmethod
    def before_next_page(player, timeout_happened):
        player_get_earnings(player)

class j_Donation_Ante_Hypothetical(Page):
    form_model = 'player'
    form_fields = ['donate_ante_share_hypo', 'donate_ante_abs_hypo']
    @staticmethod
    def is_displayed(player):
        return player.participant.treatment == 1 or player.participant.treatment == 2
    @staticmethod
    def vars_for_template(player: Player):
        return dict(treatment = player.participant.treatment,
                    label_text_treat_1 = "Below you can enter any number between 0% (donate nothing) and 100% (donate all). It is a hypothetical decision and will not affect your donation or your earnings.",
                    label_text_treat_2 = "Below you can enter any donation amount starting from 0.00 GBP (donate nothing) to {} GBP. It is a hypothetical decision and will not affect your donation or your earnings.".format(player.earnings_P2)
                    )
    @staticmethod
    def get_form_fields(player):
        if player.participant.treatment == 1:
            return ['donate_ante_share_hypo']
        elif player.participant.treatment == 2:
            return ['donate_ante_abs_hypo']
    @staticmethod
    def error_message(player, values):
        if player.participant.treatment == 2:
            if values['donate_ante_abs_hypo'] > player.earnings_P2:
                return 'You can not enter number exceeding your earnings.'
            if values['donate_ante_abs_hypo'] < 0:
                return 'You can not enter negative number.'
    @staticmethod
    def before_next_page(player, timeout_happened):
        player_calculate_payoffs(player)


class j_Donation_Post(Page):
    form_model = 'player'
    form_fields = ['donate_post_share']
    @staticmethod
    def is_displayed(player):
        return player.participant.treatment == 3
    @staticmethod
    def vars_for_template(player: Player):
        return dict(treatment = player.treatment)
    @staticmethod
    def before_next_page(player, timeout_happened):
        player_calculate_payoffs(player)

class k_Questionnaire(Page):
    # changed to Welcome base class
    form_model = 'player'
    form_fields = ['q_age',
                   'q_gender',
                   'q_Alevel',
                   'q_degree',
                   'q_subject',
                   'q_employment',
                   'q_occupation']
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.q_degree == 'No':
            player.q_subject = " Not Applicable"
        if player.q_employment == 'No':
            player.q_occupation = "Not Applicable"

class l_Feedback(Page):
    form_model = 'player'
    @staticmethod
    def vars_for_template(player: Player):
        return dict(treatment = player.treatment,
                    charity_receives = player.don_amount*2)

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# PAGE SEQUENCE

page_sequence = [a_Welcome,
                 b_Instructions_P1,
                 c_Before_Task_P1,
                 # d_Task_P1,
                 d_Task_P1_nice,
                 e_Results_P1_Inst_P2,
                 f_Donation_Ante,
                 f_Donation_Post_Hypothetical,
                 # g_Subjective_Risk,
                 g2_Subjective_Risk2,
                 h_Before_Task_P2,
                 # i_Task_P2,
                 i_Task_P2_nice,
                 j_Donation_Ante_Hypothetical,
                 j_Donation_Post,
                 k_Questionnaire,
                 l_Feedback]

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
