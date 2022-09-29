import json
import time
import random
import itertools
from otree.api import *
from pathlib import Path
from otree import settings
from PIL import Image, ImageDraw, ImageFont
from .image_utils import encode_image
from Experiment import task_decoding

TEXT_FONT = Path(__file__).parent / "assets" / "FreeSerifBold.otf"

CHARSET = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
DIGITS = tuple('0123456789')
WORD_LENGTH = 5

INPUT_TYPE = "text"
INPUT_HINT = "enter text decoded from the number"

class C(BaseConstants):
    answertime = 20                             # Time given to perform tasks
    bonus_amount = 10                           # Specify bonus amount here
    button_next = 'Continue'
    charity_name = 'the Red Cross' # Specify the Charity name here
    GBP_threshold = 0.5                         # Specify minimum GBP threshold for receiving bonus_amount
    max_pay = 10
    NAME_IN_URL = 'donations_experiment'
    not_defined = -1
    NUM_ROUNDS = 1
    participation_pay = 5                       # Payment for participation
    piece_rate = 0.25                            # Payment per correct answer
    PLAYERS_PER_GROUP = None
    round_time = answertime//60
    study_time = 10
    captcha_length = 3

    name_in_url = "transcription"                               #############################
    players_per_group = None                                    #############################
    num_rounds = 1                                              #############################


class Subsession(BaseSubsession):
    pass

def creating_session(subsession):
    treated = itertools.cycle([1, 2, 3]) # 1 – ante_share, 2 – ante_absolute, 3 – post_share

    for player in subsession.get_players():
        participant = player.participant
        participant.Prolific_ID = player.participant.label
        participant.treatment = next(treated)

    session = subsession.session
    defaults = dict(
        retry_delay = 0.3, puzzle_delay = 0.3, attempts_per_puzzle=1, max_iterations=None
    )
    session.params = {}
    for param in defaults:
        session.params[param] = session.config.get(param, defaults[param])

class Group(BaseGroup):
    pass

class Player(BasePlayer):

    iteration = models.IntegerField(initial=0)                  #####################################
    num_trials = models.IntegerField(initial=0)                 #####################################
    num_correct = models.IntegerField(initial=0)                #####################################
    num_failed = models.IntegerField(initial=0)                 #####################################

    Prolific_ID = models.LongStringField()
    treatment = models.IntegerField(initial = 0)
    #Correct answers in Part 1 and Part 2:
    num_correct_1 = models.IntegerField(initial = -1)
    num_correct_2 = models.IntegerField(initial = -1)
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

# puzzle-specific stuff
class Puzzle(ExtraModel):
    """A model to keep record of all generated puzzles"""
    player = models.Link(Player)
    iteration = models.IntegerField(initial=0)
    attempts = models.IntegerField(initial=0)
    timestamp = models.FloatField(initial=0)
    # can be either simple text, or a json-encoded definition of the puzzle, etc.
    text = models.LongStringField()
    # solution may be the same as text, if it's simply a transcription task
    solution = models.LongStringField()
    response = models.LongStringField()
    response_timestamp = models.FloatField()
    is_correct = models.BooleanField()

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# FUNCTIONS
def player_get_earnings(player):
    player.earnings_P1 = round(player.num_correct_1 * C.piece_rate, 2)
    player.earnings_P2 = round(player.num_correct_2 * C.piece_rate, 2)

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

def generate_puzzle_fields():
    """Create new puzzle for a player"""

    chars = random.sample(CHARSET, len(DIGITS))
    digits = random.sample(DIGITS, len(DIGITS))

    lookup = dict(zip(digits, chars))

    coded_word = ''.join(random.sample(DIGITS, WORD_LENGTH))
    solution = ''.join(lookup[digit] for digit in coded_word)

    return dict(
        text = json.dumps(dict(rows=[chars, digits], coded_word=coded_word)),
        solution = solution,
    )

def generate_puzzle(player: Player) -> Puzzle:
    """Create new puzzle for a player"""
    task_module = task_decoding
    fields = task_module.generate_puzzle_fields()
    player.iteration += 1
    return Puzzle.create(
        player=player, iteration=player.iteration, timestamp=time.time(), **fields
    )

def is_correct(response, puzzle):
    return puzzle.solution.lower() == response.lower()


TEXT_SIZE = 32
TEXT_PADDING = TEXT_SIZE
CELL_DIM = TEXT_SIZE + TEXT_PADDING * 2
MID = CELL_DIM * 0.5


def render_image(puzzle):
    data = json.loads(puzzle.text)

    font = ImageFont.truetype(str(TEXT_FONT), TEXT_SIZE)
    img_w = CELL_DIM * len(DIGITS)
    # 4 because 2 rows + blank space + row for coded word
    img_h = CELL_DIM * 4
    image = Image.new("RGB", (img_w, img_h))
    draw = ImageDraw.Draw(image)

    for rownum, row in enumerate(data['rows']):
        for colnum, char in enumerate(row):
            x = colnum * CELL_DIM
            y = rownum * CELL_DIM
            draw.rectangle([x, y, x + CELL_DIM, y + CELL_DIM])
            draw.text((x + MID, y + MID), char, font=font, anchor="mm")

    coded_word = data['coded_word']
    w, h = draw.textsize(coded_word)
    draw.text(
        ((img_w - w) / 2, image.height - MID),
        data['coded_word'],
        font=font,
        anchor="mm",
    )

    return image

def get_current_puzzle(player):
    puzzles = Puzzle.filter(player = player, iteration = player.iteration)
    if puzzles:
        [puzzle] = puzzles
        return puzzle

def encode_puzzle(puzzle: Puzzle):
    """Create data describing puzzle to send to client"""
    task_module = task_decoding  # noqa
    # generate image for the puzzle
    image = task_module.render_image(puzzle)
    data = encode_image(image)
    return dict(image=data)

def get_progress(player: Player):
    """Return current player progress"""
    return dict(
        num_trials = player.num_trials,
        num_correct = player.num_correct,
        num_incorrect = player.num_failed,
        iteration = player.iteration,
    )

def play_game(player: Player, message: dict):
    """Main game workflow
    Implemented as reactive scheme: receive message from vrowser, react, respond.

    Generic game workflow, from server point of view:
    - receive: {'type': 'load'} -- empty message means page loaded
    - check if it's game start or page refresh midgame
    - respond: {'type': 'status', 'progress': ...}
    - respond: {'type': 'status', 'progress': ..., 'puzzle': data} -- in case of midgame page reload

    - receive: {'type': 'next'} -- request for a next/first puzzle
    - generate new puzzle
    - respond: {'type': 'puzzle', 'puzzle': data}

    - receive: {'type': 'answer', 'answer': ...} -- user answered the puzzle
    - check if the answer is correct
    - respond: {'type': 'feedback', 'is_correct': true|false, 'retries_left': ...} -- feedback to the answer

    If allowed by config `attempts_pre_puzzle`, client can send more 'answer' messages
    When done solving, client should explicitely request next puzzle by sending 'next' message

    Field 'progress' is added to all server responses to indicate it on page.

    To indicate max_iteration exhausted in response to 'next' server returns 'status' message with iterations_left=0
    """
    session = player.session
    my_id = player.id_in_group
    params = session.params
    task_module = task_decoding

    now = time.time()
    # the current puzzle or none
    current = get_current_puzzle(player)

    message_type = message['type']

    # page loaded
    if message_type == 'load':
        p = get_progress(player)
        if current:
            return {
                my_id: dict(type='status', progress=p, puzzle=encode_puzzle(current))
            }
        else:
            return {my_id: dict(type='status', progress=p)}

    if message_type == "cheat" and settings.DEBUG:
        return {my_id: dict(type='solution', solution=current.solution)}

    # client requested new puzzle
    if message_type == "next":
        if current is not None:
            if current.response is None:
                raise RuntimeError("trying to skip over unsolved puzzle")
            if now < current.timestamp + params["puzzle_delay"]:
                raise RuntimeError("retrying too fast")
            if current.iteration == params['max_iterations']:
                return {
                    my_id: dict(
                        type='status', progress=get_progress(player), iterations_left=0
                    )
                }
        # generate new puzzle
        z = generate_puzzle(player)
        p = get_progress(player)
        return {my_id: dict(type='puzzle', puzzle=encode_puzzle(z), progress=p)}

    # client gives an answer to current puzzle
    if message_type == "answer":
        if current is None:
            raise RuntimeError("trying to answer no puzzle")

        if current.response is not None:  # it's a retry
            if current.attempts >= params["attempts_per_puzzle"]:
                raise RuntimeError("no more attempts allowed")
            if now < current.response_timestamp + params["retry_delay"]:
                raise RuntimeError("retrying too fast")

            # undo last updation of player progress
            player.num_trials -= 1
            if current.is_correct:
                player.num_correct -= 1
            else:
                player.num_failed -= 1

        # check answer
        answer = message["answer"]

        if answer == "" or answer is None:
            raise ValueError("bogus answer")

        current.response = answer
        current.is_correct = task_module.is_correct(answer, current)
        current.response_timestamp = now
        current.attempts += 1

        # update player progress
        if current.is_correct:
            player.num_correct += 1
        else:
            player.num_failed += 1
        player.num_trials += 1

        retries_left = params["attempts_per_puzzle"] - current.attempts
        p = get_progress(player)
        return {
            my_id: dict(
                type='feedback',
                is_correct=current.is_correct,
                retries_left=retries_left,
                progress=p,
            )
        }

    raise RuntimeError("unrecognized message from client")

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
            return 'At least one of the answers is incorrect. Please consult the instructions and try again.'
        if values['q_comprehension_screen_2_2'] == 1:
            return 'At least one of the answers is incorrect. Please consult the instructions and try again.'
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
#     form_fields = ['num_correct_1']

# class d_Task_P1_nice(Page):
#     timeout_seconds = C.answertime
#     form_model = 'player'
#     form_fields = ['num_correct_1']

class d_Task_P1_decoding(Page):
    timeout_seconds = C.answertime
    live_method = play_game
    form_model = 'player'

    @staticmethod
    def js_vars(player: Player):
        return dict(params = player.session.params)

    @staticmethod
    def vars_for_template(player: Player):
        task_module = task_decoding
        return dict(DEBUG = settings.DEBUG,
                    input_type = task_module.INPUT_TYPE,
                    placeholder = task_module.INPUT_HINT)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if not timeout_happened and not player.session.params['max_iterations']:
            raise RuntimeError("malicious page submission")
        player.num_correct_1 = player.num_correct
        player.num_correct = 0
        # player.num_trials = 0
        # player.iteration = 0

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
                    comprehension_screen_5_label = 'If after the donation is deducted, the earnings from Part 2 are higher than {} GBP, one receives the bonus of {} GBP.'.format(C.GBP_threshold, C.bonus_amount)
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
#     form_fields = ['num_correct_2']
#     @staticmethod
#     def before_next_page(player, timeout_happened):
#         player_get_earnings(player)

# class i_Task_P2_nice(Page):
#     timeout_seconds = C.answertime
#     form_model = 'player'
#     form_fields = ['num_correct_2']
#     @staticmethod
#     def before_next_page(player, timeout_happened):
#         player_get_earnings(player)

class i_Task_P2_decoding(Page):
    timeout_seconds = C.answertime
    live_method = play_game
    # form_model = 'player'

    @staticmethod
    def js_vars(player: Player):
        return dict(params = player.session.params)

    @staticmethod
    def vars_for_template(player: Player):
        task_module = task_decoding
        return dict(DEBUG = settings.DEBUG,
                    input_type = task_module.INPUT_TYPE,
                    placeholder = task_module.INPUT_HINT)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if not timeout_happened and not player.session.params['max_iterations']:
            raise RuntimeError("malicious page submission")
        player.num_correct_2 = player.num_correct
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
                    don_amount = player.don_amount,
                    charity_receives = player.don_amount*2)

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# PAGE SEQUENCE

page_sequence = [a_Welcome,
                 b_Instructions_P1,
                 c_Before_Task_P1,
                 # d_Task_P1,
                 # d_Task_P1_nice,
                 d_Task_P1_decoding,
                 e_Results_P1_Inst_P2,
                 f_Donation_Ante,
                 f_Donation_Post_Hypothetical,
                 # g_Subjective_Risk,
                 g2_Subjective_Risk2,
                 h_Before_Task_P2,
                 # i_Task_P2,
                 # i_Task_P2_nice,
                 i_Task_P2_decoding,
                 j_Donation_Ante_Hypothetical,
                 j_Donation_Post,
                 k_Questionnaire,
                 l_Feedback]

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
