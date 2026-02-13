from flask import Blueprint, request, jsonify
from models import db, User, Singer, Album, Song, Favorite, Genre, SongGenre, Playlist, PlaylistSong
from datetime import datetime
import hashlib

# 创建蓝图
api = Blueprint('api', __name__)

# 密码加密函数
def hash_password(password):
    """使用MD5加密密码"""
    return hashlib.md5(password.encode()).hexdigest()

# ========== 认证相关API ==========
@api.route('/login', methods=['POST'])
def login():
    """用户登录，校验账号密码和角色，返回用户基本信息与角色"""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')  # 默认为普通用户
    
    if not username or not password:
        return jsonify({'error': '用户名和密码是必需的'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or user.password != hash_password(password):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    # 验证用户角色是否匹配
    user_role = getattr(user, 'role', 'user')
    if user_role != role:
        return jsonify({'error': '角色不匹配，请选择正确的身份登录'}), 401

    # 返回最小必要信息
    return jsonify({
        'id': user.id,
        'username': user.username,
        'role': user_role
    })

# ========== 用户相关API ==========
@api.route('/users', methods=['GET'])
def get_users():
    """获取所有用户（排除管理员用户）"""
    users = User.query.filter(User.role != 'admin').all()
    return jsonify([user.to_dict() for user in users])

@api.route('/users', methods=['POST'])
def create_user():
    """创建新用户"""
    data = request.get_json()
    
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已被使用'}), 400
    
    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email'],
        password=hash_password(data['password']),
        avatar=data.get('avatar', '')
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@api.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取特定用户"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@api.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户信息"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # 更新用户信息
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    if 'password' in data:
        user.password = hash_password(data['password'])
    user.avatar = data.get('avatar', user.avatar)
    user.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(user.to_dict())

@api.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': '用户删除成功'})

# ========== 歌手相关API ==========
@api.route('/singers', methods=['GET'])
def get_singers():
    """获取所有歌手"""
    singers = Singer.query.all()
    return jsonify([singer.to_dict() for singer in singers])

@api.route('/singers', methods=['POST'])
def create_singer():
    """创建新歌手"""
    data = request.get_json()
    
    singer = Singer(
        name=data['name'],
        avatar=data.get('avatar', ''),
        description=data.get('description', ''),
        birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date() if data.get('birth_date') else None,
        nationality=data.get('nationality', '')
    )
    
    db.session.add(singer)
    db.session.commit()
    
    return jsonify(singer.to_dict()), 201

@api.route('/singers/<int:singer_id>', methods=['GET'])
def get_singer(singer_id):
    """获取特定歌手"""
    singer = Singer.query.get_or_404(singer_id)
    return jsonify(singer.to_dict())

@api.route('/singers/<int:singer_id>', methods=['PUT'])
def update_singer(singer_id):
    """更新歌手信息"""
    singer = Singer.query.get_or_404(singer_id)
    data = request.get_json()
    
    singer.name = data.get('name', singer.name)
    singer.avatar = data.get('avatar', singer.avatar)
    singer.description = data.get('description', singer.description)
    if 'birth_date' in data and data['birth_date']:
        singer.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
    singer.nationality = data.get('nationality', singer.nationality)
    singer.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(singer.to_dict())

@api.route('/singers/<int:singer_id>', methods=['DELETE'])
def delete_singer(singer_id):
    """删除歌手"""
    singer = Singer.query.get_or_404(singer_id)
    db.session.delete(singer)
    db.session.commit()
    return jsonify({'message': '歌手删除成功'})

# ========== 专辑相关API ==========
@api.route('/albums', methods=['GET'])
def get_albums():
    """获取所有专辑"""
    albums = Album.query.all()
    return jsonify([album.to_dict() for album in albums])

@api.route('/albums', methods=['POST'])
def create_album():
    """创建新专辑"""
    data = request.get_json()
    
    album = Album(
        name=data['name'],
        cover=data.get('cover', ''),
        description=data.get('description', ''),
        release_date=datetime.strptime(data['release_date'], '%Y-%m-%d').date() if data.get('release_date') else None,
        singer_id=data['singer_id']
    )
    
    db.session.add(album)
    db.session.commit()
    
    return jsonify(album.to_dict()), 201

@api.route('/albums/<int:album_id>', methods=['GET'])
def get_album(album_id):
    """获取特定专辑"""
    album = Album.query.get_or_404(album_id)
    return jsonify(album.to_dict())

@api.route('/albums/<int:album_id>', methods=['PUT'])
def update_album(album_id):
    """更新专辑信息"""
    album = Album.query.get_or_404(album_id)
    data = request.get_json()
    
    album.name = data.get('name', album.name)
    album.cover = data.get('cover', album.cover)
    album.description = data.get('description', album.description)
    if 'release_date' in data and data['release_date']:
        album.release_date = datetime.strptime(data['release_date'], '%Y-%m-%d').date()
    album.singer_id = data.get('singer_id', album.singer_id)
    album.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(album.to_dict())

@api.route('/albums/<int:album_id>', methods=['DELETE'])
def delete_album(album_id):
    """删除专辑"""
    album = Album.query.get_or_404(album_id)
    db.session.delete(album)
    db.session.commit()
    return jsonify({'message': '专辑删除成功'})

# ========== 歌曲相关API ==========
@api.route('/songs', methods=['GET'])
def get_songs():
    """获取所有歌曲"""
    songs = Song.query.all()
    return jsonify([song.to_dict() for song in songs])

@api.route('/songs', methods=['POST'])
def create_song():
    """创建新歌曲"""
    data = request.get_json()
    
    if not data.get('name') or not data.get('singer_id'):
        return jsonify({'error': '歌曲名称和歌手ID是必需的'}), 400
    
    # 检查歌曲名称是否已存在
    if Song.query.filter_by(name=data['name']).first():
        return jsonify({'error': '该歌曲已存在'}), 400
    
    song = Song(
        name=data['name'],
        duration=data.get('duration'),
        lyrics=data.get('lyrics', ''),
        release_date=datetime.strptime(data['release_date'], '%Y-%m-%d').date() if data.get('release_date') else None,
        singer_id=data['singer_id'],
        album_id=data.get('album_id')
    )
    
    db.session.add(song)
    db.session.commit()
    
    # 处理流派关联
    if 'genre_ids' in data and data['genre_ids']:
        for genre_id in data['genre_ids']:
            # 检查流派是否存在
            genre = Genre.query.get(genre_id)
            if genre:
                # 检查是否已存在关联
                existing = SongGenre.query.filter_by(song_id=song.id, genre_id=genre_id).first()
                if not existing:
                    song_genre = SongGenre(song_id=song.id, genre_id=genre_id)
                    db.session.add(song_genre)
        
        db.session.commit()
    
    return jsonify(song.to_dict()), 201

@api.route('/songs/<int:song_id>', methods=['GET'])
def get_song(song_id):
    """获取特定歌曲"""
    song = Song.query.get_or_404(song_id)
    return jsonify(song.to_dict())

@api.route('/songs/<int:song_id>', methods=['PUT'])
def update_song(song_id):
    """更新歌曲信息"""
    song = Song.query.get_or_404(song_id)
    data = request.get_json()
    
    song.name = data.get('name', song.name)
    song.duration = data.get('duration', song.duration)
    song.lyrics = data.get('lyrics', song.lyrics)
    song.release_date = datetime.strptime(data['release_date'], '%Y-%m-%d').date() if data.get('release_date') else song.release_date
    song.singer_id = data.get('singer_id', song.singer_id)
    song.album_id = data.get('album_id', song.album_id)
    
    db.session.commit()
    
    # 处理流派关联更新
    if 'genre_ids' in data:
        # 删除现有的流派关联
        SongGenre.query.filter_by(song_id=song_id).delete()
        
        # 添加新的流派关联
        if data['genre_ids']:
            for genre_id in data['genre_ids']:
                # 检查流派是否存在
                genre = Genre.query.get(genre_id)
                if genre:
                    song_genre = SongGenre(song_id=song_id, genre_id=genre_id)
                    db.session.add(song_genre)
            
            db.session.commit()
    
    return jsonify(song.to_dict())

@api.route('/songs/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    """删除歌曲"""
    song = Song.query.get_or_404(song_id)
    db.session.delete(song)
    db.session.commit()
    return jsonify({'message': '歌曲删除成功'})

# ========== 收藏相关API ==========
@api.route('/favorites', methods=['GET'])
def get_favorites():
    """获取所有收藏记录"""
    favorites = Favorite.query.all()
    return jsonify([favorite.to_dict() for favorite in favorites])

@api.route('/favorites', methods=['POST'])
def create_favorite():
    """添加收藏"""
    data = request.get_json()
    
    # 检查是否已收藏
    existing = Favorite.query.filter_by(
        user_id=data['user_id'], 
        song_id=data['song_id']
    ).first()
    
    if existing:
        return jsonify({'error': '该歌曲已被收藏'}), 400
    
    favorite = Favorite(
        user_id=data['user_id'],
        song_id=data['song_id']
    )
    
    db.session.add(favorite)
    db.session.commit()
    
    return jsonify(favorite.to_dict()), 201

@api.route('/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    """删除收藏"""
    favorite = Favorite.query.get_or_404(favorite_id)
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'message': '收藏删除成功'})

@api.route('/favorites/user/<int:user_id>/song/<int:song_id>', methods=['DELETE'])
def delete_favorite_by_user_song(user_id, song_id):
    """根据用户ID和歌曲ID删除收藏"""
    favorite = Favorite.query.filter_by(user_id=user_id, song_id=song_id).first()
    if not favorite:
        return jsonify({'error': '收藏记录不存在'}), 404
    
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'message': '收藏删除成功'})

@api.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    """获取用户的收藏列表"""
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([favorite.to_dict() for favorite in favorites])

# ========== 数据统计API ==========
@api.route('/stats/overview', methods=['GET'])
def get_stats_overview():
    """获取系统概览统计"""
    from sqlalchemy import func
    
    # 基础统计
    user_count = User.query.count()
    singer_count = Singer.query.count()
    album_count = Album.query.count()
    song_count = Song.query.count()
    favorite_count = Favorite.query.count()
    playlist_count = Playlist.query.count()
    
    # 今日新增统计
    today = datetime.utcnow().date()
    today_users = User.query.filter(func.date(User.created_at) == today).count()
    today_songs = Song.query.filter(func.date(Song.created_at) == today).count()
    today_favorites = Favorite.query.filter(func.date(Favorite.created_at) == today).count()
    
    return jsonify({
        'basic_stats': {
            'users': user_count,
            'singers': singer_count,
            'albums': album_count,
            'songs': song_count,
            'favorites': favorite_count,
            'playlists': playlist_count
        },
        'today_stats': {
            'users': today_users,
            'songs': today_songs,
            'favorites': today_favorites
        }
    })

@api.route('/stats/top-singers', methods=['GET'])
def get_top_singers():
    """获取热门歌手排行榜（按收藏次数）"""
    from sqlalchemy import func
    
    top_singers = db.session.query(
        Singer.id,
        Singer.name,
        Singer.avatar,
        func.count(Favorite.id).label('favorite_count')
    ).outerjoin(Song, Singer.id == Song.singer_id)\
     .outerjoin(Favorite, Song.id == Favorite.song_id)\
     .group_by(Singer.id)\
     .order_by(func.count(Favorite.id).desc())\
     .limit(10)\
     .all()
    
    result = []
    for singer in top_singers:
        result.append({
            'id': singer.id,
            'name': singer.name,
            'avatar': singer.avatar,
            'favorite_count': singer.favorite_count or 0
        })
    
    return jsonify(result)

@api.route('/stats/top-songs', methods=['GET'])
def get_top_songs():
    """获取热门歌曲排行榜（按收藏次数）"""
    from sqlalchemy import func
    
    top_songs = db.session.query(
        Song.id,
        Song.name,
        Song.duration,
        Singer.name.label('singer_name'),
        Album.name.label('album_name'),
        func.count(Favorite.id).label('favorite_count')
    ).join(Singer, Song.singer_id == Singer.id)\
     .outerjoin(Album, Song.album_id == Album.id)\
     .outerjoin(Favorite, Song.id == Favorite.song_id)\
     .group_by(Song.id)\
     .order_by(func.count(Favorite.id).desc())\
     .limit(10)\
     .all()
    
    result = []
    for song in top_songs:
        result.append({
            'id': song.id,
            'name': song.name,
            'duration': song.duration,
            'singer_name': song.singer_name,
            'album_name': song.album_name,
            'favorite_count': song.favorite_count or 0
        })
    
    return jsonify(result)

@api.route('/stats/genre-distribution', methods=['GET'])
def get_genre_distribution():
    """获取音乐流派分布统计"""
    from sqlalchemy import func
    
    genre_stats = db.session.query(
        Genre.name,
        func.count(SongGenre.id).label('song_count')
    ).outerjoin(SongGenre, Genre.id == SongGenre.genre_id)\
     .group_by(Genre.id)\
     .order_by(func.count(SongGenre.id).desc())\
     .all()
    
    result = []
    for genre in genre_stats:
        result.append({
            'name': genre.name,
            'song_count': genre.song_count or 0
        })
    
    return jsonify(result)

@api.route('/stats/user-activity', methods=['GET'])
def get_user_activity():
    """获取用户活跃度统计"""
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # 获取最近7天的日期
    dates = []
    for i in range(6, -1, -1):
        date = (datetime.utcnow() - timedelta(days=i)).date()
        dates.append(date)
    
    # 查询每天的用户活跃度（收藏数量）
    activity_data = []
    for date in dates:
        favorites_count = Favorite.query.filter(func.date(Favorite.created_at) == date).count()
        activity_data.append({
            'date': date.isoformat(),
            'favorites': favorites_count
        })
    
    return jsonify(activity_data)

@api.route('/stats/singer-nationality', methods=['GET'])
def get_singer_nationality():
    """获取歌手国籍分布统计"""
    from sqlalchemy import func
    
    nationality_stats = db.session.query(
        Singer.nationality,
        func.count(Singer.id).label('singer_count')
    ).filter(Singer.nationality.isnot(None))\
     .group_by(Singer.nationality)\
     .order_by(func.count(Singer.id).desc())\
     .all()
    
    result = []
    for stat in nationality_stats:
        result.append({
            'nationality': stat.nationality,
            'singer_count': stat.singer_count
        })
    
    return jsonify(result)

# ========== 播放列表相关API ==========
@api.route('/playlists', methods=['GET'])
def get_playlists():
    """获取所有播放列表"""
    playlists = Playlist.query.all()
    return jsonify([playlist.to_dict() for playlist in playlists])

@api.route('/playlists', methods=['POST'])
def create_playlist():
    """创建播放列表"""
    data = request.get_json()
    
    # 检查必填字段
    if not data.get('name'):
        return jsonify({'error': '播放列表名称不能为空'}), 400
    
    # 检查用户是否存在
    user = User.query.get(data.get('user_id'))
    if not user:
        return jsonify({'error': '用户不存在'}), 400
    
    playlist = Playlist(
        name=data['name'],
        description=data.get('description', ''),
        cover=data.get('cover', ''),
        user_id=data['user_id'],
        is_public=data.get('is_public', False)
    )
    
    db.session.add(playlist)
    db.session.commit()
    
    return jsonify(playlist.to_dict()), 201

@api.route('/playlists/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    """获取特定播放列表"""
    playlist = Playlist.query.get_or_404(playlist_id)
    return jsonify(playlist.to_dict())

@api.route('/playlists/<int:playlist_id>', methods=['PUT'])
def update_playlist(playlist_id):
    """更新播放列表信息"""
    playlist = Playlist.query.get_or_404(playlist_id)
    data = request.get_json()
    
    playlist.name = data.get('name', playlist.name)
    playlist.description = data.get('description', playlist.description)
    playlist.cover = data.get('cover', playlist.cover)
    playlist.is_public = data.get('is_public', playlist.is_public)
    playlist.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(playlist.to_dict())

@api.route('/playlists/<int:playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    """删除播放列表"""
    playlist = Playlist.query.get_or_404(playlist_id)
    db.session.delete(playlist)
    db.session.commit()
    return jsonify({'message': '播放列表删除成功'})

@api.route('/users/<int:user_id>/playlists', methods=['GET'])
def get_user_playlists(user_id):
    """获取用户的播放列表"""
    playlists = Playlist.query.filter_by(user_id=user_id).all()
    return jsonify([playlist.to_dict() for playlist in playlists])

# ========== 播放列表歌曲管理API ==========
@api.route('/playlists/<int:playlist_id>/songs', methods=['GET'])
def get_playlist_songs(playlist_id):
    """获取播放列表中的歌曲"""
    playlist_songs = PlaylistSong.query.filter_by(playlist_id=playlist_id).order_by(PlaylistSong.order).all()
    return jsonify([playlist_song.to_dict() for playlist_song in playlist_songs])

@api.route('/playlists/<int:playlist_id>/songs', methods=['POST'])
def add_song_to_playlist(playlist_id):
    """添加歌曲到播放列表"""
    data = request.get_json()
    
    # 检查请求数据是否有效
    if not data or 'song_id' not in data:
        return jsonify({'error': '缺少必要的参数: song_id'}), 400
    
    # 检查歌曲是否存在
    song = Song.query.get(data['song_id'])
    if not song:
        return jsonify({'error': '歌曲不存在'}), 400
    
    # 检查播放列表是否存在
    playlist = Playlist.query.get(playlist_id)
    if not playlist:
        return jsonify({'error': '播放列表不存在'}), 404
    
    # 检查歌曲是否已在播放列表中
    existing = PlaylistSong.query.filter_by(
        playlist_id=playlist_id, 
        song_id=data['song_id']
    ).first()
    
    if existing:
        return jsonify({'error': '该歌曲已在播放列表中'}), 400
    
    # 获取当前播放列表中的最大顺序值
    max_order = db.session.query(db.func.max(PlaylistSong.order)).filter_by(playlist_id=playlist_id).scalar() or 0
    
    playlist_song = PlaylistSong(
        playlist_id=playlist_id,
        song_id=data['song_id'],
        order=max_order + 1
    )
    
    db.session.add(playlist_song)
    db.session.commit()
    
    return jsonify(playlist_song.to_dict()), 201

@api.route('/playlists/<int:playlist_id>/songs/<int:song_id>', methods=['DELETE'])
def remove_song_from_playlist(playlist_id, song_id):
    """从播放列表中移除歌曲"""
    playlist_song = PlaylistSong.query.filter_by(playlist_id=playlist_id, song_id=song_id).first()
    if not playlist_song:
        return jsonify({'error': '歌曲不在播放列表中'}), 404
    
    db.session.delete(playlist_song)
    db.session.commit()
    return jsonify({'message': '歌曲已从播放列表中移除'})

@api.route('/popular-singers', methods=['GET'])
def get_popular_singers():
    """获取被收藏歌曲最多的前五名歌手"""
    # 使用SQL查询统计每个歌手的歌曲被收藏次数
    from sqlalchemy import func
    
    popular_singers = db.session.query(
        Singer.id,
        Singer.name,
        Singer.avatar,
        Singer.nationality,
        func.count(Favorite.id).label('favorite_count')
    ).join(Song, Singer.id == Song.singer_id)\
     .join(Favorite, Song.id == Favorite.song_id)\
     .group_by(Singer.id)\
     .order_by(func.count(Favorite.id).desc())\
     .limit(5)\
     .all()
    
    result = []
    for singer in popular_singers:
        result.append({
            'id': singer.id,
            'name': singer.name,
            'avatar': singer.avatar,
            'nationality': singer.nationality,
            'favorite_count': singer.favorite_count
        })
    
    return jsonify(result)

# ========== 音乐流派相关API ==========
@api.route('/genres', methods=['GET'])
def get_genres():
    """获取所有音乐流派"""
    genres = Genre.query.all()
    return jsonify([genre.to_dict() for genre in genres])

@api.route('/genres', methods=['POST'])
def create_genre():
    """创建新音乐流派"""
    data = request.get_json()
    
    # 检查流派名称是否已存在
    if Genre.query.filter_by(name=data['name']).first():
        return jsonify({'error': '该流派已存在'}), 400
    
    genre = Genre(
        name=data['name'],
        description=data.get('description', '')
    )
    
    db.session.add(genre)
    db.session.commit()
    
    return jsonify(genre.to_dict()), 201

@api.route('/genres/<int:genre_id>', methods=['GET'])
def get_genre(genre_id):
    """获取特定音乐流派"""
    genre = Genre.query.get_or_404(genre_id)
    return jsonify(genre.to_dict())

@api.route('/genres/<int:genre_id>', methods=['PUT'])
def update_genre(genre_id):
    """更新音乐流派信息"""
    genre = Genre.query.get_or_404(genre_id)
    data = request.get_json()
    
    genre.name = data.get('name', genre.name)
    genre.description = data.get('description', genre.description)
    
    db.session.commit()
    return jsonify(genre.to_dict())

@api.route('/genres/<int:genre_id>', methods=['DELETE'])
def delete_genre(genre_id):
    """删除音乐流派"""
    genre = Genre.query.get_or_404(genre_id)
    db.session.delete(genre)
    db.session.commit()
    return jsonify({'message': '流派删除成功'})

@api.route('/songs/<int:song_id>/genres', methods=['POST'])
def add_song_genre(song_id):
    """为歌曲添加流派"""
    data = request.get_json()
    genre_id = data.get('genre_id')
    
    # 检查歌曲和流派是否存在
    song = Song.query.get_or_404(song_id)
    genre = Genre.query.get_or_404(genre_id)
    
    # 检查是否已存在关联
    existing = SongGenre.query.filter_by(song_id=song_id, genre_id=genre_id).first()
    if existing:
        return jsonify({'error': '该歌曲已关联此流派'}), 400
    
    song_genre = SongGenre(song_id=song_id, genre_id=genre_id)
    db.session.add(song_genre)
    db.session.commit()
    
    return jsonify(song_genre.to_dict()), 201

@api.route('/songs/<int:song_id>/genres', methods=['GET'])
def get_song_genres(song_id):
    """获取歌曲的所有流派"""
    song_genres = SongGenre.query.filter_by(song_id=song_id).all()
    return jsonify([sg.to_dict() for sg in song_genres])

# ========== 推荐相关API ==========
@api.route('/recommendations', methods=['GET'])
def get_recommendations():
    """获取个人推荐歌曲列表 - 基于用户收藏的歌曲流派和喜欢的歌手"""
    # 获取当前用户ID
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({'error': '需要提供用户ID'}), 400
    
    # 获取用户收藏的歌曲
    user_favorites = Favorite.query.filter_by(user_id=user_id).all()
    
    if not user_favorites:
        # 如果用户没有收藏，返回最新歌曲作为推荐
        popular_songs = Song.query.order_by(Song.created_at.desc()).limit(10).all()
        return jsonify([song.to_dict() for song in popular_songs])
    
    # 基于用户收藏的歌曲流派和喜欢的歌手推荐歌曲
    recommended_songs = []
    
    # 1. 统计用户收藏歌曲的流派分布
    from sqlalchemy import func
    
    # 获取用户收藏歌曲的流派统计
    genre_stats = db.session.query(
        Genre.id,
        Genre.name,
        func.count(SongGenre.id).label('genre_count')
    ).join(SongGenre, Genre.id == SongGenre.genre_id)\
     .join(Song, SongGenre.song_id == Song.id)\
     .join(Favorite, Song.id == Favorite.song_id)\
     .filter(Favorite.user_id == user_id)\
     .group_by(Genre.id)\
     .order_by(func.count(SongGenre.id).desc())\
     .all()
    
    # 2. 获取用户收藏歌曲最多的歌手
    favorite_singers = db.session.query(
        Singer.id,
        Singer.name,
        func.count(Favorite.id).label('favorite_count')
    ).join(Song, Singer.id == Song.singer_id)\
     .join(Favorite, Song.id == Favorite.song_id)\
     .filter(Favorite.user_id == user_id)\
     .group_by(Singer.id)\
     .order_by(func.count(Favorite.id).desc())\
     .limit(3)\
     .all()
    
    # 3. 优先推荐：用户收藏最多的流派的歌曲
    if genre_stats:
        top_genre_id = genre_stats[0].id
        # 获取该流派的所有歌曲
        genre_songs = db.session.query(Song).join(SongGenre, Song.id == SongGenre.song_id)\
            .filter(SongGenre.genre_id == top_genre_id)\
            .filter(Song.id.notin_([fav.song_id for fav in user_favorites]))\
            .limit(5).all()
        
        for song in genre_songs:
            if song not in recommended_songs:
                recommended_songs.append(song)
    
    # 4. 推荐用户喜欢的歌手的歌曲
    if favorite_singers:
        for singer in favorite_singers:
            singer_songs = Song.query.filter_by(singer_id=singer.id)\
                .filter(Song.id.notin_([fav.song_id for fav in user_favorites]))\
                .limit(3).all()
            
            for song in singer_songs:
                if song not in recommended_songs:
                    recommended_songs.append(song)
    
    # 5. 如果推荐歌曲不足，补充其他流派的歌曲（基于用户收藏的流派）
    if len(recommended_songs) < 10 and len(genre_stats) > 1:
        for i in range(1, min(3, len(genre_stats))):  # 取前3个流派（除了第一个）
            genre_id = genre_stats[i].id
            genre_songs = db.session.query(Song).join(SongGenre, Song.id == SongGenre.song_id)\
                .filter(SongGenre.genre_id == genre_id)\
                .filter(Song.id.notin_([fav.song_id for fav in user_favorites]))\
                .limit(2).all()
            
            for song in genre_songs:
                if len(recommended_songs) < 10 and song not in recommended_songs:
                    recommended_songs.append(song)
    
    # 6. 如果推荐歌曲仍然不足，补充最新歌曲
    if len(recommended_songs) < 10:
        remaining_count = 10 - len(recommended_songs)
        popular_songs = Song.query.order_by(Song.created_at.desc())\
            .filter(Song.id.notin_([fav.song_id for fav in user_favorites]))\
            .limit(remaining_count).all()
        
        for song in popular_songs:
            if song not in recommended_songs:
                recommended_songs.append(song)
    
    # 限制返回数量为10首
    recommended_songs = recommended_songs[:10]
    
    return jsonify([song.to_dict() for song in recommended_songs])

@api.route('/recommendations/popular', methods=['GET'])
def get_popular_recommendations():
    """获取热门推荐歌曲（不基于用户历史）"""
    popular_songs = Song.query.order_by(Song.created_at.desc()).limit(10).all()
    return jsonify([song.to_dict() for song in popular_songs])