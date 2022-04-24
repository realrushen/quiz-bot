import logging
import pathlib
from itertools import tee, chain, zip_longest, islice

logger = logging.getLogger(__name__)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

QUIZ_DIRECTORY = pathlib.Path().cwd().parent / 'quiz-questions'


def grouper(iterable, n, *, incomplete='fill', fillvalue=None):
    "Collect data into non-overlapping fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, fillvalue='x') --> ABC DEF Gxx
    # grouper('ABCDEFG', 3, incomplete='strict') --> ABC DEF ValueError
    # grouper('ABCDEFG', 3, incomplete='ignore') --> ABC DEF
    args = [iter(iterable)] * n
    if incomplete == 'fill':
        return zip_longest(*args, fillvalue=fillvalue)
    if incomplete == 'strict':
        return zip(*args, strict=True)
    if incomplete == 'ignore':
        return zip(*args)
    else:
        raise ValueError('Expected fill, strict, or ignore')


def flatten(list_of_lists):
    """Flatten one level of nesting"""
    return chain.from_iterable(list_of_lists)


def scan_files(directory: pathlib.Path):
    all_questions_with_answers = []
    files_scanned = 0
    total_questions = 0
    for file in directory.iterdir():
        logger.info('reading file %s', file.name)
        file_contents = file.read_text(encoding='koi8-r')

        # extract questions and answers
        questions_with_answers = [
            entry for entry in file_contents.split('\n\n')
            if ('Вопрос' in entry) or ('Ответ:' in entry)
        ]

        pairs = list(grouper(questions_with_answers, 2))

        # drop questions with images and tags
        questions_with_answers_without_pics_and_tags = filter(
            lambda pair: ('(pic:' not in pair[0]) and ('</' not in pair[0]),
            pairs,
        )

        # drop None if exists
        questions_with_answers_without_pics_and_tags = [
            item for item in flatten(questions_with_answers_without_pics_and_tags)
            if item
        ]
        logger.info('found %d questions with answers', len(questions_with_answers_without_pics_and_tags))
        all_questions_with_answers.extend(questions_with_answers_without_pics_and_tags)

        files_scanned += 1
        total_questions += len(questions_with_answers_without_pics_and_tags) / 2

    logger.info('scanned %d files and %d questions', files_scanned, total_questions)
    return all_questions_with_answers


def main():
    all_questions_with_answers = scan_files(QUIZ_DIRECTORY)

    pathlib.Path('quiz.txt').write_text('\n\n'.join(all_questions_with_answers), encoding='utf-8')


if __name__ == '__main__':
    main()
