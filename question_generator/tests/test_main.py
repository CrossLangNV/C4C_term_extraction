from question_generator.scripts import generate_question_from_text

if __name__ == '__main__':
    text_file = "and I just walk 500  miles and I just walk 500 more and so on. I can't believe you just hit me!"

    generate_question_from_text.main(text_file)
