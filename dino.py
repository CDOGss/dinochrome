import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Dino Streamlit", page_icon="🦖")

st.title("🦖 Le Jeu du T-Rex - Version Complète")
st.write("Cliquez sur le jeu ci-dessous. Utilisez la touche **Espace** ou **Flèche Haut** pour sauter, et **Flèche Bas** pour vous baisser !")

# Code HTML/JS/CSS du jeu complet
code_jeu_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; display: flex; justify-content: center; align-items: center; background-color: #f0f2f6; font-family: sans-serif; }
        canvas { background-color: white; border: 2px solid #333; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); border-radius: 5px; outline: none; }
    </style>
</head>
<body>
    <div>
        <canvas id="gameCanvas" width="800" height="400" tabindex="1"></canvas>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        
        canvas.focus();
        canvas.addEventListener('click', () => canvas.focus());

        // Paramètres du jeu
        const HAUTEUR = canvas.height;
        const LARGEUR = canvas.width;
        const SOL = HAUTEUR - 20;

        // Variables Dino
        const dinoNormal = { w: 40, h: 60 };
        const dinoBaisse = { w: 55, h: 30 };
        let dino = { 
            x: 50, 
            y: SOL - 60, 
            w: dinoNormal.w, 
            h: dinoNormal.h, 
            vitesseY: 0, 
            gravite: 0.8, 
            enSaut: false, 
            enBaisse: false 
        };

        // Variables de partie
        let obstacles = [];
        let score = 0;
        let vitesseJeu = 3.0;
        const vitesseMax = 18.0;
        const acceleration = 0.003;
        let frames = 0;
        let enCours = true;

        // Contrôles (Appui)
        canvas.addEventListener("keydown", function(event) {
            if (["Space", "ArrowUp", "ArrowDown"].includes(event.code)) {
                event.preventDefault(); // Empêche le défilement de la page
            }
            if (!enCours && (event.code === "Space" || event.code === "ArrowUp")) {
                reinitialiserJeu();
                return;
            }
            if (enCours) {
                if ((event.code === "Space" || event.code === "ArrowUp") && !dino.enSaut && !dino.enBaisse) {
                    dino.vitesseY = -15;
                    dino.enSaut = true;
                }
                if (event.code === "ArrowDown" && !dino.enSaut) {
                    dino.enBaisse = true;
                    dino.w = dinoBaisse.w;
                    dino.h = dinoBaisse.h;
                    dino.y = SOL - dino.h;
                }
            }
        });

        // Contrôles (Relâchement)
        canvas.addEventListener("keyup", function(event) {
            if (event.code === "ArrowDown") {
                dino.enBaisse = false;
                dino.w = dinoNormal.w;
                dino.h = dinoNormal.h;
                dino.y = SOL - dino.h;
            }
        });

        function reinitialiserJeu() {
            dino = { x: 50, y: SOL - 60, w: dinoNormal.w, h: dinoNormal.h, vitesseY: 0, gravite: 0.8, enSaut: false, enBaisse: false };
            obstacles = [];
            score = 0;
            vitesseJeu = 7.0;
            frames = 0;
            enCours = true;
            boucleJeu();
        }

        function detecterCollision(rect1, rect2) {
            // Hitbox légèrement réduite pour être moins punitif
            const marge = 5;
            return (
                rect1.x + marge < rect2.x + rect2.w &&
                rect1.x + rect1.w - marge > rect2.x &&
                rect1.y + marge < rect2.y + rect2.h &&
                rect1.y + rect1.h - marge > rect2.y
            );
        }

        function boucleJeu() {
            if (!enCours) return;

            // --- PHYSIQUE DU DINO ---
            dino.vitesseY += dino.gravite;
            dino.y += dino.vitesseY;

            if (dino.y >= SOL - dino.h) {
                dino.y = SOL - dino.h;
                dino.vitesseY = 0;
                dino.enSaut = false;
            }

            // --- VITESSE GLOBALE ---
            if (vitesseJeu < vitesseMax) {
                vitesseJeu += acceleration;
            }

            // --- GESTION DES OBSTACLES ---
            frames++;
            let limiteApparition = Math.floor(120 / (vitesseJeu / 5)); // Les obstacles apparaissent plus vite avec la vitesse

            if (frames > limiteApparition + Math.random() * 50) {
                // S'il y a assez de score, 30% de chance d'avoir un oiseau
                if (score > 200 && Math.random() < 0.3) {
                    let hauteursPtera = [HAUTEUR - 110, HAUTEUR - 65, HAUTEUR - 40];
                    let hauteurChoisie = hauteursPtera[Math.floor(Math.random() * hauteursPtera.length)];
                    obstacles.push({ type: "ptera", x: LARGEUR, y: hauteurChoisie, w: 40, h: 30 });
                } else {
                    let hauteurCactus = 30 + Math.random() * 40;
                    obstacles.push({ type: "cactus", x: LARGEUR, y: SOL - hauteurCactus, w: 20, h: hauteurCactus });
                }
                frames = 0;
            }

            for (let i = obstacles.length - 1; i >= 0; i--) {
                let obs = obstacles[i];
                obs.x -= vitesseJeu;
                
                // Les ptérodactyles sont un peu plus rapides
                if (obs.type === "ptera") obs.x -= 1;

                // Suppression et score
                if (obs.x + obs.w < 0) {
                    obstacles.splice(i, 1);
                    score += 10;
                }

                // Collision
                if (detecterCollision(dino, obs)) {
                    enCours = false;
                }
            }

            // --- DESSIN ---
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Ligne du sol
            ctx.beginPath();
            ctx.moveTo(0, SOL);
            ctx.lineTo(LARGEUR, SOL);
            ctx.strokeStyle = "black";
            ctx.lineWidth = 2;
            ctx.stroke();

            // Dessin Dino (Bleu si baissé, Noir sinon)
            ctx.fillStyle = dino.enBaisse ? "#0000C8" : "#000000";
            ctx.fillRect(dino.x, dino.y, dino.w, dino.h);

            // Dessin Obstacles
            obstacles.forEach(obs => {
                if (obs.type === "cactus") {
                    ctx.fillStyle = "#228B22"; // Vert
                    ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
                } else {
                    ctx.fillStyle = "#C80000"; // Rouge
                    ctx.fillRect(obs.x, obs.y, obs.w, obs.h);
                }
            });

            // Textes (Score et Vitesse)
            ctx.fillStyle = "black";
            ctx.font = "bold 20px Arial";
            ctx.fillText("Score: " + Math.floor(score), 20, 30);
            ctx.font = "16px Arial";
            ctx.fillText("Vitesse: " + Math.floor(vitesseJeu), 20, 55);

            // Écran de fin
            if (!enCours) {
                ctx.fillStyle = "black";
                ctx.font = "bold 30px Arial";
                ctx.fillText("Game Over !", LARGEUR / 2 - 90, HAUTEUR / 2 - 20);
                ctx.font = "20px Arial";
                ctx.fillText("Appuyez sur ESPACE pour rejouer", LARGEUR / 2 - 160, HAUTEUR / 2 + 20);
            } else {
                requestAnimationFrame(boucleJeu);
            }
        }

        // Lancement initial
        boucleJeu();
    </script>
</body>
</html>
"""

components.html(code_jeu_html, height=450)
