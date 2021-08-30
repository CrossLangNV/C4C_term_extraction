from enum import Enum, unique

from question_generator.questiongenerator import QuestionGenerator, print_qa

# TODO should we load this once, instead of with every call?
model_dir = None
QG = QuestionGenerator(
    model_dir
)


@unique
class AnswerStyle(Enum):
    """
    The desired type of answers. Choose from ['all', 'sentences', 'multiple_choice']
    """
    ALL = "all"
    SENTENCES = "sentences"
    MULTIPLE_CHOICE = "multiple_choice"


def main(text: str,
         # model_dir=None, # TODO
         num_questions: int = 10,
         answer_style: AnswerStyle = AnswerStyle.ALL.value,
         use_qa_eval: bool = True,
         show_answers: bool = True
         ):
    """ Question generation method

    :param text:
        Text to extract questions from.
    :param model_dir:
        "The folder that the trained model checkpoints are in."
    :param num_questions: (optional)
        The desired number of questions to generate.
    :param answer_style: (optional)
    :param use_qa_eval: (optional)
        Whether or not you want the generated questions to be filtered for quality. Choose from ['True', 'False']",
    :return:
    """

    qa_list = QG.generate(
        text,
        num_questions=int(num_questions),
        answer_style=answer_style,
        use_evaluator=use_qa_eval
    )
    print_qa(qa_list, show_answers=show_answers)
    print(qa_list)

    return qa_list
