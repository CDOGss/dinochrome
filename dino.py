import pygame
import random
import sys
import os

pygame.init()

# Dimensions de la fenêtre
LARGEUR = 800
HAUTEUR = 400
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Dino Chrome - Vitesse et Ptérodactyles")

BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ROUGE = (200, 0, 0) # Couleur de secours pour le ptérodactyle
BLEU = (0, 0, 200)  # Couleur de secours pour le dino baissé

FPS = 60
horloge = pygame.time.Clock()

# --- CHARGEMENT SÉCURISÉ DES IMAGES ---
images_actives = True
try:
    img_dino = pygame.transform.scale(pygame.image.load("dino.png").convert_alpha(), (40, 60))
    img_dino_baisse = pygame.transform.scale(pygame.image.load("dino_baisse.png").convert_alpha(), (55, 30))
    img_cactus_base = pygame.image.load("cactus.png").convert_alpha()
    img_ptera = pygame.transform.scale(pygame.image.load("ptera.png").convert_alpha(), (40, 30))
except FileNotFoundError:
    images_actives = False
    print("\n[ATTENTION] Images manquantes (dino_baisse.png, ptera.png, etc.).")
    print("Le jeu utilisera des blocs de couleur en attendant.\n")

class Dino:
    def __init__(self):
        self.largeur_normale = 40
        self.hauteur_normale = 60
        self.largeur_baisse = 55
        self.hauteur_baisse = 30
        
        self.largeur = self.largeur_normale
        self.hauteur = self.hauteur_normale
        self.x = 50
        self.y_sol = HAUTEUR - 20
        self.y = self.y_sol - self.hauteur
        
        self.vitesse_y = 0
        self.gravite = 0.8
        self.en_saut = False
        self.en_baisse = False

    def sauter(self):
        # On ne peut sauter que si on n'est pas déjà en l'air et qu'on n'est pas baissé
        if not self.en_saut and not self.en_baisse:
            self.vitesse_y = -15
            self.en_saut = True

    def baisser(self, etat):
        # On ne peut se baisser que si on est au sol
        if not self.en_saut:
            self.en_baisse = etat
            if self.en_baisse:
                self.hauteur = self.hauteur_baisse
                self.largeur = self.largeur_baisse
            else:
                self.hauteur = self.hauteur_normale
                self.largeur = self.largeur_normale
            
            # Ajuster la position Y pour rester collé au sol
            self.y = self.y_sol - self.hauteur

    def mettre_a_jour(self):
        self.vitesse_y += self.gravite
        self.y += self.vitesse_y

        if self.y >= self.y_sol - self.hauteur:
            self.y = self.y_sol - self.hauteur
            self.vitesse_y = 0
            self.en_saut = False

    def dessiner(self, surface):
        if images_actives:
            image_actuelle = img_dino_baisse if self.en_baisse else img_dino
            surface.blit(image_actuelle, (self.x, self.y))
        else:
            couleur = BLEU if self.en_baisse else NOIR
            pygame.draw.rect(surface, couleur, (self.x, self.y, self.largeur, self.hauteur))

    def get_rect(self):
        # On réduit légèrement la hitbox (boîte de collision) pour que le jeu soit moins punitif
        return pygame.Rect(self.x + 5, self.y + 5, self.largeur - 10, self.hauteur - 10)

class Obstacle:
    def __init__(self, type_obstacle):
        self.type = type_obstacle
        self.x = LARGEUR
        
        if self.type == "cactus":
            self.hauteur = random.randint(30, 70)
            self.largeur = 20
            self.y = HAUTEUR - 20 - self.hauteur
            if images_actives:
                self.image = pygame.transform.scale(img_cactus_base, (self.largeur, self.hauteur))
                
        elif self.type == "ptera":
            self.largeur = 40
            self.hauteur = 30
            # Le ptérodactyle peut apparaître à 3 hauteurs : haut, moyen (nécessite de se baisser), bas (nécessite de sauter)
            hauteurs_possibles = [HAUTEUR - 110, HAUTEUR - 65, HAUTEUR - 40]
            self.y = random.choice(hauteurs_possibles)
            if images_actives:
                self.image = img_ptera

    def mettre_a_jour(self, vitesse_jeu):
        # L'obstacle recule à la vitesse globale du jeu
        self.x -= vitesse_jeu
        
        # Les ptérodactyles volent un peu plus vite que les cactus
        if self.type == "ptera":
             self.x -= 1 

    def dessiner(self, surface):
        if images_actives:
            surface.blit(self.image, (self.x, self.y))
        else:
            couleur = NOIR if self.type == "cactus" else ROUGE
            pygame.draw.rect(surface, couleur, (self.x, self.y, self.largeur, self.hauteur))
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.largeur, self.hauteur)

def jeu():
    dino = Dino()
    obstacles = []
    score = 0
    
    # --- GESTION DE LA VITESSE ---
    vitesse_jeu = 7.0 
    vitesse_max = 18.0
    acceleration = 0.003 # La vitesse augmente un tout petit peu à chaque image
    
    font = pygame.font.SysFont(None, 36)
    compteur_apparition = 0
    en_cours = True

    while en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Quand on APPUIE sur une touche
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    dino.sauter()
                if event.key == pygame.K_DOWN:
                    dino.baisser(True)
                    
            # Quand on RELÂCHE une touche
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    dino.baisser(False)

        # Mise à jour du dinosaure
        dino.mettre_a_jour()

        # Augmentation progressive de la vitesse globale
        if vitesse_jeu < vitesse_max:
            vitesse_jeu += acceleration

        # Génération aléatoire des obstacles (qui dépend maintenant de la vitesse)
        compteur_apparition += 1
        # Plus le jeu va vite, plus les obstacles doivent apparaître rapidement
        limite_apparition = random.randint(int(600/vitesse_jeu), int(1200/vitesse_jeu))
        
        if compteur_apparition > limite_apparition:
            # S'il y a assez de score, on a 30% de chance d'avoir un oiseau, 70% un cactus
            if score > 200 and random.randint(1, 100) <= 30:
                obstacles.append(Obstacle("ptera"))
            else:
                obstacles.append(Obstacle("cactus"))
            compteur_apparition = 0

        # Mise à jour et nettoyage des obstacles
        for obs in obstacles:
            obs.mettre_a_jour(vitesse_jeu)
            if obs.x < -obs.largeur:
                obstacles.remove(obs)
                score += 10 

        # Vérification des collisions
        dino_rect = dino.get_rect()
        for obs in obstacles:
            if dino_rect.colliderect(obs.get_rect()):
                en_cours = False 

        # Dessin
        ecran.fill(BLANC)
        pygame.draw.line(ecran, NOIR, (0, HAUTEUR - 20), (LARGEUR, HAUTEUR - 20), 2)
        
        dino.dessiner(ecran)
        for obs in obstacles:
            obs.dessiner(ecran)

        # Affichage du score
        texte_score = font.render(f"Score: {int(score)}  |  Vitesse: {int(vitesse_jeu)}", True, NOIR)
        ecran.blit(texte_score, (10, 10))

        pygame.display.flip()
        horloge.tick(FPS)

    # Écran de fin
    texte_fin = font.render("Game Over ! Appuyez sur ESPACE pour rejouer", True, NOIR)
    ecran.blit(texte_fin, (LARGEUR//2 - 270, HAUTEUR//2))
    pygame.display.flip()
    
    attente = True
    while attente:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                jeu()

if __name__ == "__main__":
    jeu()