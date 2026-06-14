-- ════════════════════════════════════════════════════════════════
-- HealthAI Coach — Migration V3 : Mini-réseau social
-- Fichier  : V3__social_network.sql
-- Moteur   : PostgreSQL 16
-- Auteur   : MSPR Team
-- Date     : 2026
--
-- Nouvelles tables pour le mini-réseau social :
-- - posts       : Publications des utilisateurs
-- - comments    : Commentaires sur les posts
-- - likes       : Réactions de type "like"
-- - media       : Fichiers médias associés aux posts
--
-- Modifications :
-- - Ajout de champs au profil utilisateur (display_name, profile_photo_url, bio)
-- ════════════════════════════════════════════════════════════════


-- ─────────────────────────────────────────────────────────────────
-- MODIFICATION : TABLE users
-- Ajout des champs pour le mini-réseau social
-- ─────────────────────────────────────────────────────────────────
ALTER TABLE users ADD COLUMN IF NOT EXISTS display_name VARCHAR(150);
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_photo_url VARCHAR(500);
ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;


-- ─────────────────────────────────────────────────────────────────
-- TABLE : posts
-- Publications des utilisateurs
-- Champs : id, user_id, content, media_count, created_at, updated_at
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS posts (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Contenu principal
    content       TEXT NOT NULL,
    
    -- Métadonnées
    media_count   SMALLINT DEFAULT 0,
    
    -- Timestamps
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_posts_user_id    ON posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC);


-- ─────────────────────────────────────────────────────────────────
-- TABLE : media
-- Fichiers médias associés aux posts (photos, vidéos)
-- Gestion adaptée à l'environnement conteneurisé (MinIO, S3)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS media (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id       UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    
    -- Identité du fichier
    filename      VARCHAR(255) NOT NULL,
    file_type     VARCHAR(50) CHECK (file_type IN ('image', 'video', 'document')),
    mime_type     VARCHAR(100),
    file_size_kb  INTEGER,
    
    -- URL d'accès (MinIO, S3, ou stockage local)
    url           VARCHAR(500) NOT NULL,
    
    -- Métadonnées médias
    width_px      INTEGER,
    height_px     INTEGER,
    duration_sec  NUMERIC(8,2),      -- pour les vidéos
    
    -- Timestamps
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_media_post_id   ON media(post_id);
CREATE INDEX IF NOT EXISTS idx_media_file_type ON media(file_type);


-- ─────────────────────────────────────────────────────────────────
-- TABLE : comments
-- Commentaires sur les posts
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS comments (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id       UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Contenu du commentaire
    content       TEXT NOT NULL,
    
    -- Timestamps
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_comments_post_id   ON comments(post_id);
CREATE INDEX IF NOT EXISTS idx_comments_user_id   ON comments(user_id);
CREATE INDEX IF NOT EXISTS idx_comments_created_at ON comments(created_at DESC);


-- ─────────────────────────────────────────────────────────────────
-- TABLE : likes
-- Réactions de type "like" sur les posts
-- Contrainte UNIQUE pour éviter les doublons
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS likes (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id       UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Timestamps
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    
    -- Contrainte : un utilisateur ne peut liker qu'une fois le même post
    UNIQUE(post_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_likes_post_id ON likes(post_id);
CREATE INDEX IF NOT EXISTS idx_likes_user_id ON likes(user_id);


-- ─────────────────────────────────────────────────────────────────
-- TRIGGER : mise à jour automatique de updated_at sur posts
-- ─────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_posts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER posts_updated_at
    BEFORE UPDATE ON posts
    FOR EACH ROW EXECUTE FUNCTION update_posts_updated_at();


-- ─────────────────────────────────────────────────────────────────
-- TRIGGER : mise à jour automatique de updated_at sur comments
-- ─────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_comments_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER comments_updated_at
    BEFORE UPDATE ON comments
    FOR EACH ROW EXECUTE FUNCTION update_comments_updated_at();
