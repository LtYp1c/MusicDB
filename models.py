from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

# 创建独立的db实例
db = SQLAlchemy()

class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)                        # 主键约束
    username = db.Column(db.String(80), unique=True, nullable=False)    # 非空约束
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), 
                           onupdate=datetime.now(timezone.utc))
    
    # 关联关系
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade='all, delete-orphan')
    playlists = db.relationship('Playlist', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'role': getattr(self, 'role', None),
            'favorites_count': len(self.favorites) if self.favorites is not None else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Singer(db.Model):
    """歌手表"""
    __tablename__ = 'singers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    nationality = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # 关联关系
    albums = db.relationship('Album', backref='singer', lazy=True, cascade='all, delete-orphan')
    songs = db.relationship('Song', backref='singer', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'avatar': self.avatar,
            'description': self.description,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'nationality': self.nationality,
            'albums_count': len(self.albums) if self.albums is not None else 0,
            'songs_count': len(self.songs) if self.songs is not None else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Album(db.Model):
    """专辑表"""
    __tablename__ = 'albums'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    cover = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    release_date = db.Column(db.Date, nullable=True)
    singer_id = db.Column(db.Integer, db.ForeignKey('singers.id'), nullable=False)  # 外键约束
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), 
                           onupdate=datetime.now(timezone.utc))
    
    # 关联关系
    songs = db.relationship('Song', backref='album', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cover': self.cover,
            'description': self.description,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'singer_id': self.singer_id,
            'singer_name': self.singer.name if self.singer else None,
            'songs_count': len(self.songs) if self.songs is not None else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Song(db.Model):
    """歌曲表"""
    __tablename__ = 'songs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.Integer, nullable=True)  # 时长（秒）
    lyrics = db.Column(db.Text, nullable=True)
    release_date = db.Column(db.Date, nullable=True)
    singer_id = db.Column(db.Integer, db.ForeignKey('singers.id'), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('albums.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # 关联关系
    favorites = db.relationship('Favorite', backref='song', lazy=True, cascade='all, delete-orphan')
    song_genres = db.relationship('SongGenre', backref='song', lazy=True, cascade='all, delete-orphan')
    playlist_songs = db.relationship('PlaylistSong', backref='song', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        # 获取歌曲的流派信息
        genres = [sg.genre.name for sg in self.song_genres if sg.genre]
        
        return {
            'id': self.id,
            'name': self.name,
            'duration': self.duration,
            'lyrics': self.lyrics,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'singer_id': self.singer_id,
            'singer_name': self.singer.name if self.singer else None,
            'album_id': self.album_id,
            'album_name': self.album.name if self.album else None,
            'favorite_count': len(self.favorites) if self.favorites is not None else 0,
            'genres': genres,  # 添加流派信息
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Favorite(db.Model):
    """收藏表"""
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # 确保用户和歌曲组合的唯一性
    __table_args__ = (db.UniqueConstraint('user_id', 'song_id', name='unique_user_song'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'song_id': self.song_id,
            'song_name': self.song.name if self.song else None,
            'singer_name': self.song.singer.name if self.song and self.song.singer else None,
            'album_name': self.song.album.name if self.song and self.song.album else None,
            'username': self.user.username if self.user else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Genre(db.Model):
    """音乐流派表"""
    __tablename__ = 'genres'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # 关联关系
    songs = db.relationship('SongGenre', backref='genre', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'songs_count': len(self.songs) if self.songs is not None else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SongGenre(db.Model):
    """歌曲-流派关联表（多对多关系）"""
    __tablename__ = 'song_genres'
    
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # 确保歌曲和流派组合的唯一性
    __table_args__ = (db.UniqueConstraint('song_id', 'genre_id', name='unique_song_genre'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'song_id': self.song_id,
            'genre_id': self.genre_id,
            'song_name': self.song.name if self.song else None,
            'genre_name': self.genre.name if self.genre else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Playlist(db.Model):
    """播放列表表"""
    __tablename__ = 'playlists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    cover = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False)  # 是否公开
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # 关联关系
    playlist_songs = db.relationship('PlaylistSong', backref='playlist', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'cover': self.cover,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'is_public': self.is_public,
            'songs_count': len(self.playlist_songs) if self.playlist_songs is not None else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PlaylistSong(db.Model):
    """播放列表-歌曲关联表"""
    __tablename__ = 'playlist_songs'
    
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)  # 歌曲在播放列表中的顺序
    added_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # 确保播放列表和歌曲组合的唯一性
    __table_args__ = (db.UniqueConstraint('playlist_id', 'song_id', name='unique_playlist_song'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'playlist_id': self.playlist_id,
            'song_id': self.song_id,
            'order': self.order,
            'song_name': self.song.name if self.song else None,
            'singer_name': self.song.singer.name if self.song and self.song.singer else None,
            'added_at': self.added_at.isoformat() if self.added_at else None
        }