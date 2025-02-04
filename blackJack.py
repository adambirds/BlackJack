import random, pygame, sys
from os import path
from cardClasses import *
from char import Character, Player, Dealer
import config 
from buttons import *
#random.seed()
seed = random.randrange(sys.maxsize)
rng = random.seed(1130654034904112621)
print("Seed was:", seed)

class TheGame():

    def __init__(self, screen, main_player: Player):
        self.screen = screen

        #------------------------------------------------------------------------------------	
        #Load pictures
        table_img = pygame.image.load(path.join(config.IMG_DIR,"black_jack_table.png")).convert_alpha()
        self.table = pygame.transform.scale(table_img,(config.WIDTH, config.HEIGHT))
        #Creates the 8 decks each deck holds 52 Card(). Totalling 416 cards. The holder is pre shuffled.
        self.main_deck = Deck_holder()
        self.main_deck.create_multi_decks(6)
        self.main_deck.shuffle_holder()
        self.starting_cards = 2
        #player attributes 
        self.main_player = main_player
        #dealer attributes
        self.the_dealer = Dealer()
        #images and button attributes
        self.btn_imgs = []
        coin_img = pygame.image.load(os.path.join(config.IMG_DIR,"coin.png")).convert_alpha()
        self.coin_img = pygame.transform.scale(coin_img,(config.COIN_X, config.COIN_Y))
        self.card_images = CardImages()
        self.create_buttons()
        self.need_back = False
        self.frame = 0

    #deal one card to each player in the self.total_player list
    def deal_table(self):
        
        self.need_back = True
        self.reset_hand()
        print (self.main_player.bet)
        self.hit(self.main_player)
        self.hit(self.the_dealer)
        self.hit(self.main_player)
        self.hit(self.the_dealer)
        print (f"the player has {self.main_player.get_total()}")
        print (f"the dealer has {self.the_dealer.get_total()}")
        self.deal_btn.set_active(False)
        self.stand_btn.set_active(True)
        self.hit_btn.set_active(True)
    
    def get_card_coords(self, card_position: int, player: Character) -> tuple[int, int]:
        if player == self.main_player:
            if card_position == 1:
                return (235, 496)
            else:
                x = card_position - 2
                return (317+(30*x),496-(30*x)) 
        elif player == self.the_dealer:
            if card_position == 1:
                return (235,137)
            else:
                x = card_position - 2
                return (317+(30*x),137+(30*x)) 
        else:
            return (0,0)
    
    def reset_hand(self):
        
        self.main_player.reset()
        self.the_dealer.reset()
    
    def hit(self, person: Character):
        """Hit the given person."""#crypto docstring
        if not person.bust:
            x, y = self.get_card_coords(len(person.hand)+1,person)
            person.hit(self.main_deck, x, y)
            print (f"{person.name} has {person.get_total()}")
    
    def stand(self):   
        
        self.need_back = False
        #returns true if dealer has 17 - 21
        if self.main_player.check_blackjack():
            self.main_player.calc_win()
            print ("yeah you have black jack")
        elif self.the_dealer.check_for_stand() or self.main_player.check_bust():
            self.check_result()
            print("Second if")
        else:
            while not self.the_dealer.bust and not self.the_dealer.check_for_stand():
                self.hit(self.the_dealer)
                self.the_dealer.show_cards()
            self.check_result()
            
        self.stand_btn.set_active(False)
        self.hit_btn.set_active(False)
    

    
    #checks player score to the dealers score
    #calculates the bet return.
    def check_result(self):
        if self.main_player.check_bust():
            self.main_player.lost()
        elif self.the_dealer.check_bust():
            self.main_player.calc_win()
        elif self.main_player.total > self.the_dealer.total:
            self.main_player.calc_win()
        elif self.main_player.total < self.the_dealer.total:
            self.main_player.lost()
        else:
            self.main_player.draw()
        self.deal_btn.set_active(True)
       

    def create_buttons(self):
        btn_dict = generate_button_images()
        BTN_START_X = 100
        BTN_START_Y = 600
        
        def hit_main_player():
            self.hit(self.main_player)
        
        def player_place_bet():
            self.main_player.set_bet()
            print (self.main_player.bet)

        self.bet_btn = Buttons(player_place_bet, btn_dict["bet_grey"],btn_dict["bet_up"], btn_dict["bet_down"], BTN_START_X, BTN_START_Y)
        self.btn_imgs.append(self.bet_btn)
        self.deal_btn = Buttons(self.deal_table, btn_dict["deal_grey"],btn_dict["deal_up"], btn_dict["deal_down"], BTN_START_X+100, BTN_START_Y)
        self.btn_imgs.append(self.deal_btn)
        self.hit_btn = Buttons(hit_main_player, btn_dict["hit_grey"],btn_dict["hit_up"], btn_dict["hit_down"], BTN_START_X+200, BTN_START_Y, False)
        self.btn_imgs.append(self.hit_btn)
        self.stand_btn = Buttons(self.stand, btn_dict["stand_grey"],btn_dict["stand_up"], btn_dict["stand_down"], BTN_START_X+300, BTN_START_Y, False)
        self.btn_imgs.append(self.stand_btn)

    def draw_bet (self):
        if self.main_player.bet_made:
            self.table.blit(self.coin_img,(100,520)) 

    def draw_all_graphics(self):
        self.screen.blit(self.table,(0,0))
        self.main_deck.draw_deck(self.table, (105, 270))
        self.draw_bet()
        for btn in self.btn_imgs:
            btn.draw_button(self.table)
        self.draw_hand_cards(self.main_player.hand)
        self.draw_hand_cards(self.the_dealer.hand)
    
    def draw_back_card(self, x, y):
        CardImages().draw_card_back(x,y,self.table)

    #@param hand_list needs to hold Card() objects
    #loops through CardImage().draw_card to blit card to screen 
    def draw_hand_cards(self, hand_list):
        if hand_list == self.the_dealer.hand and self.need_back:
            self.draw_back_card(235,137)
            self.card_images.draw_card(self.screen,hand_list[1])   
        else:
            for card in hand_list:
                self.card_images.draw_card(self.screen, card)
            
    def event_handler_on_click (self):
        for btn in self.btn_imgs:
            if btn.check_collide(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                btn.click()

    def reset_buttons(self):
        for btn in self.btn_imgs:
            btn.reset_image()
        

def main():
    pygame.init()

    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption("Black Jack")
    clock = pygame.time.Clock()
    config.IMG_DIR = path.join(path.dirname(__file__), 'images')

    player = Player("Phil")
    game = TheGame(screen, player)
    player.show_cards()
    print(player.get_total())
    print("")
    game.the_dealer.show_cards()
    print (game.the_dealer.get_total())


    running = True
    #--------------------------------------------------------------------------
    #main game loop
    while running:

        clock.tick(config.FPS)
        for event in pygame.event.get():
            
            # Check for closing window
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #print (pygame.mouse.get_pos())
                if pygame.mouse.get_pressed() == (1,0,0): 
                    game.event_handler_on_click()
            elif event.type == pygame.MOUSEBUTTONUP:
                game.reset_buttons()
               
        
        screen.fill(config.BLACK)
        game.draw_all_graphics()
        
        pygame.display.update()


    pygame.quit()	

if __name__ == "__main__":
    main()