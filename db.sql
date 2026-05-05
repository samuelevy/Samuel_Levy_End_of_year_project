
-- User table. Every user gets a random id; every user gets a role.
CREATE TABLE app_user (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  name    VARCHAR(100) NOT NULL,
  role    VARCHAR(10)  NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  CONSTRAINT chk_app_user_role
    CHECK (role IN ('ADMIN','PLAYER'))
);

-- Subclasses of user, Player and Admin. 
-- "TRIES" is an experimental value set to 0 for now, and used for later implementation 
CREATE TABLE player (
  user_id INT PRIMARY KEY,
  elo      DECIMAL(10,3),
  glicko   DECIMAL(10,3),
  glicko_rd DECIMAL(10,3) DEFAULT 350 NOT NULL,  -- rating deviation RD
  volatility DECIMAL(10,5) DEFAULT 0.06 NOT NULL, 
  `tries` INT DEFAULT 0 NOT NULL,
  gamecount BIGINT DEFAULT 0 NOT NULL,
  last_game_date DATETIME, -- might be useful to update RD.
  CONSTRAINT fk_player_user
    FOREIGN KEY (user_id) REFERENCES app_user(user_id)
);

CREATE TABLE admin_user (
  user_id INT PRIMARY KEY,
  CONSTRAINT fk_admin_user
    FOREIGN KEY (user_id) REFERENCES app_user(user_id)
);

-- Enforce that any ADMIN_USER row truly belongs to a user with role='ADMIN'
DELIMITER $$

CREATE TRIGGER trg_admin_role_chk
BEFORE INSERT ON admin_user
FOR EACH ROW
BEGIN
  DECLARE v_role VARCHAR(10);

  SELECT role INTO v_role
  FROM app_user
  WHERE user_id = NEW.user_id;

  IF v_role <> 'ADMIN' THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'User must have role ADMIN to appear in ADMIN_USER.';
  END IF;
END$$

DELIMITER ;

-- Table competition for tournaments and bog set of games
CREATE TABLE competition (
  comp_id INT AUTO_INCREMENT PRIMARY KEY,
  setting VARCHAR(100),
  num_players INT NOT NULL
);

-- Game: a heap storing all of the game history to be able to access it.
-- The basic elo and glicko algorithm will not need this, and this will stay unused
-- until we can put the experimental feature in.
CREATE TABLE game (
  game_id INT AUTO_INCREMENT PRIMARY KEY,
  player1 INT NOT NULL,
  player2 INT NOT NULL,
  outcome INT,             -- FK to the winning player; NULL allowed for draw/unknown
  played_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,

  CONSTRAINT fk_game_p1
    FOREIGN KEY (player1) REFERENCES player(user_id),
  CONSTRAINT fk_game_p2
    FOREIGN KEY (player2) REFERENCES player(user_id),
  CONSTRAINT fk_game_outcome
    FOREIGN KEY (outcome) REFERENCES player(user_id),

  CONSTRAINT chk_game_players_distinct
    CHECK (player1 <> player2),

  CONSTRAINT chk_game_outcome_participant
    CHECK ( outcome IS NULL OR outcome IN (player1, player2) )
);

-- Helpful indexes for common queries
CREATE INDEX idx_game_p1       ON game(player1);
CREATE INDEX idx_game_p2       ON game(player2);
CREATE INDEX idx_game_outcome  ON game(outcome);
CREATE INDEX idx_game_playedat ON game(played_at);

-- Now for normalisation purposes we need a table to link game and competition.
CREATE TABLE competition_game (
  comp_id INT NOT NULL,
  game_id INT NOT NULL,
  CONSTRAINT pk_competition_game PRIMARY KEY (comp_id, game_id),
  CONSTRAINT fk_competition_game_comp
    FOREIGN KEY (comp_id) REFERENCES competition(comp_id),
  CONSTRAINT fk_competition_game_game
    FOREIGN KEY (game_id) REFERENCES game(game_id)
);
