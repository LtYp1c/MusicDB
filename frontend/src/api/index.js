import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 用户相关API
export const userApi = {
  getUsers: () => api.get('/users'),
  getUser: (id) => api.get(`/users/${id}`),
  createUser: (data) => api.post('/users', data),
  updateUser: (id, data) => api.put(`/users/${id}`, data),
  deleteUser: (id) => api.delete(`/users/${id}`)
}

// 歌手相关API
export const singerApi = {
  getSingers: () => api.get('/singers'),
  getSinger: (id) => api.get(`/singers/${id}`),
  createSinger: (data) => api.post('/singers', data),
  updateSinger: (id, data) => api.put(`/singers/${id}`, data),
  deleteSinger: (id) => api.delete(`/singers/${id}`)
}

// 专辑相关API
export const albumApi = {
  getAlbums: () => api.get('/albums'),
  getAlbum: (id) => api.get(`/albums/${id}`),
  createAlbum: (data) => api.post('/albums', data),
  updateAlbum: (id, data) => api.put(`/albums/${id}`, data),
  deleteAlbum: (id) => api.delete(`/albums/${id}`)
}

// 歌曲相关API
export const songApi = {
  getSongs: () => api.get('/songs'),
  getSong: (id) => api.get(`/songs/${id}`),
  createSong: (data) => api.post('/songs', data),
  updateSong: (id, data) => api.put(`/songs/${id}`, data),
  deleteSong: (id) => api.delete(`/songs/${id}`)
}

// 收藏相关API
export const favoriteApi = {
  getAllFavorites: () => api.get('/favorites'),
  getUserFavorites: (userId) => api.get(`/users/${userId}/favorites`),
  createFavorite: (data) => api.post('/favorites', data),
  deleteFavorite: (id) => api.delete(`/favorites/${id}`),
  deleteFavoriteByUserSong: (userId, songId) => api.delete(`/favorites/user/${userId}/song/${songId}`)
}

// 统计相关API
export const statsApi = {
  getPopularSingers: () => api.get('/popular-singers'),
  getStatsOverview: () => api.get('/stats/overview'),
  getTopSingers: () => api.get('/stats/top-singers'),
  getTopSongs: () => api.get('/stats/top-songs'),
  getGenreDistribution: () => api.get('/stats/genre-distribution'),
  getUserActivity: () => api.get('/stats/user-activity'),
  getSingerNationality: () => api.get('/stats/singer-nationality')
}

// 推荐相关API
export const recommendationApi = {
  getRecommendations: (userId) => api.get(`/recommendations?user_id=${userId}`),
  getPopularRecommendations: () => api.get('/recommendations/popular')
}

// 播放列表相关API
export const playlistApi = {
  getPlaylists: () => api.get('/playlists'),
  getPlaylist: (id) => api.get(`/playlists/${id}`),
  createPlaylist: (data) => api.post('/playlists', data),
  updatePlaylist: (id, data) => api.put(`/playlists/${id}`, data),
  deletePlaylist: (id) => api.delete(`/playlists/${id}`),
  addSongToPlaylist: (playlistId, songId) => api.post(`/playlists/${playlistId}/songs`, { song_id: songId }),
  getPlaylistSongs: (playlistId) => api.get(`/playlists/${playlistId}/songs`),
  removeSongFromPlaylist: (playlistId, songId) => api.delete(`/playlists/${playlistId}/songs/${songId}`)
}

// 流派相关API
export const genreApi = {
  getGenres: () => api.get('/genres'),
  getGenre: (id) => api.get(`/genres/${id}`),
  createGenre: (data) => api.post('/genres', data),
  updateGenre: (id, data) => api.put(`/genres/${id}`, data),
  deleteGenre: (id) => api.delete(`/genres/${id}`),
  getSongGenres: (songId) => api.get(`/songs/${songId}/genres`),
  addSongGenre: (songId, data) => api.post(`/songs/${songId}/genres`, data)
}

export default api

// 认证相关API
export const authApi = {
  login: (data) => api.post('/login', data)
}