import telebot
import random
bot = telebot.TeleBot('6774580974:AAFhRc8R_PsKmtL-6lSISjjcSbO8oJ2138M')

def deal_the_cards():
    cards = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
    card = random.choice(cards)
    return card

# Раздать и пользователю и компу по 2 карты

def play_game():
    user_cards = []
    computer_cards = []
    game_over = False

    for _ in range(2):
        user_cards.append(deal_the_cards())
        computer_cards.append(deal_the_cards())

    # Теперь надо сложить те значения, что мы положили в список

    def calculate_score(cards):
        # Прописываем условие для туза, который может быть и 1 и 11
        if sum(cards) == 21 in cards and len(cards) == 2:
            return 0

        if 11 in cards and sum(cards) > 21:
        # То тогда мы должны заминусовать 11 и добавить 1
            cards.remove(11)
            cards.append(1)
        return sum(cards)

        # 13 Теперь задача у нас - сравнить получаемые данные

    def compare(user_score, computer_score):
        if user_score == computer_score:
            return "Ничья"
        elif computer_score == 0:
            return "Вы проиграли. Компьютер снова победил"
        elif user_score == 0:
            return "Победа."
        elif user_score > 21:
            return "Вы проиграли."
        elif computer_score > 21:
            return "Компьютер проиграл."
        elif user_score> computer_score:
            return "вы победили."
        else :
            return "вы проиграли."

        # 11 Теперь надо перепроверить количество карт и это может продолжаться ещё 9 раз

    while not game_over:
        # высчитываем сумму значений карт и если она равна 21 - заканчиваем игру.
        user_score = calculate_score(user_cards)
        comp_score = calculate_score(computer_cards)
        print(f'Ваши карты {user_cards} {computer_cards}')
        print(f'Первая карта компьютера {computer_cards[0]}, а вот ваше число {user_score}')

        if user_score == 0 or comp_score == 0 or user_score > 21:
            game_over = True
        else:
            user_deal = input("Введите Y(английская) чтобы взять дополнительную карту и введите N, чтобы посмотреть результаты: ")
            if user_deal == 'y':
                user_cards.append(deal_the_cards())
            else:
                game_over = True


    while comp_score != 0 and comp_score < 17:
        computer_cards.append(deal_the_cards())
        comp_score = calculate_score(computer_cards)

    # 14 тут вставляем последнюю функцию
    print(f"Ваши итоговые карты {user_cards} и ваш результат {user_score}")
    print(compare(user_score, comp_score))

while input("вы хотите сыграть снова? Просто введите Y или N: ") == 'y':
    
    play_game()
    # Теперь нам надо дать юзеру выбрать возможность продолжить игру и взять ещё карту или остановить игру и выявить победителя - добавляем цикл while

# После того, как мы взяли все карты - наступает время компьютера.
bot.polling(none_stop=True, interval=0)