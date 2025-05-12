from random import choice , randint


def get_response(user_input: str) -> str:

    # if not user_input.startswith("$"):
    #     return ''
    
    # user_input = user_input[1:].strip()

    lowered:str = user_input.lower()

    if lowered == '':
        return 'Well You\'re awfully silent....'
    elif 'hello' in lowered:
        return 'Hello There!'
    elif 'how are you' in lowered:
        return 'I am doing well. how about you?'
    elif 'bye' in lowered:
        return 'Bye, hit me up if you need anything'
    elif 'roll dice' in lowered:
        return f'you rolled: {randint(1,6)}'
    elif 'bye' in lowered:
        return 'Bye, hit me up if you need anything'
    elif 'what do you think of esha?' in lowered:
        return choice(['Oh esha? isnt she a little kid?',
                       'hmmm that is a very interesting question. i would say she is a fun to play minecraft with',
                       'Yeah esha is a nice person , you shouldnt be so mean to her'])
    elif 'what time is it' in lowered:
        from datetime import datetime
        return f"The current time is {datetime.now().strftime('%H:%M:%S')}"
    elif 'flip a coin' in lowered:
        return f'You Got:{choice(["Heads","Tails"])}!'
    elif 'math' in lowered or 'solve' in lowered:
        try:
            result = eval(user_input.replace("solve","").replace("math","").strip())
            return f"The answer is {result}"
        except Exception as e:
            return "Sorry i couldnt solve that.. please try again"
    
    else:
        return choice(['I do not understand... i am in early stages of development so my communication is a work in progress',
                       'what are you talking about?.... i am in early stages of development so my communication is a work in progress',
                       'Do you mind rephrasing that?... i am in early stages of development so my communication is a work in progress'])