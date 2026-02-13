"""
数据库初始化脚本
"""

import hashlib
import random
from datetime import datetime, timedelta

from app import app, db
from models import User, Singer, Album, Song, Favorite, Genre, SongGenre, Playlist, PlaylistSong
from sqlalchemy import text

def init_database():
    """初始化数据库"""
    with app.app_context():
        print("开始初始化数据库...")
        
        # 先禁用外键检查
        print("禁用外键检查...")
        db.session.execute(text('SET FOREIGN_KEY_CHECKS = 0'))
        
        # 手动删除所有表，按依赖顺序
        print("手动删除所有表...")
        tables = [
            'comment_likes', 'comments', 'user_behaviors', 'playlist_songs', 
            'playlists', 'song_genres', 'favorites', 'song_statistics', 
            'songs', 'albums', 'singers', 'genres', 'users'
        ]
        
        for table in tables:
            try:
                db.session.execute(text(f'DROP TABLE IF EXISTS {table}'))
                print(f"成功删除表: {table}")
            except Exception as e:
                print(f"删除表 {table} 失败: {e}")
        
        # 创建所有表
        print("创建所有表...")
        db.create_all()
        
        # 重新启用外键检查
        print("启用外键检查...")
        db.session.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
        
        # 创建默认数据
        create_sample_data()
        print("成功创建示例数据")
        
        print("\n数据库初始化完成！")

def create_sample_data():
    """创建丰富的示例数据"""
    print("开始创建示例数据...")
    
    # 创建10名用户（包含1名管理员）
    print("创建用户数据...")
    users = []
    
    # 管理员用户
    admin_user = User(
        username='admin',
        email='admin@music.com',
        password=hashlib.md5('123456'.encode()).hexdigest(),
        avatar='/avatars/admin.jpg',
        role='admin'
    )
    users.append(admin_user)
    db.session.add(admin_user)
    
    # 普通用户
    for i in range(2, 11):
        user = User(
            username=f'user{i}',
            email=f'user{i}@music.com',
            password=hashlib.md5('123456'.encode()).hexdigest(),
            avatar=f'/avatars/user{i}.jpg'
        )
        users.append(user)
        db.session.add(user)
    
    db.session.commit()
    print(f"成功创建了 {len(users)} 个用户")
    
    # 创建50名歌手
    print("创建歌手数据...")
    singer_names = [
        # 华语歌手 (20名)
        '周杰伦', '林俊杰', '邓紫棋', '王力宏', '蔡依林',
        '陈奕迅', '孙燕姿', '张惠妹', '李荣浩', '薛之谦',
        '张杰', '华晨宇', '杨丞琳', 'S.H.E', '五月天',
        'Beyond', '张学友', '刘德华', '王菲', '那英',
        # 欧美歌手 (20名)
        'Taylor Swift', 'Ed Sheeran', 'Adele', 'Bruno Mars', 'Beyoncé',
        'Rihanna', 'Justin Bieber', 'Lady Gaga', 'Katy Perry', 'Drake',
        'Eminem', 'Coldplay', 'Maroon 5', 'Imagine Dragons', 'Billie Eilish',
        'The Weeknd', 'Dua Lipa', 'Ariana Grande', 'Post Malone', 'Harry Styles',
        # 日韩歌手 (10名)
        'BTS', 'BLACKPINK', 'TWICE', 'EXO', 'IU',
        'AKB48', 'YOASOBI', 'Official髭男dism', 'ONE OK ROCK', 'Radwimps'
    ]
    
    singers = []
    for i, name in enumerate(singer_names, 1):
        singer = Singer(
            name=name,
            description=f'{name}的详细介绍',
            avatar=f'/singers/{name}.jpg',
            nationality='中国' if i <= 20 else ('美国' if i <= 40 else ('韩国' if i <= 45 else '日本')),
            birth_date=datetime(1980 + random.randint(0, 20), random.randint(1, 12), random.randint(1, 28))
        )
        singers.append(singer)
        db.session.add(singer)
    
    db.session.commit()
    print(f"成功创建了 {len(singers)} 个歌手")
    
    # 创建100张专辑（每名歌手2张专辑）
    print("创建专辑数据...")
    albums = []
    
    for singer in singers:
        # 每名歌手创建2张专辑
        for j in range(1, 3):
            year = 2000 + random.randint(0, 20)
            album = Album(
                name=f'{singer.name} - 专辑{j}',
                singer_id=singer.id,
                release_date=datetime(year, random.randint(1, 12), random.randint(1, 28)),
                cover=f'/albums/{singer.name}_album{j}.jpg',
                description=f'{singer.name}的第{j}张专辑'
            )
            albums.append(album)
            db.session.add(album)
    
    db.session.commit()
    print(f"成功创建了 {len(albums)} 张专辑")
    
    # 创建500首歌曲（每张专辑5首歌曲）
    print("创建歌曲数据...")
    songs = []
    song_names = [
        '梦想启航', '星空之下', '时光倒流', '青春纪念', '爱的告白',
        '雨中漫步', '夏日回忆', '冬日恋歌', '春天来了', '秋天的思念',
        '城市之光', '乡村小路', '大海之歌', '山间清风', '月光曲',
        '阳光灿烂', '彩虹桥', '流星雨', '云朵之上', '风之谷',
        '夜空中最亮的星', '小幸运', '平凡之路', '岁月神偷', '后来',
        '童话', '勇气', '红豆', '吻别', '朋友',
        '海阔天空', '光辉岁月', '真的爱你', '喜欢你', '冷雨夜',
        'Shape of You', 'Perfect', 'Thinking Out Loud', 'Photograph', 'Castle on the Hill',
        'Love Story', 'Blank Space', 'Shake It Off', 'Bad Blood', 'Wildest Dreams',
        'Rolling in the Deep', 'Someone Like You', 'Hello', 'Set Fire to the Rain', 'Skyfall',
        'Uptown Funk', 'Just the Way You Are', 'Grenade', 'Locked Out of Heaven', '24K Magic',
        'Dynamite', 'Butter', 'Permission to Dance', 'Life Goes On', 'Boy With Luv',
        'Kill This Love', 'How You Like That', 'Pink Venom', 'DDU-DU DDU-DU', 'Whistle',
        'Fancy', 'Feel Special', 'More & More', 'I Can\'t Stop Me', 'Scientist',
        'Growl', 'Call Me Baby', 'Love Shot', 'Tempo', 'Obsession',
        'Blueming', 'Palette', 'BBIBBI', 'Eight', 'Celebrity',
        'Heavy Rotation', 'Koisuru Fortune Cookie', 'UZA', 'Kimi wa Melody', 'Teacher Teacher',
        '夜に駆ける', '群青', '三原色', '怪物', '優しい彗星',
        'Pretender', 'I Love...', 'Subtitle', 'Cry Baby', 'Mixed Nuts'
    ]
    
    for album in albums:
        # 每张专辑创建5首歌曲
        for j in range(1, 6):
            song_name = random.choice(song_names)
            song = Song(
                name=f'{song_name} - {album.name.split(" - ")[1]}',
                singer_id=album.singer_id,
                album_id=album.id,
                duration=random.randint(180, 360),  # 3-6分钟
                release_date=album.release_date + timedelta(days=random.randint(0, 30)),
                lyrics=f'{song_name}的歌词内容...\n\n这是{song_name}的完整歌词。'
            )
            songs.append(song)
            db.session.add(song)
    
    db.session.commit()
    print(f"成功创建了 {len(songs)} 首歌曲")
    
    # 创建音乐流派
    print("创建流派数据...")
    genres_data = [
        ('流行', '流行音乐'),
        ('摇滚', '摇滚音乐'),
        ('民谣', '民谣音乐'),
        ('电子', '电子音乐'),
        ('R&B', '节奏布鲁斯'),
        ('嘻哈', '嘻哈音乐'),
        ('古典', '古典音乐'),
        ('爵士', '爵士音乐'),
        ('乡村', '乡村音乐'),
        ('金属', '重金属音乐'),
        ('朋克', '朋克摇滚'),
        ('蓝调', '蓝调音乐'),
        ('雷鬼', '雷鬼音乐'),
        ('新世纪', '新世纪音乐'),
        ('世界音乐', '世界各民族音乐')
    ]
    
    genres = []
    for name, description in genres_data:
        genre = Genre(name=name, description=description)
        genres.append(genre)
        db.session.add(genre)
    
    db.session.commit()
    print(f"成功创建了 {len(genres)} 个音乐流派")
    
    # 创建歌曲-流派关联（每首歌曲1-3个流派）
    print("创建歌曲-流派关联...")
    song_genres = []
    for song in songs:
        num_genres = random.randint(1, 3)
        selected_genres = random.sample(genres, num_genres)
        for genre in selected_genres:
            sg = SongGenre(song_id=song.id, genre_id=genre.id)
            song_genres.append(sg)
            db.session.add(sg)
    
    db.session.commit()
    print(f"成功创建了 {len(song_genres)} 个歌曲-流派关联")
    
    # 创建收藏记录（每个用户收藏50-200首歌曲）
    print("创建收藏记录...")
    favorites = []
    for user in users:
        num_favorites = random.randint(50, 200)
        selected_songs = random.sample(songs, min(num_favorites, len(songs)))
        for song in selected_songs:
            favorite = Favorite(
                user_id=user.id,
                song_id=song.id
            )
            favorites.append(favorite)
            db.session.add(favorite)
    
    db.session.commit()
    print(f"成功创建了 {len(favorites)} 个收藏记录")
    
    # 创建播放列表（每个用户2-5个播放列表）
    print("创建播放列表...")
    playlists = []
    playlist_names = ['我的最爱', '工作音乐', '放松时光', '运动歌单', '旅行音乐', '学习专注', '派对狂欢', '深夜emo']
    
    for user in users:
        num_playlists = random.randint(2, 5)
        for j in range(num_playlists):
            playlist = Playlist(
                name=f'{random.choice(playlist_names)} {j+1}',
                user_id=user.id,
                description=f'{user.username}的个性化歌单',
                cover=f'/playlists/playlist{len(playlists)+1}.jpg',
                is_public=random.choice([True, False])
            )
            playlists.append(playlist)
            db.session.add(playlist)
    
    db.session.commit()
    print(f"成功创建了 {len(playlists)} 个播放列表")
    
    # 创建播放列表-歌曲关联（每个播放列表10-30首歌曲）
    print("创建播放列表-歌曲关联...")
    playlist_songs = []
    for playlist in playlists:
        num_songs = random.randint(10, 30)
        selected_songs = random.sample(songs, min(num_songs, len(songs)))
        for order, song in enumerate(selected_songs, 1):
            ps = PlaylistSong(playlist_id=playlist.id, song_id=song.id, order=order)
            playlist_songs.append(ps)
            db.session.add(ps)
    
    db.session.commit()
    print(f"成功创建了 {len(playlist_songs)} 个播放列表-歌曲关联")
    
    # 统计信息
    print("\n=== 数据统计 ===")
    print(f"用户数量: {len(users)}")
    print(f"歌手数量: {len(singers)}")
    print(f"专辑数量: {len(albums)}")
    print(f"歌曲数量: {len(songs)}")
    print(f"流派数量: {len(genres)}")
    print(f"歌曲-流派关联: {len(song_genres)}")
    print(f"收藏记录: {len(favorites)}")
    print(f"播放列表: {len(playlists)}")
    print(f"播放列表歌曲: {len(playlist_songs)}")
    print("================")
    
    print("\n示例数据创建完成！")

if __name__ == "__main__":
    init_database()